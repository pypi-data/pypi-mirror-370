# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from datetime import datetime
from pathlib import PurePath
from typing import TYPE_CHECKING, Optional

from azure.ai.ml._utils.utils import dump_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml.operations import DatastoreOperations
from marshmallow import EXCLUDE

from azureml.featurestore._utils.utils import PathType, _download_file, _parse_path_format, copy_rename_and_zip
from azureml.featurestore.contracts.feature_transformation import FeatureTransformation

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class TransformationCode(FeatureTransformation):
    """Feature transformation code representation
    :param path: The source data path
    :type path: str, required
    :param transformer_class: The transformer module name and class name
    :type transformer_class: str, required
    """

    def __init__(self, *, path: str, transformer_class: str, **kwargs):  # pylint: disable=unused-argument
        self.path = path
        self.transformer_class = transformer_class
        self.__code_local_path = None

    @property
    def code_local_path(self):
        return self.__code_local_path

    def __repr__(self):
        yaml_serialized = self._to_dict()
        return dump_yaml(yaml_serialized, default_flow_style=False)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, obj):
        return (
            isinstance(obj, TransformationCode)
            and obj.path == self.path
            and obj.transformer_class == self.transformer_class
        )

    def _to_dict(self):
        from ..schema.feature_set_schema import TransformationCodeSchema

        return TransformationCodeSchema(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member

    def _apply_spark_transform(
        self,
        transform_function: str,
        start_time: datetime = None,
        end_time: datetime = None,
        df: "DataFrame" = None,
        **kwargs,
    ) -> "DataFrame":
        import importlib

        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()

        if not self.__code_local_path:
            self._patch_zip()
        strs = self.transformer_class.split(".")
        pyfile = "{}".format(strs[0])  # cspell:ignore pyfile
        class_name = strs[1]

        # Transformer code path is a zip with namespace
        spark.sparkContext.addPyFile(self.__code_local_path)

        file_name = os.path.basename(self.__code_local_path)
        namespace = os.path.splitext(file_name)[0]
        module = importlib.import_module(name=f"{namespace}.{pyfile}")  # cspell:ignore pyfile
        _class = getattr(module, class_name)

        transformer = _class(**kwargs) if not df else _class()
        func = getattr(transformer, transform_function)

        if df:
            df = func(df)
        else:
            df = func(start_time, end_time, **kwargs)

        return df

    def _patch_zip(
        self, spec_folder_path: Optional[str] = None, datastore_operations: DatastoreOperations = None
    ) -> str:
        if spec_folder_path:
            code_path = self.path
            code_path_type, code_path = _parse_path_format(code_path)

            if code_path_type == PathType.cloud:
                msg = "Transformation code must be relative to spec_folder_path {}. Found: {}"
                raise ValidationException(
                    message=msg.format(spec_folder_path, code_path),
                    no_personal_data_message="Transformation code must be relative to spec_folder_path",
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.GENERAL,
                )

            code_path = str(PurePath(spec_folder_path, code_path))
        else:
            code_path = self.path

        path_type, code_path = _parse_path_format(code_path)
        if path_type != PathType.local:
            code_path = _download_file(path=code_path, path_type=path_type, datastore_operations=datastore_operations)

        # Put code in a uuid() folder and zip so that sc can import script without collision
        self.__code_local_path = copy_rename_and_zip(code_path)

        return self.__code_local_path


class SourceProcessCode(TransformationCode):
    """Source process code representation
    :param path: The source data path
    :type path: str, required
    :param process_class: The source process module name and class name
    :type process_class: str, required
    """

    def __init__(self, *, path: str, process_class: str):
        super().__init__(path=path, transformer_class=process_class)

    @property
    def process_class(self):
        return self.transformer_class

    @process_class.setter
    def process_class(self, value):
        self.transformer_class = value

    def __repr__(self):
        return f"SourceProcessCode(Path={self.path},ProcessClass={self.transformer_class})"

    def _to_dict(self):
        return {"path": self.path, "process_class": self.transformer_class}
