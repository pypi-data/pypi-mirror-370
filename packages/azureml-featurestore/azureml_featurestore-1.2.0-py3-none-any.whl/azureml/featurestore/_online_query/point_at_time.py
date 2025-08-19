# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from datetime import datetime, timezone
from typing import Dict, List
from warnings import warn

import pandas as pd
import pyarrow
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._online_query.online_retrieval_job import OnlineRetrievalJob
from azureml.featurestore._utils._constants import (
    COL_OBSERVATION_FEATURE_SET_UNIQUE_ROW_ID,
    CREATE_TIMESTAMP_COLUMN,
    QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY,
)
from azureml.featurestore._utils.utils import validate_expected_columns_in_entity_df


class PointAtTimeOnTheFlyRetrievalJob(OnlineRetrievalJob):
    def __init__(
        self,
        *,
        features_map: Dict[FeatureSet, List[str]],
        observation_data: pd.DataFrame,
        on_the_fly_entities: str = None,
        **kwargs,
    ):
        validate_expected_columns_in_entity_df(
            dict(observation_data.dtypes),  # cspell: ignore dtypes
            None,
            list(features_map.keys()),
        )
        self.observation_df_end = datetime.now(timezone.utc)
        self.observation_df_start = self.observation_df_end

        self.feature_sets = list(features_map.keys())
        self.feature_set_to_features_map = features_map
        self.observation_dataframe = observation_data
        self.features = [i for value in list(features_map.values()) for i in value]
        self.on_the_fly_entities = on_the_fly_entities

        self.apply_temporal_join_lookback = True
        if QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY in kwargs:
            self.apply_temporal_join_lookback = kwargs[QUERY_APPLY_TEMPORAL_JOIN_LOOKBACK_KEY]

        if not self.apply_temporal_join_lookback:
            self.observation_df_start = datetime(1970, 1, 1)

    def to_pandas_dataframe(self) -> pd.DataFrame:
        # make a deterministic list of output columns
        # first the columns in the same order from observation data
        # second, the list of features in the order it is given
        output_columns = self.observation_dataframe.columns.tolist() + self.features

        observation_df = self.observation_dataframe.copy()
        feature_set_unique_row_id_col_names = {}

        # create unique row IDs in the observation (entity) df, one for each feature_set
        # row-id = index columns of the feature set
        for feature_set in self.feature_sets:
            if isinstance(feature_set, FeatureSet):
                # this is a feature set, use arm id as the unique id
                fstore_guid = feature_set.feature_store_guid  # cspell: ignore fstore
            else:
                # this is feature set spec
                fstore_guid = "local"  # cspell: ignore fstore

            col_name = COL_OBSERVATION_FEATURE_SET_UNIQUE_ROW_ID.format(
                fstore_guid=fstore_guid,  # cspell: ignore fstore
                fset_name=feature_set.name,
                fset_version=feature_set.version,
            )
            feature_set_unique_row_id_col_names[feature_set] = col_name

            fset_idx_cols = [idx_col.name for idx_col in feature_set.get_index_columns()]
            # cspell: ignore astype
            observation_df[col_name] = observation_df[fset_idx_cols].apply(lambda x: "_".join(x.astype(str)), axis=1)

        # process each feature set dataframe
        all_fset_df = {}
        for feature_set in self.feature_sets:
            df = self._process_feature_set(
                observation_df,
                feature_set,
                self.feature_set_to_features_map[feature_set],
                feature_set_unique_row_id_col_names[feature_set],
            )

            all_fset_df[feature_set] = df

        # left join each processed feature set df into the observation df
        # join key is the unique row id corresponding to each feature set
        for feature_set, df in all_fset_df.items():
            col_name = feature_set_unique_row_id_col_names[feature_set]
            observation_df = observation_df.merge(df, on=col_name, how="left")

        # select a list of columns by the output_column list
        observation_df = observation_df[output_columns]

        return observation_df

    def to_pyarrow_table(self) -> pyarrow.Table:
        pandas_df = self.to_pandas_dataframe()
        return pyarrow.Table.from_pandas(df=pandas_df)

    def _process_feature_set(
        self,
        observation_df: pd.DataFrame,
        feature_set: FeatureSet,
        features: List[str],
        observation_row_id_col_name: str,
    ):
        """
        1. Get the feature set dataframe using the feature window start and end
        If temporal join lookback is not provided, we need to search from the beginning of feature_set.
        if a join lookback limit is provided, we can limit the dataframe to be the entity df
        start timestamp - temporal join lookback limit. This is just to define the rough window and
        the source_delay and temp join look back will be considered accurately in the join itself
        """

        feature_window_end = self.observation_df_end

        if self.apply_temporal_join_lookback:
            if not feature_set.temporal_join_lookback:
                msg = (
                    "Feature Set {} does not define temporal join lookback."
                    "Temporal join lookback is required for online on-the-fly feature retrieval."
                )
                raise ValidationException(
                    message=msg.format(feature_set.name),
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.MISSING_FIELD,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )

            feature_window_start = self.observation_df_start - feature_set.temporal_join_lookback.to_timedelta()
        else:
            warn("Temporal join lookback is overridden. This may result in performance degradation.")
            feature_window_start = self.observation_df_start

        df = (
            feature_set._to_pandas_dataframe(  # pylint: disable=protected-access
                feature_window_start_date_time=feature_window_start,
                feature_window_end_date_time=feature_window_end,
                on_the_fly_entities=self.on_the_fly_entities,
            )
            if self.on_the_fly_entities
            else (
                feature_set._to_pandas_dataframe(  # pylint: disable=protected-access
                    feature_window_start_date_time=feature_window_start,
                    feature_window_end_date_time=feature_window_end,
                )
            )
        )

        # 2. select the index column, timestamp column, and required features
        # rename timestamp column to event_timestamp
        # if created_timestamp column does not exist, use the value of event timestamp column
        # group by the index columns and keep only the latest timestamp
        idx_cols = [idx_col.name for idx_col in feature_set.get_index_columns()]
        timestamp_col, _ = feature_set.get_timestamp_column()
        col_list = idx_cols + features + [timestamp_col, CREATE_TIMESTAMP_COLUMN]
        col_aliases = {timestamp_col: "event_timestamp", CREATE_TIMESTAMP_COLUMN: "created_timestamp"}

        if CREATE_TIMESTAMP_COLUMN not in df.columns:
            df[CREATE_TIMESTAMP_COLUMN] = df[timestamp_col]

        df = df[col_list]
        df = df.rename(columns=col_aliases)

        df = df.sort_values("event_timestamp").groupby(idx_cols).tail(1)

        # 3. create a unique list of row ids for this feature set on the observation df
        # including the idx columns used by feature_set and the corresponding unique row id column
        col_list = idx_cols + [observation_row_id_col_name]
        observation_dataframe = observation_df[col_list].drop_duplicates()

        # 4. inner join the feature_set df with observation_dataframe
        df = df.merge(observation_dataframe, on=idx_cols, how="inner")

        # 5. final clean up
        # only select the unique row id and the feature columns
        col_list = features + [observation_row_id_col_name]
        df = df[col_list]

        return df
