# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class TimestampColumn(object):
    """A dataframe timestamp column
    :param name: The column name
    :type name: str, required
    :param format: timestamp format
    :type format: str, required"""

    def __init__(self, name: str, format: str = None):  # pylint: disable=redefined-builtin
        self.name = name
        self.format = format

    def __repr__(self):
        return f"TimestampColumn(Name={self.name},Format={self.format})"

    def __str__(self):
        return self.__repr__()

    def _to_dict(self):
        return {"name": self.name, "format": self.format}
