# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-locals,logging-fstring-interpolation,no-member,too-many-statements

import datetime
from typing import TYPE_CHECKING

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._telemetry.activity import ActivityType, monitor_with_activity
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationErrorType, ValidationException

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._utils._constants import MAXIMUM_MATERIALIZATION_RETRY_TIMES, PACKAGE_NAME
from azureml.featurestore._utils.arm_id_utils import OfflineStoreTargetArmId
from azureml.featurestore._utils.error_constants import (
    OFFLINE_CONNECTION_NAME_MISTMACH,
    OFFLINE_MATERIALIZATION_DISABLED,
)
from azureml.featurestore._utils.utils import _build_logger
from azureml.featurestore.contracts.offline_store import OfflineStore

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

ops_logger = _build_logger(__name__)


class AzureDataLakeOfflineStore(OfflineStore):
    def __init__(self, target: str, connection_name: str, location: str):
        self.__location = location
        super().__init__(target=target, connection_name=connection_name)

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->OfflineStore.ReadData", ActivityType.PUBLICAPI)
    def read_data(
        self,
        feature_set: FeatureSet,
        feature_window_start_time: datetime = None,
        feature_window_end_time: datetime = None,
        **kwargs,
    ) -> "DataFrame":
        if not feature_set.materialization_settings.offline_enabled:
            raise ValidationException(
                message=OFFLINE_MATERIALIZATION_DISABLED.format(feature_set.name, feature_set.version),
                no_personal_data_message=OFFLINE_MATERIALIZATION_DISABLED,
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.FEATURE_SET,
            )

        if self.connection_name != feature_set.offline_store_connection_name:
            raise ValidationException(
                message=OFFLINE_CONNECTION_NAME_MISTMACH,
                no_personal_data_message=OFFLINE_CONNECTION_NAME_MISTMACH,
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

        materialization_version = kwargs.get("materialization_version", None)

        df = self.validate_data(
            feature_set=feature_set,
            feature_window_start_time=feature_window_start_time,
            feature_window_end_time=feature_window_end_time,
            materialization_version=materialization_version,
        )
        if not df:
            return None

        from pyspark.sql.functions import col, lit, to_timestamp

        partition_column = feature_set.partition.partition_column

        if feature_window_start_time:
            feature_window_start_partition = feature_set.partition.get_partition(feature_window_start_time)
            df = df.filter(col(partition_column) >= lit(feature_window_start_partition))
            df = df.filter(
                col(feature_set.source.timestamp_column.name) >= to_timestamp(lit(feature_window_start_time))
            )

        if feature_window_end_time:
            feature_window_end_partition = feature_set.partition.get_partition(feature_window_end_time)
            df = df.filter(col(partition_column) <= lit(feature_window_end_partition))
            df = df.filter(col(feature_set.source.timestamp_column.name) < to_timestamp(lit(feature_window_end_time)))

        return df

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->OfflineStore.WriteData", ActivityType.PUBLICAPI)
    def write_data(
        self,
        feature_set: FeatureSet,
        df: "DataFrame" = None,
        feature_window_start_time: datetime = None,
        feature_window_end_time: datetime = None,
        **kwargs,
    ) -> int:
        replace = kwargs.get("replace", False)
        materialization_version = kwargs.get("materialization_version", None)

        try:
            if not feature_set.materialization_settings.offline_enabled:
                raise ValidationException(
                    message=OFFLINE_MATERIALIZATION_DISABLED.format(feature_set.name, feature_set.version),
                    no_personal_data_message=OFFLINE_MATERIALIZATION_DISABLED,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )

            if self.connection_name != feature_set.offline_store_connection_name:
                raise ValidationException(
                    message=OFFLINE_CONNECTION_NAME_MISTMACH,
                    no_personal_data_message=OFFLINE_CONNECTION_NAME_MISTMACH,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.GENERAL,
                )

            from delta.exceptions import ConcurrentAppendException, ConcurrentDeleteReadException

            if not df:
                return 0

            timestamp_column, _ = feature_set.get_timestamp_column()
            partition_column = feature_set.partition.partition_column

            partitions = [partition_column]

            table_path = self.__get_offline_store_table_path(
                OfflineStoreTargetArmId(self.target),
                feature_set.arm_id,
                materialization_version=materialization_version,
            )

            df = feature_set.partition.apply_partition(df=df)

            number_of_materialized_rows = df.count()
            print(
                f"[Materialization Job] Ingest feature set: {feature_set.name}, version: {feature_set.version} data"
                f" into offline store: {self.target}"
            )
            table_exist = bool(
                self.validate_data(feature_set=feature_set, materialization_version=materialization_version)
            )
            for i in range(0, MAXIMUM_MATERIALIZATION_RETRY_TIMES):
                try:
                    if table_exist:
                        if replace:
                            print(
                                f"[Materialization Job] Overwrite data in existing table: {feature_set.name}, version:"
                                f" {feature_set.version}"
                            )
                            start_partition = feature_set.partition.get_partition(feature_window_start_time)
                            end_partition = feature_set.partition.get_partition(feature_window_end_time)

                            condition = (
                                f"{partition_column} >= '{start_partition}' AND {partition_column} <= '{end_partition}'"
                                f" AND {timestamp_column} >= '{feature_window_start_time}' AND {timestamp_column} <"
                                f" '{feature_window_end_time}'"
                            )

                            df.write.mode("overwrite").format("delta").option("replaceWhere", condition).save(
                                table_path
                            )
                        else:
                            print(
                                f"[Materialization Job] Appending data to existing table: {feature_set.name}, version:"
                                f" {feature_set.version}"
                            )
                            df.write.partitionBy(partitions).format("delta").mode("append").save(table_path)
                    else:
                        print(
                            f"[Materialization Job] Creating new table: {feature_set.name}, version:"
                            f" {feature_set.version}"
                        )
                        df.write.partitionBy(partitions).format("delta").mode("overwrite").save(table_path)
                    print("Successfully write data to offline store")
                    return number_of_materialized_rows
                except (ConcurrentAppendException, ConcurrentDeleteReadException):
                    print(
                        "[Materialization Job] Warning: hit concurrent operation exception when ingesting data, retry:"
                        f" {i + 1}"
                    )
                    if i == MAXIMUM_MATERIALIZATION_RETRY_TIMES:
                        ex_msg = "[Materialization Job] Failed to materialize after max retry."
                        log_and_raise_error(Exception(ex_msg), debug=True)
                    continue
        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, MlException):
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->OfflineStore.WriteData, {type(ex).__name__}: {ex.no_personal_data_message}"
                )
            else:
                ops_logger.package_logger.error(f"{PACKAGE_NAME}->OfflineStore.WriteData, {type(ex).__name__}: {ex}")

            log_and_raise_error(error=ex, debug=True)

    def validate_data(
        self,
        feature_set: FeatureSet,
        feature_window_start_time: datetime = None,
        feature_window_end_time: datetime = None,
        **kwargs,
    ) -> "DataFrame":
        from pyspark.sql import SparkSession
        from pyspark.sql.utils import AnalysisException

        spark = SparkSession.builder.getOrCreate()

        materialization_version = kwargs.pop("materialization_version", None)
        materialized_path = self.__get_offline_store_table_path(
            OfflineStoreTargetArmId(self.target), feature_set.arm_id, materialization_version=materialization_version
        )
        try:
            df = spark.read.format("delta").load(materialized_path)
            return df
        except AnalysisException as ae:
            if "not exist" in str(ae) or "not a Delta table" in str(ae):
                return None
            raise

    def __get_offline_store_table_path(
        self,
        offline_store_arm_id: OfflineStoreTargetArmId,
        feature_set_version_arm_id: AMLVersionedArmId,
        materialization_version: str = None,
    ):
        feature_store_id = "{}_{}_{}".format(
            feature_set_version_arm_id.workspace_name,
            feature_set_version_arm_id.subscription_id,
            feature_set_version_arm_id.resource_group_name,
        )

        path = "{}/{}/{}/{}".format(
            offline_store_arm_id.to_abfs_path(self.__location),  # cspell:ignore abfs
            feature_store_id,
            feature_set_version_arm_id.asset_name,
            feature_set_version_arm_id.asset_version,
        )

        if materialization_version:
            path = "{}/{}/{}/{}/{}".format(
                offline_store_arm_id.to_abfs_path(self.__location),  # cspell:ignore abfs
                feature_store_id,
                "materialize_store",
                feature_set_version_arm_id.asset_name,
                feature_set_version_arm_id.asset_version,
            )
            path = "{}/{}".format(path, materialization_version)

        return path.lower()
