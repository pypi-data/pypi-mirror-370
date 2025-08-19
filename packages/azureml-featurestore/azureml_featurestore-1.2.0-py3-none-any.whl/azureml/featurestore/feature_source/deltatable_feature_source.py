# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime
from typing import TYPE_CHECKING

from azureml.featurestore.contracts.datetimeoffset import DateTimeOffset
from azureml.featurestore.contracts.feature_source_type import SourceType
from azureml.featurestore.contracts.timestamp_column import TimestampColumn

from .simple_feature_source import SimpleFeatureSource

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class DeltaTableFeatureSource(SimpleFeatureSource):
    """A delta table feature source
    :param path: The source data path
    :type path: str, required
    :param timestamp_column: Timestamp column for this feature set
    :type timestamp_column: TimestampColumn, optional
    :param source_delay: The source delay
    :type source_delay: DateTimeOffset, optional
    """

    def __init__(
        self,
        *,
        path: str,
        timestamp_column: TimestampColumn = None,
        source_delay: DateTimeOffset = None,
    ):
        super().__init__(path=path, timestamp_column=timestamp_column, source_delay=source_delay)
        self.type = SourceType.DELTATABLE

    def _load(self, start_time: datetime = None, end_time: datetime = None, **kwargs) -> "DataFrame":
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        source_df = spark.read.format("delta").load(self.path)

        return self.source_timestamp_check_filter(source_df, start_time, end_time)

    def __repr__(self):
        formatted_info = ", ".join(["{}: {}".format(k, v) for k, v in self._to_dict().items()])
        return "DeltaTableFeatureSource({})".format(formatted_info)
