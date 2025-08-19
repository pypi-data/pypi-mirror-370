# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.featurestore.contracts.column import ColumnType

# Declare any spark type that should be serialized here.
columnType_serializable_const = set([ColumnType.FLOAT, ColumnType.DOUBLE, ColumnType.BINARY])


def _get_lookup_key(featureset, row):
    prefix, suffix_column_name = _get_lookup_key_pattern(featureset, featureset.online_materialization_version)

    return _get_lookup_key_udf(prefix, suffix_column_name, row)


def _get_lookup_key_udf(prefix, suffix_column_names, row):
    suffix_parts = []

    for index_column in suffix_column_names:
        suffix_parts.append(index_column)
        suffix_parts.append(row[index_column])

    suffix = ":".join(suffix_parts)
    return f"{prefix}:{suffix}"


def _get_lookup_key_pattern(featureset, materialization_version=None):
    featureset_schema_version = 1
    if hasattr(featureset, "schema_version") and featureset.schema_version is not None:
        featureset_schema_version = featureset.schema_version

    if featureset_schema_version == 1:
        prefix = f"featurestore:{featureset.feature_store_guid}" + \
            f":featureset:{featureset.name}:version:{featureset.version}:"
        # update when feature set has online materialize prefix returned from backend
        if materialization_version:
            prefix = f"{prefix}{materialization_version}:"

        suffix_column_names = []

        for entity in featureset.entities:
            for index_column in entity.index_columns:
                suffix_column_names.append(index_column.name)

        return prefix.lower(), suffix_column_names

    if featureset_schema_version == 2:
        import hashlib
        prefix = f"featurestore:{featureset.feature_store_guid}" + \
            f":featureset:{featureset.name}:version:{featureset.version}:"
        # update when feature set has online materialize prefix returned from backend
        if materialization_version:
            prefix = f"{prefix}{materialization_version}:"

        suffix_column_names = []

        for entity in featureset.entities:
            for index_column in entity.index_columns:
                suffix_column_names.append(index_column.name)

        # MD5 is used here to generate a short, non-cryptographic key identifier for featuresets.
        # Given the small number of featuresets (< 100) in a single-tenant redis database,
        # collision risk is negligible and impact of collisions is minimal.
        # CodeQL [SM02167] Negligible collision risk.
        return hashlib.md5(prefix.lower().encode("utf-8")).hexdigest(), suffix_column_names

    raise ValueError(
        f"Unsupported feature set schema version: {featureset_schema_version}"
    )


def _get_redis_function_key_format(key_columns):
    key_cols_formatted = "{"
    for key in key_columns:
        key_cols_formatted = key_cols_formatted + "'" + key + "'"
        if not key == key_columns[-1]:
            key_cols_formatted += ","
    key_cols_formatted += "}"
    return key_cols_formatted


def _get_redis_function_value_column_name_format(value_columns):
    value_cols_formatted = "{"
    for value in value_columns:
        value_cols_formatted = value_cols_formatted + "'" + value + "'"
        if not value == value_columns[-1]:
            value_cols_formatted += ","
    value_cols_formatted += "}"
    return value_cols_formatted


def _get_serializable_column_datatype():
    return set(columnType_serializable_const)
