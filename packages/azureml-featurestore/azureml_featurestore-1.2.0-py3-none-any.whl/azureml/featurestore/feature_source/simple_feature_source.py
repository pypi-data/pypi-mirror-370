# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore hdfs

import hashlib
from collections import OrderedDict
from typing import Dict

from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from jinja2 import Template

from azureml.featurestore._utils.utils import _resolve_hdfs_path_from_storage_info
from azureml.featurestore.contracts.datetimeoffset import DateTimeOffset
from azureml.featurestore.contracts.timestamp_column import TimestampColumn
from .feature_source_base import FeatureSourceBase


class SimpleFeatureSource(FeatureSourceBase):
    """A simple feature source (abstract)
    :param path: The source data path
    :type path: str, required
    :param timestamp_column: Timestamp column for this feature set
    :type timestamp_column: TimestampColumn, required
    :param source_delay: The source delay
    :type source_delay: DateTimeOffset, optional"""

    def __init__(
        self,
        *,
        path: str,
        timestamp_column: TimestampColumn = None,
        source_delay: DateTimeOffset = None,
    ):
        self.path = path
        super().__init__(timestamp_column=timestamp_column, source_delay=source_delay)

    def __hash__(self):
        return int(hashlib.sha256(self.path.encode()).hexdigest(), 16)

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        # Workaround for cross-workspace data access
        hdfs_path = _resolve_hdfs_path_from_storage_info(asset_artifact)
        self.path = hdfs_path

    def _to_dict(self) -> Dict:
        info = OrderedDict()
        info["path"] = self.path
        info["timestamp_column"] = self.timestamp_column.__repr__()
        info["source_delay"] = self.source_delay.__repr__()

        return info

    def _to_feathr_config(self, name: str = None) -> str:
        # Feathr source delay is set on observation setting, will add in later iteration
        tm = Template(
            """
"{{source_name}}": {
    location: {path: "{{source.path}}"}
    {%- if source.time_partition_pattern %}
    timePartitionPattern: "{{source.time_partition_pattern}}"
    {% endif %}
    {%- if source.timestamp_column %}
    timeWindowParameters: {
        timestampColumn: "{{source.timestamp_column.name}}"
        timestampColumnFormat: "{{timestamp_format}}"
    }
    {% endif %}
}"""
        )
        source_name = name if name else str(self.__hash__())
        timestamp_format = self.timestamp_column.format if self.timestamp_column.format else "%Y-%m-%d"
        return tm.render(source=self, source_name=source_name, timestamp_format=timestamp_format)
