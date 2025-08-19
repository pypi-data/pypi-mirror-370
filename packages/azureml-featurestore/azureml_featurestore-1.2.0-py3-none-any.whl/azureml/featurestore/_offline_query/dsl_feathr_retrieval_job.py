# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore jspark

from typing import List, Set, Tuple

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._offline_query.offline_retrieval_job import OfflineRetrievalJob
from azureml.featurestore._utils._constants import TIME_STAMP_FORMAT_ARG
from azureml.featurestore._utils.dsl_utils import _to_feathr_fset_config, _to_feathr_join_config
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.transformation import TransformationExpressionCollection

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


@experimental
class DslFeathrRetrievalJob(OfflineRetrievalJob):
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

        observation_df_timestamp_range = infer_event_timestamp_range(observation_data, timestamp_column)

        self.observation_df_start = observation_df_timestamp_range[0]
        self.observation_df_end = observation_df_timestamp_range[1]

        self.feature_sets = feature_sets
        self.observation_data = observation_data
        self.feature_references = feature_references
        self.features = features
        self.observation_timestamp_column = timestamp_column
        self.observation_timestamp_format = kwargs.get(TIME_STAMP_FORMAT_ARG, "%Y-%m-%d")

        self.use_materialized_data = use_materialized_data

    def to_spark_dataframe(self) -> "DataFrame":
        from pyspark.sql import DataFrame
        from pyspark.sql.session import SparkSession

        spark = SparkSession.builder.getOrCreate()
        sc = spark.sparkContext

        if self.use_materialized_data:
            from azureml.featurestore._offline_query import DslFeathrShimRetrievalJob
            from azureml.featurestore._utils.spark_utils import _offline_retrieval_job_schema_check

            job = DslFeathrShimRetrievalJob(
                feature_sets=self.feature_sets,
                feature_references=self.feature_references,
                features=self.features,
                observation_data=self.observation_data,
                timestamp_column=self.observation_timestamp_column,
                use_materialized_data=True,
            )

            return job.to_spark_dataframe()

        dsl = sc._jvm.entrypoint.FeatureJobEntryPoint()  # pylint: disable=protected-access
        feathr_join_string, feathr_config_string = self._to_feathr_config()
        jdf = dsl.joinFeatures(
            spark._jsparkSession,  # pylint: disable=protected-access
            feathr_join_string,
            feathr_config_string,
            self.observation_data._jdf,  # pylint: disable=protected-access
        )

        df = DataFrame(jdf, spark)

        df = _offline_retrieval_job_schema_check(self, df)

        return df

    def _to_feathr_config(self) -> Tuple[str, str]:
        feature_names = [feature.name for feature in self.features]
        join_keys = []
        for feature_set in self.feature_sets:
            if not isinstance(feature_set.feature_transformation, TransformationExpressionCollection):
                msg = (
                    "Feature Set {} does not have a valid feature transformation. "
                    "All feature transformations must be defined by a transformation expression."
                )
                raise ValidationException(
                    message=msg.format(feature_set.name),
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

            join_keys.extend([idx_col.name for idx_col in feature_set.get_index_columns()])

        feathr_join_string = _to_feathr_join_config(
            timestamp_col_name=self.observation_timestamp_column,
            timestamp_col_format=self.observation_timestamp_format,
            feature_names=feature_names,
            join_keys=join_keys,
            start_time=str(self.observation_df_start),
            end_time=str(self.observation_df_end),
        )

        feathr_config_string = _to_feathr_fset_config(feature_sets=self.feature_sets)

        return feathr_join_string, feathr_config_string
