# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-locals,too-many-statements

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from azureml.featurestore._utils._constants import TIME_TO_LIVE
from azureml.featurestore._utils.error_constants import ONLINE_CONNECTION_NAME_MISMATCH, ONLINE_MATERIALIZATION_DISABLED
from azureml.featurestore.contracts.store_connection import OnlineStoreType
from azureml.featurestore.online._redis_client_pool import _get_redis_connection_string
from azureml.featurestore.online._utils import (
    _get_lookup_key_pattern,
    _get_redis_function_key_format,
    _get_redis_function_value_column_name_format,
    _get_serializable_column_datatype,
)


def materialize_online(feature_set, dataframe_to_store, materialization_version=None):
    if not dataframe_to_store:
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
    # Do the 3 steps
    from pyspark.sql import SparkSession

    SparkSession.builder.getOrCreate()
    # Repartition the data
    # Figure out the header rows
    key_index_column = feature_set.get_index_columns()
    # Extract only the name from the column object
    key_index_column = [x.name for x in key_index_column]

    from pyspark.sql import Window
    from pyspark.sql.functions import col, current_timestamp, desc, rank, unix_timestamp

    from azure.ai.ml.identity import AzureMLOnBehalfOfCredential

    # This process is needed because it is possible that we have rows with duplicate key.
    # We will only keep the key with the latest timestamp
    # Rank each row by the key columns ordered by timestmap. Take the largest timestamp
    temporal_lookback = feature_set.temporal_join_lookback
    time_stamp, _ = feature_set.get_timestamp_column()
    win_spec = Window.partitionBy([col(x) for x in key_index_column]).orderBy(desc(time_stamp))
    dataframe_to_store = (
        dataframe_to_store.withColumn("rank", rank().over(win_spec)).select("*").where("rank = 1").drop("rank")
    )
    if temporal_lookback:
        cur_time_unix = unix_timestamp(current_timestamp())
        temporal_lookback_seconds = temporal_lookback.to_timedelta().total_seconds()
        df = dataframe_to_store.withColumn(
            TIME_TO_LIVE, temporal_lookback_seconds - (cur_time_unix - unix_timestamp(dataframe_to_store[time_stamp]))
        )
        dataframe_to_store = df.filter(df[TIME_TO_LIVE] > 0)
    # Convert timestamp to epochsecond
    dataframe_to_store = dataframe_to_store.withColumn(time_stamp, unix_timestamp(dataframe_to_store[time_stamp]))

    number_of_materialized_rows = dataframe_to_store.count()
    prefix, _ = _get_lookup_key_pattern(feature_set, materialization_version)

    # Steps to figure out which dataframe column needs to be serialized for space efficiency.
    serializable_column_datatype_set = _get_serializable_column_datatype()
    # Generate a set of the current featureset value column that should be serialized
    value_column_to_serialize_set = set()
    value_column_not_to_serialize = []
    for feature in feature_set.features:
        if feature.type in serializable_column_datatype_set:
            value_column_to_serialize_set.add(feature.name)
        else:
            value_column_not_to_serialize.append(feature.name)
    # order matter so we convert it to list
    value_column_to_serialize_set = list(value_column_to_serialize_set)

    # Get the redis connection string
    credential = AzureMLOnBehalfOfCredential()
    redis_connection_string = _get_redis_connection_string(feature_set.online_store.target, credential)
    import pkgutil

    lua_script_string = pkgutil.get_data(__name__, "_redis_materialization_function_template.lua").decode()

    # These are the placeholder variables in _redis_materialization_function_template redis script
    key_cols_lua = "keyColsFormat"
    value_cols_lua = "valueColsFormat"
    key_prefix_lua = "keyPrefixFormat"
    time_stamp_col_lua = "timestampColFormat"
    time_to_live_lua = "timeToLiveExistFormat"

    # Merge serializable value column and non serializable value column into a single list to be injected into redis.
    structured_value_columns = []
    structured_value_columns.extend(value_column_not_to_serialize)
    structured_value_columns.extend(value_column_to_serialize_set)
    # Injecting variable into redis script template
    key_cols_formatted_lua = _get_redis_function_key_format(key_index_column)
    value_cols_formatted_lua = _get_redis_function_value_column_name_format(structured_value_columns)
    key_prefix_formatted_lua = "'" + prefix + "'"
    time_stamp_col_formatted_lua = "'" + time_stamp + "'"
    time_to_live_formatted_lua = "'" + str(bool(temporal_lookback)).lower() + "'"

    lua_variable_replacement_dict = {
        key_cols_lua: key_cols_formatted_lua,
        value_cols_lua: value_cols_formatted_lua,
        key_prefix_lua: key_prefix_formatted_lua,
        time_stamp_col_lua: time_stamp_col_formatted_lua,
        time_to_live_lua: time_to_live_formatted_lua,
    }
    lua_script_string = lua_script_string.format(**lua_variable_replacement_dict)

    def saveIntoRedisViaRedisScript(rdd):
        # Format every single value to be saved via redis script
        import base64

        import msgpack
        from redis import Redis

        redis_client = Redis.from_url(redis_connection_string)
        pipe = redis_client.pipeline()
        materialize_redis_function = pipe.register_script(lua_script_string)
        for record in rdd:
            # Arglist is the list of values to be sent to redis script.
            argList = []
            # Order of operations matters here
            # Redis matches these values to the correct key via the index
            # Redis script expects the value in the format of
            # [keys1, keys2, ...keys_n, value_not_serialize1, 2 ... n, value_to_serialize1, 2, ...n, timestamp, TTL]
            for key in key_index_column:
                argList.append(str(record[key]))
            for column_not_serialize in value_column_not_to_serialize:
                argList.append(str(record[column_not_serialize]))
            for column_to_serialize in value_column_to_serialize_set:
                current_record_value = record[column_to_serialize]
                # Serialize the current value using msgpack
                packed_byte = msgpack.packb(current_record_value)  # cspell:disable-line
                encoded_str = base64.b64encode(packed_byte).decode("utf-8")
                argList.append(encoded_str)
            # Adding time_stamp and TTL must be last 2 steps
            argList.append(str(record[time_stamp]))
            if temporal_lookback:
                argList.append(str(record[TIME_TO_LIVE]))
            materialize_redis_function(keys=[0], args=argList)
        pipe.execute(raise_on_error=True)

    dataframe_to_store.rdd.foreachPartition(
        lambda x: saveIntoRedisViaRedisScript(x)  # pylint: disable=unnecessary-lambda
    )
    print("Successfully write data to online store")
    return number_of_materialized_rows
