# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class Partition(ABC):
    def __init__(self, source_column: str, partition_column: str):
        self.source_column = source_column
        self.partition_column = partition_column

    @abstractmethod
    def apply_partition(self, df: "DataFrame") -> "DataFrame":
        pass

    @abstractmethod
    def get_partition(self, data: object) -> str:
        pass
