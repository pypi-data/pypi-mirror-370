# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore fstore, dedup
# pylint: disable=too-many-instance-attributes

from datetime import timedelta
from typing import List, Set

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._offline_query.point_at_time import PointAtTimeRetrievalJob
from azureml.featurestore._utils._constants import COL_OBSERVATION_ENTITY_TIMESTAMP
from azureml.featurestore.contracts.feature import Feature


class EqualTimeRetrievalJob(PointAtTimeRetrievalJob):
    def __init__(
        self,
        feature_sets: Set[FeatureSet],
        feature_references: List[str],
        features: List[Feature],
        observation_data,
        timestamp_column: str,
        use_materialized_data: bool,
        **kwargs
    ):
        super().__init__(feature_sets=feature_sets, feature_references=feature_references,
                         features=features, observation_data=observation_data, timestamp_column=timestamp_column,
                         use_materialized_data=use_materialized_data, **kwargs)

    def _process_feature_set(self, observation_df, feature_set, features, observation_row_id_col_name, **kwargs):
        from pyspark.sql.functions import col

        # 1. Get the feature set dataframe using the feature window start and end
        # start timestamp - temporal join lookback limit
        feature_window_start = self.observation_df_start
        # add 1 millisecond to the end time,
        # so that the feature set to_spark_df() can be inclusive to the last event time in observation data
        # in the equal time join, the temporal_look_back should be 0, and source_delay is not used during join.
        feature_window_end = self.observation_df_end + timedelta(milliseconds=1)

        # no need to dedup on to_spark_df
        df = feature_set.to_spark_dataframe(
            feature_window_start_date_time=feature_window_start,
            feature_window_end_date_time=feature_window_end,
            use_materialized_data=self.use_materialized_data,
            **kwargs,
        )
        # 2. select the index column, timestamp column, and required features
        idx_cols = [idx_col.name for idx_col in feature_set.get_index_columns()]
        timestamp_col, _ = feature_set.get_timestamp_column()

        col_list = idx_cols + features + [timestamp_col]
        col_aliases = {timestamp_col: "event_timestamp"}

        selected_columns = [col(c).alias(col_aliases.get(c, c)) for c in col_list]
        df = df.select(selected_columns)

        # 3. create a unique list of row ids for this feature set on the observation df
        # including the timestamp, idx columns used by feature_set, the corresponding unique row id column
        col_list = idx_cols + [COL_OBSERVATION_ENTITY_TIMESTAMP, observation_row_id_col_name]
        observation_dataframe_dedup = observation_df.select(col_list).distinct()

        # 4. inner join the feature_set df with observation_dataframe_dedup
        #  join by the index columns and also on timestamp (getting only features from the past of observation)
        #  this should filter out rows in the feature set df which are not used by the observation data df
        #  apply both source_delay and temporal_join_lookback

        df = (
            df.alias("subquery")
            .join(observation_dataframe_dedup.alias("observation_dataframe"), on=idx_cols, how="inner")
            .where(
                col("subquery.event_timestamp")
                == col(f"observation_dataframe.{COL_OBSERVATION_ENTITY_TIMESTAMP}")
            )
        )

        df = df.select(
            "subquery.*",
            col(f"observation_dataframe.{COL_OBSERVATION_ENTITY_TIMESTAMP}"),
            col(f"observation_dataframe.{observation_row_id_col_name}"),
        )

        # 5. final clean up
        # only select the unique row id and the feature columns
        col_list = features + [observation_row_id_col_name]
        df = df.select(col_list)

        return df
