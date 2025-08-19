# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from datetime import timedelta
from typing import List, Set

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._offline_query.offline_retrieval_job import OfflineRetrievalJob
from azureml.featurestore._utils._constants import (
    COL_OBSERVATION_ENTITY_TIMESTAMP,
    QUERY_APPLY_SOURCE_DELAY_KEY,
    QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY,
)
from azureml.featurestore._utils.dsl_utils import _to_feathr_shim_config
from azureml.featurestore._utils.utils import get_feature_set_to_features_map
from azureml.featurestore.contracts.feature import Feature

from azure.ai.ml._utils._experimental import experimental


@experimental
class DslFeathrShimRetrievalJob(OfflineRetrievalJob):
    def __init__(
        self,
        feature_sets: Set[FeatureSet],
        feature_references: List[str],
        features: List[Feature],
        observation_data,
        timestamp_column: str,
        use_materialized_data: bool,
        **kwargs,
    ):
        from azureml.featurestore._utils.spark_utils import infer_event_timestamp_range

        self.apply_source_delay = True
        if QUERY_APPLY_SOURCE_DELAY_KEY in kwargs:
            self.apply_source_delay = kwargs[QUERY_APPLY_SOURCE_DELAY_KEY]

        self.apply_temporal_join_lookback = True
        if QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY in kwargs:
            self.apply_temporal_join_lookback = kwargs[QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY]

        self.observation_df_timestamp_range = infer_event_timestamp_range(observation_data, timestamp_column)
        self.feature_sets = feature_sets
        self.observation_data = observation_data
        self.feature_references = feature_references
        self.features = features
        self.observation_timestamp_column = timestamp_column

        self.use_materialized_data = use_materialized_data

        self.feature_set_to_features_map = get_feature_set_to_features_map(self.feature_sets, self.feature_references)

    def to_spark_dataframe(self, **kwargs) -> "DataFrame":
        from pyspark.sql.functions import unix_timestamp
        from azureml.featurestore._utils.spark_utils import _dsl_shim_join, _offline_retrieval_job_schema_check

        # create a new timestamp_seconds column on the observation data, for feathr
        observation_df = self.observation_data.withColumn(
            COL_OBSERVATION_ENTITY_TIMESTAMP, unix_timestamp(self.observation_timestamp_column)
        )

        # for each feature set, get the source df, timestamp, joinkeys, and the dsl features
        scala_features_list = []
        for featureset in self.feature_sets:
            feature_window_start = None
            # add 1 millisecond to the end time
            # so that the feature set to_spark_df() can be inclusive to the last event time in observation data
            feature_window_end = self.observation_df_timestamp_range[1] + timedelta(milliseconds=1)
            if self.apply_temporal_join_lookback and featureset.temporal_join_lookback:
                feature_window_start = (
                    self.observation_df_timestamp_range[0] - featureset.temporal_join_lookback.to_timedelta()
                )
            if self.apply_source_delay and featureset.source.source_delay:
                source_delay = featureset.source.source_delay.to_timedelta()
                feature_window_start = feature_window_start - source_delay if feature_window_start else None
                feature_window_end = feature_window_end - source_delay

            df = featureset._load_dataframe_dsl(
                feature_window_start_date_time=feature_window_start,
                feature_window_end_date_time=feature_window_end,
                use_materialized_data=self.use_materialized_data,
                **kwargs
            )

            features = self.feature_set_to_features_map[featureset]
            scala_features_list.append(
                _to_feathr_shim_config(
                    source_df=df,
                    feature_set_or_spec=featureset,
                    features=features,
                    is_materialized=self.use_materialized_data,
                )
            )

        df = _dsl_shim_join(
            observation_df=observation_df,
            scala_features_list=scala_features_list,
            should_apply_source_transformation=not self.use_materialized_data,
        )

        df = _offline_retrieval_job_schema_check(self, df)

        return df
