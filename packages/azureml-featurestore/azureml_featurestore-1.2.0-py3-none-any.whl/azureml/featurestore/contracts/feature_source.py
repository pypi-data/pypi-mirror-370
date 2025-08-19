# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell:ignore hdfs

import json
from collections import OrderedDict
from os import PathLike
from typing import Dict, Optional, Union

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from azureml.featurestore._utils.utils import _resolve_hdfs_path_from_storage_info
from azureml.featurestore.contracts import DateTimeOffset
from azureml.featurestore.contracts.feature_source_type import SourceType
from azureml.featurestore.contracts.timestamp_column import TimestampColumn


class FeatureSource(Artifact):
    """A featurestore source
    :param type: The source type
    :type type: str, required
    :param path: The source data path
    :type path: str, required
    :param timestamp_column: Timestamp column for this feature set
    :type timestamp_column: TimestampColumn, required
    :param source_delay: The source delay
    :type source_delay: DateTimeOffset, optional"""

    def __init__(
        self,
        *,
        type: SourceType,  # pylint: disable=redefined-builtin
        path: str,
        timestamp_column: TimestampColumn,
        source_delay: Optional[DateTimeOffset] = None,
        **kwargs,
    ):
        from warnings import warn

        warn("FeatureSource class will be deprecated, please use classes under" " azureml.featurestore.feature_source")

        if type == SourceType.CUSTOM:
            msg = (
                "Custom type is not supported for FeatureSource class, please use"
                " azureml.featurestore.feature_source.CustomFeatureSource"
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
            )

        self.type = type
        self.timestamp_column = timestamp_column
        self.source_delay = source_delay

        super().__init__(
            path=path,
            **kwargs,
        )

    def __repr__(self):
        info = OrderedDict()

        info["type"] = self.type
        info["path"] = self.path
        info["timestamp_column"] = self.timestamp_column.__repr__()
        info["source_delay"] = self.source_delay.__repr__()
        formatted_info = ", ".join(["{}: {}".format(k, v) for k, v in info.items()])
        return "FeatureSource({})".format(formatted_info)

    def __str__(self):
        return self.__repr__()

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        # Workaround for cross-workspace data access
        hdfs_path = _resolve_hdfs_path_from_storage_info(asset_artifact)
        self.path = hdfs_path

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ):
        pass

    def _to_dict(self) -> Dict:
        from azureml.featurestore.schema.feature_set_schema import Source
        from marshmallow import EXCLUDE

        # pylint: disable=no-member
        return json.loads(json.dumps(Source(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)))
