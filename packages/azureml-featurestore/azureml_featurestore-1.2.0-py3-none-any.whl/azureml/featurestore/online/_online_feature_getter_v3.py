# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-locals
# cspell: ignore hmget

import asyncio
import datetime
import struct
import time
from typing import Dict, List, Optional, Set, Tuple
import urllib.parse

from azure.ai.ml.exceptions import ValidationException
from azureml.featurestore import FeatureStoreClient
from azureml.featurestore._utils._constants import ON_THE_FLY_ENTITY_KEY, FEATURE_STORE_ONLINE_INFERENCE
from azureml.featurestore._utils._preview_method import _is_private_preview_enabled
from azureml.featurestore._utils.arm_id_utils import FeatureSetVersionedArmId
from azureml.featurestore.contracts.column import ColumnType
from azureml.featurestore.contracts.store_connection import OnlineStoreType


import pyarrow

from ._on_the_fly_feature_getter import OnTheFlyFeatureGetter
from ._online_feature_getter_v2 import _type_converters
from ._redis_client_pool import _get_redis_connection_string
from ._utils import _get_lookup_key_pattern


FEATURE_STORE_KEY_TEMPLATE = "/subscriptions/{}/resourcegroups/{}/workspaces/{}"
FEATURE_SET_KEY_TEMPLATE = "/subscriptions/{}/resourcegroups/{}/workspaces/{}/feature_sets/{}/version/{}"

_type_serializers = {
    ColumnType.STRING: lambda v: v.encode('utf-8'),
    ColumnType.INTEGER: lambda v: struct.pack('<i', v),
    ColumnType.LONG: lambda v: struct.pack('<l', v),
    ColumnType.FLOAT: lambda v: struct.pack('<f', v),
    ColumnType.DOUBLE: lambda v: struct.pack('<d', v),
    ColumnType.BOOLEAN: lambda v: b'1' if v else b'0',
    ColumnType.BINARY: lambda v: v,
    ColumnType.DATETIME: lambda v: (v.isoformat()).encode('utf-8'),
}

_type_deserializers = {
    ColumnType.STRING: lambda b: b.decode('utf-8'),
    ColumnType.INTEGER: lambda b: struct.unpack('<i', b)[0],
    ColumnType.LONG: lambda b: struct.unpack('<l', b)[0],
    ColumnType.FLOAT: lambda b: struct.unpack('<f', b)[0],
    ColumnType.DOUBLE: lambda b: struct.unpack('<d', b)[0],
    ColumnType.BOOLEAN: lambda b: b == b'1',
    ColumnType.BINARY: lambda b: b,
    ColumnType.DATETIME: lambda b: datetime.datetime.fromisoformat(b.decode('utf-8'))
}


def _parse_feature_uris(feature_uris, feature_set_uris_to_recompute, credential):
    featurestore_client_cache = {}
    featureset_cache = {}
    for feature_uri in feature_uris:
        feature_id = feature_uri.lstrip("azureml://")

        parts = feature_id.split("/")
        subscription_id = parts[1]
        resource_group = parts[3]
        workspace = parts[7]
        feature_set_name = parts[9]
        feature_set_version = parts[11]

        if (subscription_id, resource_group, workspace) not in featurestore_client_cache:
            featurestore_client_cache[(subscription_id, resource_group, workspace)] = FeatureStoreClient(
                credential=credential,
                subscription_id=subscription_id,
                resource_group_name=resource_group,
                name=workspace,
            )

        fs_client = featurestore_client_cache[(subscription_id, resource_group, workspace)]

        if (subscription_id, resource_group, workspace, feature_set_name, feature_set_version) not in featureset_cache:
            featureset_cache[(subscription_id, resource_group, workspace, feature_set_name, feature_set_version)] =\
                fs_client.feature_sets.get(
                feature_set_name,
                feature_set_version,
                headers={FEATURE_STORE_ONLINE_INFERENCE: "true"}
                )

    features = []
    for feature_uri in feature_uris:
        feature_id = feature_uri.lstrip("azureml://")

        parsed_uri = urllib.parse.urlsplit(feature_uri)
        parsed_qs = dict(urllib.parse.parse_qsl(parsed_uri.query))

        parts = feature_id.split("/")
        subscription_id = parts[1]
        resource_group = parts[3]
        workspace = parts[7]
        feature_set_name = parts[9]
        feature_set_version = parts[11]
        feature_name = parts[13].split("?")[0]

        feature_set = featureset_cache[
            (subscription_id, resource_group, workspace, feature_set_name, feature_set_version)
        ]

        feature = feature_set.get_feature(feature_name)
        feature.output_name = parsed_qs.get("output_name", feature.output_name)
        feature.type = parsed_qs.get("type", feature.type)

        features.append(feature)

    recompute_feature_sets = []
    for feature_set_uri in feature_set_uris_to_recompute:
        fs_arm_id = FeatureSetVersionedArmId(feature_set_uri)
        recompute_feature_sets.append(
            featureset_cache[(
                fs_arm_id.subscription_id,
                fs_arm_id.resource_group_name,
                fs_arm_id.workspace_name,
                fs_arm_id.featureset_name,
                fs_arm_id.featureset_version
            )]
        )

    return features, recompute_feature_sets


def _init_redis_clients(features, credential, redis_database_overrides=None):
    redis_clients = {}

    for feature in features:
        if not feature.feature_set_reference.online_store.target:
            raise ValidationException(
                f"Feature '{feature.uri}' belongs to a feature store that does not specify an online store connection.",
                f"Feature '{feature.uri}' belongs to a feature store that does not specify an online store connection.",
            )

        if feature.feature_set_reference.online_store.type != OnlineStoreType.REDIS:
            raise ValidationException(
                f"Feature '{feature.uri}' belongs to a feature store that specifies an online store connection of type"
                f" '{feature.feature_set_reference.online_store.type}'. Only Redis stores are currently supported.",
                f"Feature '{feature.uri}' belongs to a feature store that specifies an online store connection of type"
                f" '{feature.feature_set_reference.online_store.type}'. Only Redis stores are currently supported.",
            )

        if redis_database_overrides is not None and \
                feature.feature_set_reference.feature_store_guid in redis_database_overrides:
            redis_database_arm_id = redis_database_overrides[feature.feature_set_reference.feature_store_guid]
        else:
            redis_database_arm_id = feature.feature_set_reference.online_store.target

        if redis_database_arm_id not in redis_clients:
            connection_string, clustering_enabled = \
                _get_redis_connection_string(redis_database_arm_id, credential)
            if clustering_enabled:
                from redis.asyncio.cluster import RedisCluster
                redis_clients[redis_database_arm_id] = \
                    RedisCluster.from_url(connection_string)
            else:
                from redis.asyncio import Redis
                redis_clients[redis_database_arm_id] = Redis.from_url(connection_string)

    return redis_clients


def _init_hashkey_formats(features):
    hashkey_formats_map = {}

    for feature in features:
        feature_set_uri = feature.uri.split(f"/features/{feature.name}")[0]
        if feature_set_uri in hashkey_formats_map:
            continue

        hash_key_format, _ = _get_lookup_key_pattern(
            feature.feature_set_reference, feature.feature_set_reference.online_materialization_version
        )
        featureset_schema_version = 1
        if hasattr(feature.feature_set_reference, "schema_version") and \
                feature.feature_set_reference.schema_version is not None:
            featureset_schema_version = feature.feature_set_reference.schema_version

        if featureset_schema_version == 1:
            hash_key_format = hash_key_format.rstrip(":")

            for entity in feature.feature_set_reference.entities:
                for index_column in entity.index_columns:
                    hash_key_format += f":{index_column.name}:{{{index_column.name}}}"

            hashkey_formats_map[feature_set_uri] = hash_key_format
        elif featureset_schema_version == 2:
            hash_key_format += "("

            for entity in feature.feature_set_reference.entities:
                for index_column in entity.index_columns:
                    hash_key_format += f"{{{index_column.name}}}:"

            hash_key_format = hash_key_format.rstrip(":") + ")"
            hashkey_formats_map[feature_set_uri] = hash_key_format
        else:
            raise ValidationException(
                f"Unsupported schema version {featureset_schema_version} for feature '{feature_set_uri}'",
                f"Unsupported schema version {featureset_schema_version} for feature '{feature_set_uri}'",
            )

    return hashkey_formats_map


def _init_features_map(features, redis_database_overrides=None):
    features_map = {}

    for feature in features:
        if redis_database_overrides is not None and \
                feature.feature_set_reference.feature_store_guid in redis_database_overrides:
            redis_arm_id = redis_database_overrides[feature.feature_set_reference.feature_store_guid]
        else:
            redis_arm_id = feature.feature_set_reference.online_store.target

        if hasattr(feature.feature_set_reference, "schema_version"):
            feature_set_schema_version = feature.feature_set_reference.schema_version or 1
        else:
            feature_set_schema_version = 1

        feature_set_uri = feature.uri.split(f"/features/{feature.name}")[0]
        feature_name = feature.name

        features_map[feature.uri.split("?")[0]] = (
            redis_arm_id,
            feature_set_uri,
            feature_set_schema_version,
            feature_name,
            feature.type,
            feature.output_name,
        )

    return features_map


class OnlineFeatureGetterV3(object):
    def __init__(
            self,
            credential,
            initial_feature_uris=None,
            feature_sets_to_recompute: Optional[List[str]] = None,
            redis_database_overrides: Optional[Dict[str, str]] = None):

        global_start_time = time.perf_counter()

        # reconstruct feature objects from URIs
        feature_construction_start_time = time.perf_counter()
        print(f"[{time.time()}] Constructing feature objects...", flush=True)
        features, feature_sets = _parse_feature_uris(initial_feature_uris, feature_sets_to_recompute, credential)
        print(
            f"[{time.time()}] Done constructing feature objects in {time.perf_counter() - feature_construction_start_time} seconds.", #pylint: disable=line-too-long
            flush=True
        )

        # maps redis resource ARM IDs to redis clients
        redis_initialization_start_time = time.perf_counter()
        print(f"[{time.time()}] Constructing redis clients...", flush=True)
        self.redis_clients = _init_redis_clients(features, credential, redis_database_overrides)
        print(
            f"[{time.time()}] Done constructing redis clients in {time.perf_counter() - redis_initialization_start_time} seconds.", #pylint: disable=line-too-long
            flush=True
        )

        # maps feature_set_uris to a format string that can be used with str.format and the observation row dict to
        # produce the redis hashkey for this featureset and any observation row.
        formatter_construction_start_time = time.perf_counter()
        print(f"[{time.time()}] Constructing lookup key formatters...", flush=True)
        self.hashkey_formats = _init_hashkey_formats(features)
        print(
            f"[{time.time()}] Done constructing key formatters in {time.perf_counter() - formatter_construction_start_time} seconds.", #pylint: disable=line-too-long
            flush=True
        )

        # maps feature URIs (without query params) to a tuple of (redis_resource_arm_id, feature_set_uri, feature_name,
        # feature_data_type, feature_output_name)
        feature_map_construction_start_time = time.perf_counter()
        print(f"[{time.time()}] Indexing features...", flush=True)
        self.features_map = _init_features_map(features, redis_database_overrides)
        print(
            f"[{time.time()}] Done indexing features in {time.perf_counter() - feature_map_construction_start_time} seconds.", #pylint: disable=line-too-long
            flush=True
        )

        # Construct an asyncio event loop for use in retrieval operations later
        event_loop_construction_start_time = time.perf_counter()
        print(f"[{time.time()}] Creating event loop...", flush=True)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        print(
            f"[{time.time()}] Done creating event loop in {time.perf_counter() - event_loop_construction_start_time} seconds.", #pylint: disable=line-too-long
            flush=True
        )

        self.featuresets_to_recompute = feature_sets
        if self.featuresets_to_recompute:
            on_the_fly_getter_init_start_time = time.perf_counter()
            print(f"[{time.time()}] Initializing on-the-fly feature getter...", flush=True)
            self.on_the_fly_feature_getter = OnTheFlyFeatureGetter(credential, features, self.featuresets_to_recompute)
            print(
                f"[{time.time()}] Initialized OTF feature getter in {time.perf_counter() - on_the_fly_getter_init_start_time} seconds.", #pylint: disable=line-too-long
                flush=True
            )
        else:
            print(f"[{time.time()}] No on-the-fly features to recompute.", flush=True)

        print(
            f"[{time.time()}] OnlineFeatureGetterV3 fully initialized in {time.perf_counter() - global_start_time} seconds.", #pylint: disable=line-too-long
            flush=True
        )

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

        try:
            feature_dataframe = self.loop.run_until_complete(
                self._fetch_feature_data(feature_uris=feature_uris, observation_df=observation_df)
            )
        except Exception as e:
            print(f"[{time.time()}] Error fetching feature data: {e}", flush=True)
            raise

        print(f"[{time.time()}] Successfully fetched feature data.", flush=True)

        return feature_dataframe

    async def _fetch_feature_data(self, feature_uris: "List[str]", observation_df: "pyarrow.Table"):
        grouping_start = time.perf_counter()
        grouped_features = self._group_features_by_redis_resource_and_featureset(
            feature_uris, set(observation_df.column_names)
        )
        grouping_latency = time.perf_counter() - grouping_start

        observation_df_pylist = observation_df.to_pylist()
        retrieval_tasks = []
        retrieved_feature_data = []

        network_start = time.perf_counter()
        # Start retrieval tasks for all the data that we need to fetch
        for (redis_resource_id, feature_group) in grouped_features.items():
            redis_client = self.redis_clients[redis_resource_id]
            retrieved_feature_data.append({})

            # for each observation dataframe row, do:
            for observation_dict in observation_df_pylist:
                # for each featureset we're retrieving data from, do:
                for feature_set_uri, feature_tuples in feature_group.items():
                    # get the hashkey format string for this featureset
                    feature_set_hashkey_format = self.hashkey_formats[feature_set_uri]

                    # collect feature names, and add columns for the feature data
                    feature_names = []
                    for schema_version, feature_name, feature_data_type, feature_output_name in feature_tuples:
                        retrieved_feature_data[-1][feature_output_name] = []
                        feature_names.append(feature_name)

                    # issue an HMGET for all the features we need, for this featureset, for this row of observations
                    retrieval_tasks.append(
                        redis_client.hmget(feature_set_hashkey_format.format(**observation_dict), feature_names))

        # process redis responses
        for (group_index, (_, feature_group)) in enumerate(grouped_features.items()):
            for observation_dict in observation_df_pylist:
                for feature_set_uri, feature_tuples in feature_group.items():
                    hmget_response = await retrieval_tasks.pop(0)
                    for (schema_version, feature_name, feature_data_type, feature_output_name), feature_value in \
                            zip(feature_tuples, hmget_response):
                        # Schema version 1 - featureset that uses base64 encoding and msgpack
                        if schema_version == 1:
                            retrieved_feature_data[group_index][feature_output_name].append(
                                None if feature_value is None else _type_converters[feature_data_type](feature_value)
                            )
                        # Schema version 2 - featureset that uses direct struct encoding
                        elif schema_version == 2:
                            retrieved_feature_data[group_index][feature_output_name].append(
                                None if feature_value is None else _type_deserializers[feature_data_type](feature_value)
                            )
                        else:
                            raise ValidationException(
                                f"Unsupported schema version {schema_version} for feature "
                                f"'{feature_set_uri}/{feature_name}'",
                                f"Unsupported schema version {schema_version} for feature "
                                f"'{feature_set_uri}/{feature_name}'",
                            )
        network_latency = time.perf_counter() - network_start

        postprocess_start = time.perf_counter()
        combined_feature_dict = observation_df.to_pydict()
        for feature_dict in retrieved_feature_data:
            combined_feature_dict = {**combined_feature_dict, **feature_dict}

        # collect results into a feature dataframe
        combined_feature_df = pyarrow.Table.from_pydict(combined_feature_dict)
        postprocess_latency = time.perf_counter() - postprocess_start

        # return
        print(
            f"Feature data retrieval latencies: "
            f"grouping={grouping_latency:.4f}s, "
            f"network={network_latency:.4f}s, "
            f"postprocess={postprocess_latency:.4f}s",
            flush=True
        )
        return combined_feature_df

    def _group_features_by_redis_resource_and_featureset(
        self, feature_uris: List[str], column_names: Set[str]
    ) -> Dict[str, Dict[str, List[Tuple[int, str, str, str]]]]:
        # this is a dict[str, dict[str, list[tuple(str, str, str)]]]
        # the top-level dictionary keys are redis resource IDs. All the features under a single key in the top-level
        # dict can be found in that redis resource. The nested dictionary keys are feature set uris. All the features
        # under a single key in the nested dict can be found under a single hash key in redis.
        # The values in the nested dictionary are a list of tuples, with this structure:
        # (featureset_schema_version, feature_name, data_type, output_name)
        redis_resources_to_features = {}

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

            redis_resource, feature_set_uri, feature_set_schema_version, \
                feature_name, default_data_type, default_output_name = \
                    self.features_map[feature_uri]

            if redis_resource not in redis_resources_to_features:
                redis_resources_to_features[redis_resource] = {}

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
                (feature_set_schema_version, feature_name, feature_data_type or default_data_type, selected_output_name)
            )

        return redis_resources_to_features
