# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore pydatetime, pyfile

import os
from datetime import datetime
from typing import List, Optional
from zipimport import zipimporter  # pylint: disable=no-name-in-module

import pandas as pd
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

from azureml.featurestore._utils._constants import CREATE_TIMESTAMP_COLUMN
from azureml.featurestore.contracts import TransformationCode


def _get_module(transformer_code: TransformationCode, transformer_class: str) -> object:
    strs = transformer_class.split(".")
    pyfile = "{}".format(strs[0])
    class_name = strs[1]

    transformer_code_local_path = transformer_code.code_local_path
    file_name = os.path.basename(transformer_code_local_path)
    namespace = os.path.splitext(file_name)[0]

    importer = zipimporter(transformer_code_local_path)
    module = importer.find_module(f"{namespace}\\{pyfile}")
    if module:
        module = importer.load_module(f"{namespace}\\{pyfile}")
    else:
        module = importer.load_module(f"{namespace}/{pyfile}")

    if module is None:
        msg = f"couldn't get module with ns={namespace} file={pyfile}"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.FEATURE_SET,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )

    _class = getattr(module, class_name)

    return _class


def infer_event_timestamp_range(observation_data: pd.DataFrame, timestamp_column: str):
    if observation_data[timestamp_column].empty:
        raise ValueError("Observation data timestamp column is empty")

    min_time, max_time = observation_data[timestamp_column].agg(["min", "max"])
    if isinstance(min_time, str):
        min_time = pd.to_datetime(min_time, utc=True).to_pydatetime()
        max_time = pd.to_datetime(max_time, utc=True).to_pydatetime()
    event_timestamp_range = (min_time, max_time)

    return event_timestamp_range


def source_process(
    feature_window_start_date_time: datetime,
    feature_window_end_date_time: datetime,
    process_code: TransformationCode,
    **kwargs,
) -> pd.DataFrame:
    _class = _get_module(process_code, process_code.process_class)
    processor = _class(**kwargs)
    df = processor.process(feature_window_start_date_time, feature_window_end_date_time, **kwargs)
    return df


def feature_transform(df: pd.DataFrame, transformer_code: TransformationCode, **kwargs) -> pd.DataFrame:
    _class = _get_module(transformer_code, transformer_code.transformer_class)
    transformer = _class()
    df = transformer.transform(df, **kwargs)
    return df


def filter_dataframe(
    df: pd.DataFrame,
    *,
    feature_window_start_datetime: datetime,
    feature_window_end_datetime: datetime,
    timestamp_column: str,
    timestamp_format: Optional[str] = None,
    index_columns: Optional[List[str]] = None,
    features: Optional[List[str]] = None,
) -> pd.DataFrame:
    # cspell:disable-next-line
    from pandas.core.dtypes.common import is_datetime64_any_dtype

    if timestamp_column not in df.columns:
        msg = "Timestamp column {} is not found."
        raise ValidationException(
            message=msg.format(timestamp_column),
            no_personal_data_message=msg,
            target=ErrorTarget.FEATURE_SET,
            error_category=ErrorCategory.USER_ERROR,
        )

    # cspell:disable-next-line
    if not is_datetime64_any_dtype(df[timestamp_column]):
        df[timestamp_column] = pd.to_datetime(
            df[timestamp_column], format=timestamp_format, infer_datetime_format=True, utc=True
        )

    # filter the dataframe to the given feature window and remove intermediate rows from source lookback (if any)
    if feature_window_start_datetime:
        df = df.query("{0} >= '{1}'".format(timestamp_column, pd.to_datetime(feature_window_start_datetime, utc=True)))

    if feature_window_end_datetime:
        df = df.query("{0} < '{1}'".format(timestamp_column, pd.to_datetime(feature_window_end_datetime, utc=True)))

    if index_columns or features:
        columns = []
        columns += index_columns
        if CREATE_TIMESTAMP_COLUMN in df.columns:
            columns.append(CREATE_TIMESTAMP_COLUMN)
        if timestamp_column:
            columns.append(timestamp_column)
        columns += features
        df = df[columns]

    return df
