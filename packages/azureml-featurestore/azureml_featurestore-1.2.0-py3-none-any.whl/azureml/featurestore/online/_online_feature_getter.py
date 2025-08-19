# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from collections import defaultdict
from typing import List

import pandas
from azureml.featurestore._utils.utils import _build_logger
from azureml.featurestore.contracts.column import ColumnType
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.contracts.store_connection import OnlineStoreType

from ._redis_client_pool import RedisClientPool
from ._utils import _get_lookup_key

ops_logger = _build_logger(__name__)


class OnlineFeatureGetter(object):
    def __init__(self, credential, initial_feature_uris=None):
        self.feature_map = dict()

        redis_resource_ids = self._populate_feature_map(initial_feature_uris, credential)
        self.client_pool = RedisClientPool(redis_resource_ids, credential)

        self.output_converters = {
            ColumnType.STRING.name: str,
            ColumnType.INTEGER.name: int,
            ColumnType.LONG.name: int,
            ColumnType.FLOAT.name: float,
            ColumnType.DOUBLE.name: float,
            ColumnType.BOOLEAN.name: bool,
            ColumnType.BINARY.name: lambda s: bin(int(s)),
            ColumnType.DATETIME.name: (
                pandas.to_datetime
            ),  # TODO: parse with customized format from customer featureset spec
        }

    def _populate_feature_map(self, feature_uris: List[str], credential):
        """
        Populate feature map when new features fed in during initialization.
        """
        redis_resource_ids = set()
        for feature_uri in feature_uris:
            feature = Feature.from_uri(feature_uri, credential)
            self.feature_map[feature_uri] = feature

            if not feature.feature_set_reference.online_store.target:
                raise Exception(
                    f'Feature "{feature_uri}" belongs to a feature store that does not specify an online store'
                    " connection."
                )

            if feature.feature_set_reference.online_store.type == OnlineStoreType.REDIS:
                redis_resource_ids.add(feature.feature_set_reference.online_store.target)
            else:
                raise Exception(
                    f'Feature "{feature_uri}" specifies an online store connection of type'
                    f' "{feature.feature_set_reference.online_store.type}". Only "redis" online stores are currently'
                    " supported."
                )

        return redis_resource_ids

    def _group_features_by_feature_set(self, feature_uris: List[str]):
        target_feature_sets = dict()
        for feature_uri in feature_uris:
            feature = self.feature_map[feature_uri]

            if feature.feature_set_reference.arm_id not in target_feature_sets:
                target_feature_sets[feature.feature_set_reference.arm_id] = (
                    [(feature.name, feature.type)],
                    feature.feature_set_reference,
                )
            else:
                target_feature_sets[feature.feature_set_reference.arm_id][0].append((feature.name, feature.type))

        # pylint: disable=logging-fstring-interpolation
        logging.info(f"Feature sets found from features:\n {target_feature_sets}")

        return target_feature_sets

    def _get_client_online_features(self, redis_client, feature_set, feature_pairs, observation_df):
        feature_values = defaultdict(list)
        for _, row in observation_df.iterrows():  # cspell:disable-line
            redis_key = _get_lookup_key(feature_set, row)
            # For a non-existing key will return a list of nil values.
            # For every field that does not exist in the hash, a nil value is returned.
            results = redis_client.hmget(  # cspell:disable-line
                redis_key, [feature_name for feature_name, _ in feature_pairs]
            )

            for index, res in enumerate(results):
                feature_name, feature_type = feature_pairs[index]
                if res is not None:
                    value = self.output_converters[feature_type](res.decode("utf-8"))
                else:
                    value = None  # TODO: Raise exception
                feature_values[feature_name].append(value)

        return feature_values

    def get_online_features(self, feature_uris: List[str], observation_df: "pandas.DataFrame"):
        target_feature_sets = self._group_features_by_feature_set(feature_uris)

        feature_dataframe = observation_df.to_dict("list")
        features_seen = set()
        for feature_set in target_feature_sets:
            feature_pairs, feature_set = target_feature_sets[feature_set]

            redis_client = self.client_pool.get_client(feature_set.online_store.target)
            client_feature_dataframe = self._get_client_online_features(
                redis_client, feature_set, feature_pairs, observation_df
            )

            duplicate_features = features_seen.intersection(set(client_feature_dataframe.keys()))
            if duplicate_features:
                raise Exception(f"Duplicate features {duplicate_features} found from different feature sets.")

            features_seen.update(set(client_feature_dataframe.keys()))

            feature_dataframe.update(client_feature_dataframe)

        return pandas.DataFrame(feature_dataframe)
