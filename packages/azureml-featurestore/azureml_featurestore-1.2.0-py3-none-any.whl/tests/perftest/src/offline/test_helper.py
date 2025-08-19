import time
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


class TestHelper:
    @staticmethod
    def get_obs_df(
        spark: SparkSession,
        obs_key: str,
        timestamp_column: str,
        start_time: datetime,
        end_time: datetime,
        obs_cloud_path: str,
    ):

        key = "DOLocationID"
        return (
            spark.read.parquet(obs_cloud_path, header=True, inferSchema=True)
            .select(key, timestamp_column)
            .filter(col(key) == obs_key)
            .where(col(timestamp_column).between(*(start_time, end_time)))
        )

    @staticmethod
    def test_materialize(feature_set, feature_window_start_time, feature_window_end_time, attempt_times):
        from azureml.featurestore._utils.materialize import materialize

        time_taken = []
        for i in range(attempt_times):
            start_counter = time.perf_counter()
            materialize(
                feature_set=feature_set,
                feature_window_start_time=feature_window_start_time,
                feature_window_end_time=feature_window_end_time,
                upsert=True,
                offline_prefix=feature_set._FeatureSet__offline_materialization_version,
            )
            time_taken.append(time.perf_counter() - start_counter)

        min_time = round(min(time_taken), 2)
        avg_time = round(sum(time_taken) / len(time_taken), 2)
        max_time = round(max(time_taken), 2)

        return {"min": min_time, "avg": avg_time, "max": max_time}

    @staticmethod
    def test_offline_retrieval(features, observation_data, timestamp_col, use_materialized_data, attempt_times):
        from azureml.featurestore import get_offline_features

        time_taken = []
        for i in range(attempt_times):
            start_counter = time.perf_counter()
            training_df = get_offline_features(
                features=features,
                observation_data=observation_data,
                timestamp_column=timestamp_col,
                use_materialized_data=use_materialized_data,
            )
            time_taken.append(time.perf_counter() - start_counter)
        min_time = round(min(time_taken), 2)
        avg_time = round(sum(time_taken) / len(time_taken), 2)
        max_time = round(max(time_taken), 2)

        return {"min": min_time, "avg": avg_time, "max": max_time}
