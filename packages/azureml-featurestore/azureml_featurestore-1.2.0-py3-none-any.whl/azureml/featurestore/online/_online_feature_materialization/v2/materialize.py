# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-locals,too-many-statements
# cspell: ignore packb

import datetime
import os
import pkgutil
import time

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.identity import AzureMLOnBehalfOfCredential
from azureml.featurestore._utils._constants import TIME_TO_LIVE, AZUREML_FEATURESTORE_DEBUG_ENVVAR
from azureml.featurestore._utils.error_constants import ONLINE_CONNECTION_NAME_MISMATCH, ONLINE_MATERIALIZATION_DISABLED
from azureml.featurestore.contracts.store_connection import OnlineStoreType
from azureml.featurestore.online._online_feature_getter_v3 import _type_serializers
from azureml.featurestore.online._utils import _get_lookup_key_pattern
from azureml.featurestore.online._online_feature_materialization.v2.materialize_helpers import get_mapper
import msgpack

__LUA_SCRIPT_TEMPLATE = pkgutil.get_data(__name__, "_redis_materialization_function_template.lua").decode()
__ENABLE_MATERIALIZATION_LOGGING = os.getenv(AZUREML_FEATURESTORE_DEBUG_ENVVAR, "false").lower() == "true"


def _prepare_dataframe(feature_set, dataframe):
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import current_timestamp, unix_timestamp

    SparkSession.builder.getOrCreate()

    timestamp_column, _ = feature_set.get_timestamp_column()
    dataframe_to_store = dataframe\
        .withColumn(timestamp_column, unix_timestamp(dataframe[timestamp_column]))

    # If the featureset has a temporal lookback, filter out the rows that are older than the lookback
    temporal_lookback = feature_set.temporal_join_lookback
    if temporal_lookback:
        cur_time_unix = unix_timestamp(current_timestamp())
        temporal_lookback_seconds = temporal_lookback.to_timedelta().total_seconds()
        df = dataframe_to_store.withColumn(
            TIME_TO_LIVE, temporal_lookback_seconds - (cur_time_unix - dataframe_to_store[timestamp_column])
        )
        dataframe_to_store = df.filter(df[TIME_TO_LIVE] > 0).drop(TIME_TO_LIVE)

    return dataframe_to_store


def materialize_online(feature_set, dataframe, materialization_version=None):
    # Timestamp the start of online materialization
    online_materialization_start_time = time.time()

    # Various validations
    if not dataframe:
        print(f"[OnlineMaterialization @ {datetime.datetime.now(datetime.timezone.utc)}] No data to materialize.")
        return 0

    if not feature_set.online_store.target:
        msg = "Featureset {} belongs to a featurestore that does not specify an online store connection."
        raise ValidationException(
            message=msg.format(feature_set.arm_id),
            no_personal_data_message=msg,
            error_type=ValidationErrorType.INVALID_VALUE,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.FEATURE_SET,
        )

    if feature_set.online_store.type != OnlineStoreType.REDIS:
        msg = (
            "Featureset {} specifies an online store connection of type {}. Only 'redis' online stores are currently"
            " supported."
        )
        raise ValidationException(
            message=msg.format(feature_set.arm_id, feature_set.online_store.type),
            no_personal_data_message=msg,
            error_type=ValidationErrorType.INVALID_VALUE,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.FEATURE_SET,
        )

    if not feature_set.materialization_settings.online_enabled:
        raise ValidationException(
            message=ONLINE_MATERIALIZATION_DISABLED.format(feature_set.name, feature_set.version),
            no_personal_data_message=ONLINE_MATERIALIZATION_DISABLED,
            error_type=ValidationErrorType.INVALID_VALUE,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.FEATURE_SET,
        )

    if feature_set.online_store.connection_name != feature_set.online_store_connection_name:
        raise ValidationException(
            message=ONLINE_CONNECTION_NAME_MISMATCH,
            no_personal_data_message=ONLINE_CONNECTION_NAME_MISMATCH,
            error_type=ValidationErrorType.INVALID_VALUE,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )

    print(f"[OnlineMaterialization @ {datetime.datetime.now(datetime.timezone.utc)}] Featureset validations passed."
          f" Materializing feature data to redis resource: {feature_set.online_store.target}")

    # Constructing a record serializer function
    key_prefix, key_columns = _get_lookup_key_pattern(feature_set, materialization_version)
    timestamp_column, _ = feature_set.get_timestamp_column()

    feature_info = [(feature.name, feature.type) for feature in feature_set.features]

    def _record_serializer(row):
        key_suffix = ":".join(str(row[key_column]) for key_column in key_columns)
        record_values = [
            _type_serializers[feature_type](row[feature_name]) if row[feature_name] is not None else None
            for (feature_name, feature_type) in feature_info
        ]

        return (
            f"{key_prefix}({key_suffix})",
            row[timestamp_column],
            msgpack.packb(record_values, use_bin_type=False)
        )

    # Constructing a materialization lua script
    if feature_set.temporal_join_lookback:
        temporal_lookback_seconds = feature_set.temporal_join_lookback.to_timedelta().total_seconds()
    else:
        temporal_lookback_seconds = None

    lua_script = __LUA_SCRIPT_TEMPLATE.format(
        featureColumnNames=", ".join([f"'{feature_name}'" for (feature_name, _) in feature_info]),
        timestampColumnName=f"'{timestamp_column}'",
        timeToLiveSeconds=f"{temporal_lookback_seconds}" if temporal_lookback_seconds is not None else "nil",
        enableLogging=repr(__ENABLE_MATERIALIZATION_LOGGING).lower(),
        logChannel=f"'azureml.featurestore.{feature_set.name}.materialization.log'",
        errorChannel=f"'azureml.featurestore.{feature_set.name}.materialization.err'",
    )

    # Constructing the pyspark mapper function
    mapper = get_mapper(
        redis_resource_id=feature_set.online_store.target,
        lua_script=lua_script,
        record_serializer=_record_serializer,
        credential=AzureMLOnBehalfOfCredential(),
    )

    # Filtering and preparing the dataframe
    prepared_dataframe = _prepare_dataframe(feature_set, dataframe)

    print(f"[OnlineMaterialization @ {datetime.datetime.now(datetime.timezone.utc)}] Starting online materialization.")
    number_of_materialized_rows = prepared_dataframe.rdd.mapPartitionsWithIndex(mapper).sum()
    print(
        f"[OnlineMaterialization @ {datetime.datetime.now(datetime.timezone.utc)}]"
        f" Finished online materialization. Materialized {number_of_materialized_rows} rows"
        f" in {time.time() - online_materialization_start_time} seconds.")

    return number_of_materialized_rows
