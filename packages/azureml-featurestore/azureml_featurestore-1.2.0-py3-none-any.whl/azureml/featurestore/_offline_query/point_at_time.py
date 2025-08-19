# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore fstore, dedup
# pylint: disable=too-many-instance-attributes

from datetime import timedelta
from typing import List, Set

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._offline_query.offline_retrieval_job import OfflineRetrievalJob
from azureml.featurestore._utils._constants import (
    COL_OBSERVATION_ENTITY_TIMESTAMP,
    COL_OBSERVATION_FEATURE_SET_UNIQUE_ROW_ID,
    CREATE_TIMESTAMP_COLUMN,
    QUERY_APPLY_SOURCE_DELAY_KEY,
    QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY,
)
from azureml.featurestore._utils.utils import get_feature_set_to_features_map, validate_expected_columns_in_entity_df
from azureml.featurestore.contracts import TransformationCode
from azureml.featurestore.contracts.feature import Feature


class PointAtTimeRetrievalJob(OfflineRetrievalJob):
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
        from pyspark.sql import SparkSession

        validate_expected_columns_in_entity_df(
            dict(observation_data.dtypes),  # cspell: ignore dtypes
            timestamp_column,
            feature_sets,
        )

        observation_df_timestamp_range = infer_event_timestamp_range(observation_data, timestamp_column)

        self.observation_df_start = observation_df_timestamp_range[0]
        self.observation_df_end = observation_df_timestamp_range[1]

        self.feature_sets = feature_sets
        self.observation_data = observation_data
        self.feature_references = feature_references
        self.features = features
        self.observation_timestamp_column = timestamp_column

        self.use_materialized_data = use_materialized_data

        self.apply_source_delay = True
        if QUERY_APPLY_SOURCE_DELAY_KEY in kwargs:
            self.apply_source_delay = kwargs[QUERY_APPLY_SOURCE_DELAY_KEY]

        self.apply_temporal_join_lookback = True
        if QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY in kwargs:
            self.apply_temporal_join_lookback = kwargs[QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY]

        for feature_set in self.feature_sets:
            if feature_set.feature_transformation and not isinstance(
                feature_set.feature_transformation, TransformationCode
            ):
                msg = (
                    "Feature Set {} does not have a valid feature transformation. "
                    "Transformation must be a TransformationCode."
                )
                raise ValidationException(
                    message=msg.format(feature_set.name),
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

        spark_session = SparkSession.getActiveSession()
        if not spark_session:
            spark_builder = SparkSession.builder
            spark_session = spark_builder.getOrCreate()
        self.spark_session = spark_session

    def to_spark_dataframe(self, **kwargs):
        from pyspark.sql.functions import col, concat

        # make a deterministic list of output columns
        # first the columns in the same order from observation data
        # second, the list of features in the order it is given
        output_columns = self.observation_data.columns + [feature.name for feature in self.features]

        # make a copy of the timestamp column in the observation data
        observation_df = self.observation_data.withColumn(
            COL_OBSERVATION_ENTITY_TIMESTAMP, col(self.observation_timestamp_column)
        )

        feature_set_unique_row_id_col_names = {}

        # create unique row IDs in the observation (entity) df, one for each feature_set
        # row-id = index columns of the feature set + entity timestamp
        for feature_set in self.feature_sets:
            if isinstance(feature_set, FeatureSet):
                # this is a feature set, use arm id as the unique id
                fstore_guid = feature_set.feature_store_guid
            else:
                # this is feature set spec
                fstore_guid = "local"

            col_name = COL_OBSERVATION_FEATURE_SET_UNIQUE_ROW_ID.format(
                fstore_guid=fstore_guid, fset_name=feature_set.name, fset_version=feature_set.version
            )
            feature_set_unique_row_id_col_names[feature_set] = col_name

            fset_idx_cols = [idx_col.name for idx_col in feature_set.get_index_columns()]
            timestamp_col, _ = feature_set.get_timestamp_column()

            id_column_list = fset_idx_cols + [timestamp_col]
            observation_df = observation_df.withColumn(col_name, concat(*[col(c) for c in id_column_list]))

        feature_set_to_features_map = get_feature_set_to_features_map(self.feature_sets, self.feature_references)

        ## process each feature set dataframe
        all_fset_df = {}
        for feature_set in self.feature_sets:
            df = self._process_feature_set(
                observation_df,
                feature_set,
                feature_set_to_features_map[feature_set],
                f"`{feature_set_unique_row_id_col_names[feature_set]}`",
                **kwargs
            )

            all_fset_df[feature_set] = df

        # left join each processed feature set df into the observation df
        # join key is the unique row id corresponding to each feature set
        for feature_set, df in all_fset_df.items():
            col_name = feature_set_unique_row_id_col_names[feature_set]
            observation_df = observation_df.join(df, on=col_name, how="left")

        # select a list of columns by the output_column list
        observation_df = observation_df.select(*output_columns)

        return observation_df

    def _process_feature_set(self, observation_df, feature_set, features, observation_row_id_col_name, **kwargs):
        from pyspark.sql.functions import col, expr, row_number
        from pyspark.sql.window import Window

        # 1. Get the feature set dataframe using the feature window start and end
        # If temporal join lookback is not provided, we need to search from the begin of feature_set.
        # if a join lookback limit is provided, we can limit the dataframe to be the entity df
        # start timestamp - temporal join lookback limit
        # also if source_delay is set, shift the feature window accordingly
        # note that this is just define the rough window. the source_delay and temp join look back will be considered
        # accurately in the join itself
        feature_window_start = None
        # add 1 millisecond to the end time
        # so that the feature set to_spark_df() can be inclusive to the last event time in observation data
        feature_window_end = self.observation_df_end + timedelta(milliseconds=1)
        if self.apply_temporal_join_lookback and feature_set.temporal_join_lookback:
            feature_window_start = self.observation_df_start - feature_set.temporal_join_lookback.to_timedelta()
        if self.apply_source_delay and feature_set.source.source_delay:
            source_delay = feature_set.source.source_delay.to_timedelta()
            feature_window_start = feature_window_start - source_delay if feature_window_start else None
            feature_window_end = feature_window_end - source_delay

        # no need to dedup on tp_spark_df
        # later in the join, it will sort by event timestamp + create timestamp in each window anyway
        df = feature_set.to_spark_dataframe(
            feature_window_start_date_time=feature_window_start,
            feature_window_end_date_time=feature_window_end,
            use_materialized_data=self.use_materialized_data,
            **kwargs
        )

        # 2. select the index column, timestamp column, and required features
        # rename timestamp column to event_timestamp
        # if created_timestamp column does not exist, use the value of event timestamp column
        idx_cols = [idx_col.name for idx_col in feature_set.get_index_columns()]
        timestamp_col, _ = feature_set.get_timestamp_column()
        col_list = idx_cols + features + [timestamp_col, CREATE_TIMESTAMP_COLUMN]
        col_aliases = {timestamp_col: "event_timestamp", CREATE_TIMESTAMP_COLUMN: "created_timestamp"}

        if CREATE_TIMESTAMP_COLUMN not in df.columns:
            df = df.withColumn(CREATE_TIMESTAMP_COLUMN, col(timestamp_col))

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
        source_delay_expr = expr("INTERVAL 0 seconds")
        if self.apply_source_delay and feature_set.source and feature_set.source.source_delay:
            td = feature_set.source.source_delay.to_timedelta()
            source_delay_expr = expr(f"INTERVAL {td.days} days {td.seconds} seconds")

        df = (
            df.alias("subquery")
            .join(observation_dataframe_dedup.alias("observation_dataframe"), on=idx_cols, how="inner")
            .where(
                col("subquery.event_timestamp")
                <= col(f"observation_dataframe.{COL_OBSERVATION_ENTITY_TIMESTAMP}") - source_delay_expr
            )
        )

        if self.apply_temporal_join_lookback and feature_set.temporal_join_lookback:
            td = feature_set.temporal_join_lookback.to_timedelta()
            temporal_join_lookback_expr = expr(f"INTERVAL {td.days} days {td.seconds} seconds")
            df = df.where(
                col("subquery.event_timestamp")
                >= col(f"observation_dataframe.{COL_OBSERVATION_ENTITY_TIMESTAMP}") - temporal_join_lookback_expr
            )

        df = df.select(
            "subquery.*",
            col(f"observation_dataframe.{COL_OBSERVATION_ENTITY_TIMESTAMP}"),
            col(f"observation_dataframe.{observation_row_id_col_name}"),
        )

        # 5. run window function on the feature set df
        # window by the unique row id of the observation id, pick the row with max(event_timestamp, create_timestamp)
        df = (
            df.withColumn(
                "row_number",
                row_number().over(
                    Window.partitionBy(observation_row_id_col_name).orderBy(
                        col("event_timestamp").desc(), col("created_timestamp").desc()
                    )
                ),
            )
            .filter(col("row_number") == 1)
            .drop("row_number")
        )

        # 6. final clean up
        # only select the unique row id and the feature columns
        col_list = features + [observation_row_id_col_name]
        df = df.select(col_list)

        return df
