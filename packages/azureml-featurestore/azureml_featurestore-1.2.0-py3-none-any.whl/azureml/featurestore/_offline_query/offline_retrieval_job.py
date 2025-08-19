# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class OfflineRetrievalJob(ABC):
    def to_spark_dataframe(self) -> "DataFrame":
        pass
