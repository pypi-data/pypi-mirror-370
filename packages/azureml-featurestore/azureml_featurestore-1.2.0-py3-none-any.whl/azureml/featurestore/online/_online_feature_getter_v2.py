# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-locals

import base64
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from typing import Dict, List, Optional, Set, Tuple

import msgpack
import pyarrow
from azureml.featurestore._utils._constants import (
    AZUREML_FEATURESTORE_DEBUG_ENVVAR,
    FEATURE_STORE_ONLINE_INFERENCE,
    NETWORK_LATENCY_COLUMN_NAME,
    ON_THE_FLY_ENTITY_KEY,
)
from azureml.featurestore._utils._preview_method import _is_private_preview_enabled
from azureml.featurestore._utils.arm_id_utils import FeatureSetVersionedArmId
from azureml.featurestore.contracts.column import ColumnType
from azureml.featurestore.contracts.store_connection import OnlineStoreType

from ._on_the_fly_feature_getter import OnTheFlyFeatureGetter
from ._redis_client_pool import _get_redis_client
from ._utils import _get_lookup_key_pattern

FEATURE_STORE_KEY_TEMPLATE = "/subscriptions/{}/resourcegroups/{}/workspaces/{}"
FEATURE_SET_KEY_TEMPLATE = "/subscriptions/{}/resourcegroups/{}/workspaces/{}/feature_sets/{}/version/{}"


def _msgpack_unpacker(s):
    # Serialization @ _online_feature_materialization.py:126 looks like this:
    #     packed_byte = msgpack.packb(current_record_value)  # cspell:disable-line
    #     encoded_str = base64.b64encode(packed_byte).decode('utf-8')

    # base64 decode the string to get the original bytestring that msgpack packed, then unpack that bytestring.
    return msgpack.unpackb(base64.b64decode(s), raw=False)  # cspell:disable-line


_type_converters = {
    ColumnType.STRING: lambda s: s.decode("utf-8"),
    ColumnType.INTEGER: lambda s: int(s),  # pylint: disable=unnecessary-lambda
    ColumnType.LONG: lambda s: int(s),  # pylint: disable=unnecessary-lambda
    ColumnType.FLOAT: _msgpack_unpacker,
    ColumnType.DOUBLE: _msgpack_unpacker,
    ColumnType.BOOLEAN: lambda s: s == b"True",
    ColumnType.BINARY: _msgpack_unpacker,
    ColumnType.DATETIME: lambda s: s.decode(
        "utf-8"
    ),  # TODO: parse with customized format from customer featureset spec
}


def _parse_feature_uris(feature_uris, feature_set_uris_to_recompute, credential):
    from azureml.featurestore import FeatureStoreClient

    client_cache = dict()
    feature_set_cache = dict()
    features = []
    feature_sets = []

    for feature_uri in feature_uris:
        parsed_uri = urllib.parse.urlsplit(feature_uri)
        parsed_qs = dict(urllib.parse.parse_qsl(parsed_uri.query))

        feature_id = feature_uri.lstrip("azureml://")

        parts = feature_id.split("/")
        subscription_id = parts[1]
        resource_group = parts[3]
        provider = parts[5]  # pylint: disable=unused-variable
        workspace = parts[7]
        feature_set_name = parts[9]
        feature_set_version = parts[11]
        feature_name = parts[13].split("?")[0]

        feature_store_key = FEATURE_STORE_KEY_TEMPLATE.format(subscription_id, resource_group, workspace)
        if feature_store_key not in client_cache:
            client_cache[feature_store_key] = FeatureStoreClient(
                credential=credential,
                subscription_id=subscription_id,
                resource_group_name=resource_group,
                name=workspace,
            )

        fs_client = client_cache[feature_store_key]

        feature_set_key = FEATURE_SET_KEY_TEMPLATE.format(
            subscription_id, resource_group, workspace, feature_set_name, feature_set_version
        )
        if feature_set_key not in feature_set_cache:
            feature_set_cache[feature_set_key] = fs_client.feature_sets.get(
                feature_set_name, feature_set_version, headers={FEATURE_STORE_ONLINE_INFERENCE: "true"}
            )

        feature_set = feature_set_cache[feature_set_key]

        feature = feature_set.get_feature(feature_name)
        feature.output_name = parsed_qs.get("output_name", feature.output_name)
        feature.type = parsed_qs.get("type", feature.type)

        features.append(feature)

    for feature_set_uri in feature_set_uris_to_recompute:
        fs_arm_id = FeatureSetVersionedArmId(feature_set_uri)
        feature_set_key = FEATURE_SET_KEY_TEMPLATE.format(
            fs_arm_id.subscription_id,
            fs_arm_id.resource_group_name,
            fs_arm_id.workspace_name,
            fs_arm_id.featureset_name,
            fs_arm_id.featureset_version,
        )
        feature_sets.append(feature_set_cache[feature_set_key])

    return features, feature_sets


def _init_redis_clients(features, credential):
    redis_clients = dict()

    for feature in features:
        if not feature.feature_set_reference.online_store.target:
            raise Exception(
                f"Feature '{feature.uri}' belongs to a feature store that does not specify an online store connection."
            )

        if feature.feature_set_reference.online_store.type != OnlineStoreType.REDIS:
            raise Exception(
                f"Feature '{feature.uri}' belongs to a feature store that specifies an online store connection of type"
                f" '{feature.feature_set_reference.online_store.type}'. Only Redis stores are currently supported."
            )

        if feature.feature_set_reference.online_store.target not in redis_clients:
            redis_clients[feature.feature_set_reference.online_store.target] = _get_redis_client(
                feature.feature_set_reference.online_store.target, credential
            )

    return redis_clients


def _init_hashkey_formats(features):
    hashkey_formats_map = dict()

    for feature in features:
        feature_set_uri = feature.uri.split(f"/features/{feature.name}")[0]
        if feature_set_uri in hashkey_formats_map:
            continue

        hash_key_format, _ = _get_lookup_key_pattern(
            feature.feature_set_reference, feature.feature_set_reference.online_materialization_version
        )
        hash_key_format = hash_key_format.rstrip(":")

        for entity in feature.feature_set_reference.entities:
            for index_column in entity.index_columns:
                hash_key_format += f":{index_column.name}:{{{index_column.name}}}"

        hashkey_formats_map[feature_set_uri] = hash_key_format

    return hashkey_formats_map


def _init_features_map(features):
    features_map = dict()

    for feature in features:
        redis_arm_id = feature.feature_set_reference.online_store.target
        feature_set_uri = feature.uri.split(f"/features/{feature.name}")[0]
        feature_name = feature.name

        features_map[feature.uri.split("?")[0]] = (
            redis_arm_id,
            feature_set_uri,
            feature_name,
            feature.type,
            feature.output_name,
        )

    return features_map


class OnlineFeatureGetterV2(object):
    def __init__(self, credential, initial_feature_uris=None, feature_sets_to_recompute: Optional[List[str]] = None):
        print("Constructing feature objects...", flush=True)
        features, feature_sets = _parse_feature_uris(initial_feature_uris, feature_sets_to_recompute, credential)
        print("Done constructing feature objects.", flush=True)
        # maps redis resource ARM IDs to redis clients
        print("Constructing redis clients...", flush=True)
        self.redis_clients = _init_redis_clients(features, credential)
        print("Done constructing redis clients.", flush=True)

        # maps feature_set_uris to a format string that can be used with str.format and the observation row dict to
        # produce the redis hashkey for this featureset and any observation row.
        print("Constructing lookup key formatters...", flush=True)
        self.hashkey_formats = _init_hashkey_formats(features)
        print("Done constructing lookup key formatters.", flush=True)

        # maps feature URIs (without query params) to a tuple of (redis_resource_arm_id, feature_set_uri, feature_name,
        # feature_data_type, feature_output_name)
        print("Indexing features...", flush=True)
        self.features_map = _init_features_map(features)
        print("Done indexing features.", flush=True)

        print("Constructing an executor...", flush=True)
        self.executor = ThreadPoolExecutor()
        print("Done constructing an executor.", flush=True)

        self.featuresets_to_recompute = feature_sets
        if self.featuresets_to_recompute:
            self.on_the_fly_feature_getter = OnTheFlyFeatureGetter(credential, features, self.featuresets_to_recompute)

        self.report_network_latency = False
        if AZUREML_FEATURESTORE_DEBUG_ENVVAR in os.environ:
            self.report_network_latency = os.getenv(AZUREML_FEATURESTORE_DEBUG_ENVVAR).lower() == "true"

    def get_online_features(self, feature_uris: "List[str]", observation_df: "pyarrow.Table", **kwargs):
        if _is_private_preview_enabled():
            # TODO: Need to filter out the features in redis
            on_the_fly_entities = kwargs.pop(ON_THE_FLY_ENTITY_KEY, None)
            if self.featuresets_to_recompute:
                recomputed_feature_dataframe = self.on_the_fly_feature_getter.get_on_the_fly_features(
                    feature_uris, observation_df, on_the_fly_entities=on_the_fly_entities, **kwargs
                )

                return recomputed_feature_dataframe
                # feature_dataframe = feature_dataframe.join(
                #     recomputed_feature_dataframe, observation_df.column_names, right_suffix="_r"
                # )

        # these are the features that we need to fetch from an online store (currently only redis)
        features_to_fetch = feature_uris
        feature_dataframe = self._fetch_feature_data(features_to_fetch, observation_df)

        return feature_dataframe

    def _fetch_feature_data(self, feature_uris: "List[str]", observation_df: "pyarrow.Table"):
        grouped_features = self._group_features_by_redis_resource_and_featureset(
            feature_uris, set(observation_df.column_names)
        )
        # cspell:ignore hmget
        # spin off one task per redis resource. In each thread, do the following:
        #     start a pipe session, and for each featureset, do the following:
        #         Fetch the keys builder for the featureset, and use it to build the redis hash keys.
        #         There should be one for each row in `observation_df`.
        #         For each key, fire off an HMGET, appending all the feature names.

        observation_df_pylist = observation_df.to_pylist()

        def fetch_feature_data_from_redis_resource(redis_resource_id: "str"):
            pipe = self.redis_clients[redis_resource_id].pipeline()
            feature_group = grouped_features[redis_resource_id]

            retrieved_feature_data = dict()

            # for each observation dataframe row, do:
            for observation_dict in observation_df_pylist:
                # for each featureset we're retrieving data from, do:
                for feature_set_uri, feature_tuples in feature_group.items():
                    # get the hashkey format string for this featureset
                    feature_set_hashkey_format = self.hashkey_formats[feature_set_uri]

                    # collect feature names, and add columns for the feature data
                    feature_names = []
                    for feature_name, feature_data_type, feature_output_name in feature_tuples:
                        retrieved_feature_data[feature_output_name] = []
                        feature_names.append(feature_name)

                    # issue an HMGET for all the features we need, for this featureset, for this row of observations
                    pipe.hmget(feature_set_hashkey_format.format(**observation_dict), feature_names)

            # execute the pipe, and wait for responses
            network_start = perf_counter()
            responses = pipe.execute()
            network_latency = perf_counter() - network_start

            # process redis responses
            for observation_dict in observation_df_pylist:
                for feature_set_uri, feature_tuples in feature_group.items():
                    hmget_response = responses.pop(0)
                    for (feature_name, feature_data_type, feature_output_name), feature_value in zip(
                        feature_tuples, hmget_response
                    ):
                        retrieved_feature_data[feature_output_name].append(
                            _type_converters[feature_data_type](feature_value) if feature_value is not None else None
                        )

            if self.report_network_latency:
                n_rows = len(observation_df_pylist)
                retrieved_feature_data[NETWORK_LATENCY_COLUMN_NAME] = [network_latency] * n_rows

            return retrieved_feature_data

        # For 2 or fewer databases, the overhead from using ThreadPoolExecutor.map() is greater than the speedup
        # obtained from querying in parallel.
        # For 1 or 2 databases, just query data inline in this thread.
        # For 3 or more databases, fan out to individual threads.
        if len(grouped_features) < 3:
            feature_dicts = map(fetch_feature_data_from_redis_resource, grouped_features)
        else:
            feature_dicts = self.executor.map(fetch_feature_data_from_redis_resource, grouped_features)

        combined_feature_dict = observation_df.to_pydict()
        for feature_dict in feature_dicts:
            combined_feature_dict = {**combined_feature_dict, **feature_dict}

        # collect results into a feature dataframe
        combined_feature_df = pyarrow.Table.from_pydict(combined_feature_dict)

        # return
        return combined_feature_df

    def _group_features_by_redis_resource_and_featureset(
        self, feature_uris: List[str], column_names: Set[str]
    ) -> Dict[str, Dict[str, List[Tuple[str, str, str]]]]:
        # this is a dict[str, dict[str, list[(string)]]]
        # the top-level dictionary keys are redis resource IDs. All the features under a single key in the top-level
        # dict can be found in that redis resource. The nested dictionary keys are feature set uris. All the features
        # under a single key in the nested dict can be found under a single hash key in redis.
        # The values in the nested dictionary are a list of tuples, with this structure:
        # (feature_name, data_type, output_name)
        redis_resources_to_features = dict()

        for feature_uri in feature_uris:
            if "?" in feature_uri:
                feature_uri, feature_uri_params = feature_uri.split("?")
                # Yes, I know urllib.parse.parse_qs will do this for me. But I profiled parse_qs, and this
                # implementation is 3.5x faster than urllib.parse.parse_qs
                param_sections = feature_uri_params.split("&")
                param_tuples = [section.split("=") for section in param_sections]
                parsed_params = dict(param_tuples)
                feature_data_type = ColumnType[parsed_params["type"]] if "type" in parsed_params else None
                feature_output_name = parsed_params.get("output_name")
            else:
                feature_data_type = None
                feature_output_name = None

            redis_resource, feature_set_uri, feature_name, default_data_type, default_output_name = self.features_map[
                feature_uri
            ]

            if redis_resource not in redis_resources_to_features:
                redis_resources_to_features[redis_resource] = dict()

            if feature_set_uri not in redis_resources_to_features[redis_resource]:
                redis_resources_to_features[redis_resource][feature_set_uri] = []

            selected_output_name = feature_output_name or default_output_name or feature_name
            suffix_count = 0
            suffix = ""
            while f"{selected_output_name}{suffix}" in column_names:
                suffix_count += 1
                suffix = f"_{suffix_count}"

            selected_output_name = f"{selected_output_name}{suffix}"

            redis_resources_to_features[redis_resource][feature_set_uri].append(
                (feature_name, feature_data_type or default_data_type, selected_output_name)
            )

        return redis_resources_to_features
