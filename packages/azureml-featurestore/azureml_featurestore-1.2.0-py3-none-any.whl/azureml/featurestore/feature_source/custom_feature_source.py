# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
from collections import OrderedDict
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Optional

import pandas as pd
from azureml.featurestore._utils._constants import ONLINE_ON_THE_FLY
from azureml.featurestore._utils._preview_method import _is_private_preview_enabled
from azureml.featurestore._utils.pandas_utils import filter_dataframe, source_process
from azureml.featurestore.contracts.datetimeoffset import DateTimeOffset
from azureml.featurestore.contracts.feature_source_type import SourceType
from azureml.featurestore.contracts.timestamp_column import TimestampColumn
from azureml.featurestore.contracts.transformation_code import SourceProcessCode

from .feature_source_base import FeatureSourceBase

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class CustomFeatureSource(FeatureSourceBase):
    """A custom feature source
    :param timestamp_column: Timestamp column for this feature set
    :type timestamp_column: TimestampColumn, required
    :param kwargs: Dictionary for custom feature source processor
    :type kwargs: Dict, required
    :param source_process_code: The source process code
    :type source_process_code: SourceProcessCode, optional
    :param source_delay: The source delay
    :type source_delay: DateTimeOffset, optional
    """

    def __init__(
        self,
        *,
        timestamp_column: TimestampColumn,
        kwargs: Dict,
        source_process_code: SourceProcessCode = None,
        source_delay: DateTimeOffset = None,
    ):
        super().__init__(timestamp_column=timestamp_column, source_delay=source_delay)
        self.kwargs = kwargs
        self.source_process_code = source_process_code
        self.type = SourceType.CUSTOM

    def _load(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, **kwargs
    ) -> "DataFrame":
        source_df = self.source_process_code._apply_spark_transform(  # pylint: disable=protected-access
            transform_function="process", start_time=start_time, end_time=end_time, **self.kwargs
        )

        return self.source_timestamp_check_filter(source_df, start_time, end_time)

    if _is_private_preview_enabled():

        def _load_pandas(self, start_time: datetime, end_time: datetime, **kwargs) -> pd.DataFrame:
            self.kwargs[ONLINE_ON_THE_FLY] = "true"
            self.kwargs.update(kwargs)
            source_df = source_process(
                feature_window_start_date_time=start_time,
                feature_window_end_date_time=end_time,
                process_code=self.source_process_code,
                **self.kwargs,
            )

            return filter_dataframe(
                df=source_df,
                feature_window_start_datetime=start_time,
                feature_window_end_datetime=end_time,
                timestamp_column=self.timestamp_column.name,
                timestamp_format=self.timestamp_column.format,
            )

    @property
    def kwargs(self):
        return self.dict

    @kwargs.setter
    def kwargs(self, value: Dict):
        self.dict = value

    def __repr__(self):
        formatted_info = ", ".join(["{}: {}".format(k, v) for k, v in self._to_dict().items()])
        return "CustomFeatureSource({})".format(formatted_info)

    def __hash__(self):
        return int(hashlib.sha256(self.__repr__().encode()).hexdigest(), 16)

    def _to_dict(self) -> Dict:
        info = OrderedDict()
        info["timestamp_column"] = self.timestamp_column.__repr__()
        info["kwargs"] = self.dict.__repr__()
        info["source_delay"] = self.source_delay.__repr__()
        info["source_process_code"] = self.source_process_code.__repr__()

        return info

    def _to_feathr_config(self, name: str = None) -> str:
        raise NotImplementedError("Custom feature source is not supported for DSL.")
