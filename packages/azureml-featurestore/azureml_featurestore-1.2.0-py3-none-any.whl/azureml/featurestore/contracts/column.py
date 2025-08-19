# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class ColumnType(Enum, metaclass=CaseInsensitiveEnumMeta):
    """Represents data type for data column."""

    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    BINARY = "binary"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    NULL = "null"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value


class Column(object):
    """A dataframe column
    :param name: The column name
    :type name: str, required
    :param type: Column data type
    :type type: str, one of [string, integer, long, float, double, binary, datetime], required"""

    def __init__(self, name, type: ColumnType):  # pylint: disable=redefined-builtin
        self.name = name
        self.type = type

    def __repr__(self):
        return f"Column(Name={self.name},Type={self.type})"

    def __str__(self):
        return self.__repr__()

    def _to_dict(self):
        return {"name": self.name, "type": self.type.name}
