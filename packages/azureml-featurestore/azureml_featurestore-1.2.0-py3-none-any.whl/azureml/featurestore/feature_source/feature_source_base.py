# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from azureml.featurestore.contracts.datetimeoffset import DateTimeOffset
from azureml.featurestore.contracts.timestamp_column import TimestampColumn

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class FeatureSourceBase(ABC):
    """A featurestore source base class
    :param timestamp_column: Timestamp column for this feature set
    :type timestamp_column: TimestampColumn, required
    :param source_delay: The source delay
    :type source_delay: DateTimeOffset, optional"""

    def __init__(
        self, *, timestamp_column: TimestampColumn, source_delay: DateTimeOffset = None, **kwargs
    ):  # pylint: disable=unused-argument
        self.timestamp_column = timestamp_column
        self.source_delay = source_delay
        self.type = None

    @abstractmethod
    def _load(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, **kwargs
    ) -> "DataFrame":
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def _to_feathr_config(self, name: str = None) -> str:
        pass

    def source_timestamp_check_filter(
        self,
        df: "DataFrame",
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> "DataFrame":
        from azureml.featurestore._utils.error_constants import SCHEMA_ERROR_NO_TIMESTAMP_COLUMN
        from pyspark.sql.functions import col, lit, to_timestamp
        from pyspark.sql.types import TimestampType

        if not self.timestamp_column:
            return df

        if self.timestamp_column.name in df.columns:
            if df.schema[self.timestamp_column.name].dataType != TimestampType():
                if self.timestamp_column.format:
                    df = df.withColumn(
                        self.timestamp_column.name,
                        to_timestamp(self.timestamp_column.name, self.timestamp_column.format),
                    )
                else:
                    df = df.withColumn(self.timestamp_column.name, to_timestamp(self.timestamp_column.name))
        else:
            raise ValidationException(
                message=SCHEMA_ERROR_NO_TIMESTAMP_COLUMN.format(self.timestamp_column.name),
                no_personal_data_message=SCHEMA_ERROR_NO_TIMESTAMP_COLUMN,
                error_type=ValidationErrorType.MISSING_FIELD,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

        if start_time:
            df = df.filter(col(self.timestamp_column.name) >= to_timestamp(lit(start_time)))

        if end_time:
            df = df.filter(col(self.timestamp_column.name) < to_timestamp(lit(end_time)))

        return df

    def __str__(self):
        return self.__repr__()
