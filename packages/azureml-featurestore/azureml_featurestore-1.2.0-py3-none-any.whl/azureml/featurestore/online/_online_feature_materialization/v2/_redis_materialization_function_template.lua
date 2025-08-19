-- ---------------------------------------------------------
-- Copyright (c) Microsoft Corporation. All rights reserved.
-- ---------------------------------------------------------
-- IMPORTANT
-- Any string declared in bracket varName format should have its value replaced by the python script.
-- timestamp_value and ttl value should be in string format.
-- USAGE:
-- EVALSHA @redis_script_sha num_keys [key [key ...]] [record_timestamp record_struct [record_timestamp record_struct ...]]


local feature_cols = {{ {featureColumnNames} }}

local time_stamp_col = {timestampColumnName}
local record_ttl_seconds = {timeToLiveSeconds}


local function emit_log(msg)
    if ({enableLogging} == false) then
        return
    end

    redis.log(redis.LOG_INFORMATION, msg)
    redis.pcall('PUBLISH', {logChannel}, msg)
end


local function emit_err(msg)
    if ({enableLogging} == false) then
        return
    end

    redis.log(redis.LOG_ERROR, msg)
    redis.pcall('PUBLISH', {errorChannel}, msg)
end


local function process_featureset_record(key, record_timestamp, record_struct)
    if (record_timestamp == nil) then
        emit_err('For key ' .. key .. ', record timestamp is nil')
        return 0
    end

    if (record_struct == nil) then
        emit_err('For key ' .. key .. ', record struct is nil')
        return 0
    end

    -- Fetch the old timestamp value
    local old_timestamp_raw = redis.pcall('HGET', key, time_stamp_col)
    local old_timestamp = tonumber(old_timestamp_raw)
    if (old_timestamp == nil) then
        emit_log('Failed to parse old timestamp value for key ' .. key .. ': ' .. cjson.encode(old_timestamp_raw))
        old_timestamp = -1
    end

    if (old_timestamp >= tonumber(record_timestamp)) then
        emit_log('Skipping featureset row ' .. key .. '. Old timestamp ' .. old_timestamp .. ' is greater than or equal to new timestamp ' .. record_timestamp)
        return 0
    end

    -- Unpack the struct
    local struct_object = cmsgpack.unpack(record_struct)

    for feature_index = 1, #feature_cols do
        local feature_name = feature_cols[feature_index]
        local feature_value = struct_object[feature_index]

        if (feature_value == nil) then
            redis.pcall('HDEL', key, feature_name)
        else
            redis.pcall('HSET', key, feature_name, feature_value)
        end
    end

    -- Store the timestamp column
    redis.pcall('HSET', key, time_stamp_col, record_timestamp)

    -- Expire the current row of data if ttl exists
    if (record_ttl_seconds ~= nil) then
        local expiry = record_timestamp + record_ttl_seconds
        redis.pcall('EXPIREAT', key, expiry)
    end

    return 1
end


local num_rows_materialized = 0
local argcursor = 1
for key_index = 1, #KEYS do
    local key = KEYS[key_index]
    if (key == nil) then
        emit_err('Key ' .. key_index .. ' is nil')
    else
        local record_timestamp = ARGV[argcursor]
        local record_struct = ARGV[argcursor + 1]

        argcursor = argcursor + 2
        num_rows_materialized = num_rows_materialized + process_featureset_record(key, record_timestamp, record_struct)
    end
end

return num_rows_materialized
