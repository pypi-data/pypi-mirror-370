# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin


from typing import Dict

from azureml.featurestore._utils.error_constants import (
    CUSTOM_SOURCE_VALIDATION,
    FEATURE_SET_SOURCE_VALIDATION,
    SIMPLE_SOURCE_VALIDATION,
    SOURCE_TYPE_NOT_SUPPORTED,
)
from azureml.featurestore.contracts import DateTimeOffset, SourceProcessCode, SourceType, TimestampColumn
from azureml.featurestore.feature_source.feature_source_base import FeatureSourceBase

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.core.credentials import TokenCredential


class FeatureSourceFactory:
    """A feature source factory
    :param type: The source type
    :type type: str, required
    :param timestamp_column: Timestamp column for this feature set
    :type timestamp_column: TimestampColumn, required
    :param path: The source data path
    :type path: str, optional
    :param source_delay: The source delay
    :type source_delay: DateTimeOffset, optional
    :param source_process_code: The source process code
    :type source_process_code: SourceProcessCode, optional
    :param kwargs: Dictionary for custom feature source
    :type kwargs: Dict, optional
    """

    def __init__(
        self,
        *,
        type: SourceType,
        timestamp_column: TimestampColumn = None,
        path: str = None,
        source_delay: DateTimeOffset = None,
        source_process_code: SourceProcessCode = None,
        kwargs: Dict = None,
        dict: Dict = None,
        credential: TokenCredential = None,
    ):
        kwargs = dict or kwargs
        if type != SourceType.CUSTOM:
            if not (path and not kwargs and not source_process_code):
                msg = SIMPLE_SOURCE_VALIDATION.format(type)
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
            if type == SourceType.FEATURESET and timestamp_column:
                msg = FEATURE_SET_SOURCE_VALIDATION
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        else:
            if not (kwargs and source_process_code and not path):
                msg = CUSTOM_SOURCE_VALIDATION
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )
        self.type = type
        self.path = path
        self.timestamp_column = timestamp_column
        self.source_delay = source_delay
        self.source_process_code = source_process_code
        self.kwargs = kwargs
        self.credential = credential

    def build_feature_source(self) -> FeatureSourceBase:
        if self.type == SourceType.CUSTOM:
            from azureml.featurestore.feature_source import CustomFeatureSource

            return CustomFeatureSource(
                timestamp_column=self.timestamp_column,
                kwargs=self.kwargs,
                source_process_code=self.source_process_code,
                source_delay=self.source_delay,
            )
        if self.type == SourceType.CSV:
            from azureml.featurestore.feature_source import CsvFeatureSource

            return CsvFeatureSource(
                path=self.path, timestamp_column=self.timestamp_column, source_delay=self.source_delay
            )
        if self.type == SourceType.PARQUET:
            from azureml.featurestore.feature_source import ParquetFeatureSource

            return ParquetFeatureSource(
                path=self.path, timestamp_column=self.timestamp_column, source_delay=self.source_delay
            )
        if self.type == SourceType.MLTABLE:
            from azureml.featurestore.feature_source import MlTableFeatureSource

            return MlTableFeatureSource(
                path=self.path, timestamp_column=self.timestamp_column, source_delay=self.source_delay
            )
        if self.type == SourceType.DELTATABLE:
            from azureml.featurestore.feature_source import DeltaTableFeatureSource

            return DeltaTableFeatureSource(
                path=self.path, timestamp_column=self.timestamp_column, source_delay=self.source_delay
            )
        if self.type == SourceType.FEATURESET:
            from azureml.featurestore.feature_source import FeatureSetFeatureSource

            return FeatureSetFeatureSource(path=self.path)

        raise ValueError(SOURCE_TYPE_NOT_SUPPORTED.format(self.type))
