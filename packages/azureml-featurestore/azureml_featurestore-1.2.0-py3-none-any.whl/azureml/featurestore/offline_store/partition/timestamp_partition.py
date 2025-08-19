# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
from enum import Enum
from typing import TYPE_CHECKING

from azure.core import CaseInsensitiveEnumMeta  # pylint: disable=unused-import

from azureml.featurestore.contracts.partition import Partition

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class TimestampPartition(Partition):
    SPARK_DATE_FORMAT = "yyyy-MM-dd"
    SPARK_HOUR_FORMAT = "yyyy-MM-dd HH"
    PYTHON_DATE_FORMAT = "%Y-%m-%d"
    PYTHON_HOUR_FORMAT = "%Y-%m-%d %H"

    class PartitionStrategy(Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTH = 1
        DAY = 2
        HOUR = 3
        MINUTE = 4

    def __init__(self, source_column: str, partition_column: str, partition_strategy: PartitionStrategy):
        super().__init__(source_column=source_column, partition_column=partition_column)

        self.partition_strategy = partition_strategy

        if self.partition_strategy != partition_strategy.DAY:
            raise NotImplementedError(f"Partition Strategy: {self.partition_strategy} is not supported")

    def apply_partition(self, df: "DataFrame") -> "DataFrame":
        from pyspark.sql.functions import col, date_format

        if self.partition_strategy == self.PartitionStrategy.DAY:
            return df.withColumn(
                self.partition_column, date_format(col(self.source_column), TimestampPartition.SPARK_DATE_FORMAT)
            )
        if self.partition_strategy == self.PartitionStrategy.HOUR:
            return df.withColumn(
                self.partition_column, date_format(col(self.source_column), TimestampPartition.SPARK_HOUR_FORMAT)
            )

        raise NotImplementedError(f"Partition Strategy: {self.partition_strategy} is not supported")

    def get_partition(self, data: datetime) -> str:
        if self.partition_strategy == self.PartitionStrategy.DAY:
            return data.strftime(TimestampPartition.PYTHON_DATE_FORMAT)
        if self.partition_strategy == self.PartitionStrategy.HOUR:
            return data.strftime(TimestampPartition.PYTHON_HOUR_FORMAT)

        raise NotImplementedError(f"Partition Strategy: {self.partition_strategy} is not supported")
