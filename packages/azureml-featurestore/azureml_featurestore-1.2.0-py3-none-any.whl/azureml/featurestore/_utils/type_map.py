# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TYPE_CHECKING, Dict

from azureml.featurestore.contracts.column import ColumnType

if TYPE_CHECKING:
    from pyspark.sql.types import DataType


class TypeMap:
    @staticmethod
    def spark_to_column_type(spark_type_as_str: str) -> ColumnType:
        # TODO not all spark types are convertible
        # Current non-convertible types: array, interval, map, struct, structfield, decimal
        type_map: Dict[str, ColumnType] = {
            "null": ColumnType.NULL,
            "binary": ColumnType.BINARY,
            "string": ColumnType.STRING,
            "integer": ColumnType.INTEGER,
            "short": ColumnType.INTEGER,
            "long": ColumnType.LONG,
            "double": ColumnType.DOUBLE,
            "float": ColumnType.FLOAT,
            "boolean": ColumnType.BOOLEAN,
            "timestamp": ColumnType.DATETIME,
        }

        if not isinstance(spark_type_as_str, str) or spark_type_as_str not in type_map:
            raise ValueError(f"Spark data type {spark_type_as_str} is not supported")

        return type_map[spark_type_as_str.lower()]

    @staticmethod
    def column_type_to_spark(column_type_as_str: str) -> "DataType":
        from pyspark.sql.types import (
            BinaryType,
            BooleanType,
            DoubleType,
            FloatType,
            IntegerType,
            LongType,
            NullType,
            StringType,
            TimestampType,
        )

        type_map: Dict[str, "DataType"] = {
            "null": NullType(),
            "binary": BinaryType(),
            "string": StringType(),
            "integer": IntegerType(),
            "long": LongType(),
            "float": FloatType(),
            "double": DoubleType(),
            "boolean": BooleanType(),
            "datetime": TimestampType(),
        }

        if not isinstance(column_type_as_str, str) or column_type_as_str not in type_map:
            raise ValueError(
                "Data mapping error, can't map column type: {} to spark dataframe value type".format(column_type_as_str)
            )

        return type_map[column_type_as_str.lower()]
