# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,unused-argument,protected-access,logging-fstring-interpolation,no-member

import hashlib
import os
from datetime import datetime, timedelta
from os import PathLike
from pathlib import Path, PurePath
from typing import IO, TYPE_CHECKING, Dict, List, Optional, Union
from warnings import warn

import pandas as pd
import yaml
from azureml.featurestore._utils._constants import (
    COL_OBSERVATION_ENTITY_TIMESTAMP,
    DEPRECATED_FEATURE_END_NAME,
    DEPRECATED_FEATURE_START_NAME,
    DSL_QUERY_MODE_KEY,
    FEATURE_SET_SPEC_YAML_FILENAME,
    FEATURE_SET_SPEC_YAML_FILENAME_FALLBACK,
    ONLINE_ON_THE_FLY,
    PACKAGE_NAME,
    QUERY_MODE_DSL,
    QUERY_MODE_DSL_SHIM,
)
from azureml.featurestore._utils._preview_method import _is_private_preview_enabled
from azureml.featurestore._utils.dsl_utils import _to_feathr_fset_config, _to_feathr_join_config
from azureml.featurestore._utils.error_constants import (
    DESTINATION_NOT_LOCAL_PATH,
    EMPTY_FEATURE_MESSAGE,
    FEATURE_NAME_NOT_FOUND,
    FEATURE_NAME_NOT_FOUND_DSL,
    FEATURE_NAME_NOT_STRING,
    FILE_ALREADY_EXIST,
    INVALID_DERIVED_FEATURE_SET,
    MISSING_FEATURE_SOURCE,
    MISSING_INDEX_COLUMN,
    MISSING_TIMESTAMP_COLUMN,
    PATH_NOT_EXISTING_FOLDER,
    SCHEMA_ERROR_NO_INDEX_COLUMN,
    SCHEMA_ERROR_WRONG_DATA_TYPE,
    UNSUPPORTED_QUERY_MODE,
)
from azureml.featurestore._utils.pandas_utils import feature_transform, filter_dataframe
from azureml.featurestore._utils.utils import PathType, _build_logger, _parse_path_format, _process_path
from azureml.featurestore.contracts import Column, DateTimeOffset, FeatureSource, SourceType, TransformationCode
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.contracts.feature_transformation import FeatureTransformation
from azureml.featurestore.contracts.transformation_type import TransformationType
from azureml.featurestore.feature_source import CustomFeatureSource, FeatureSetFeatureSource
from azureml.featurestore.feature_source.feature_source_base import FeatureSourceBase
from azureml.featurestore.schema.feature_set_schema import FeatureSetSpecSchema
from azureml.featurestore.transformation.transformation_expression_collection import TransformationExpressionCollection
from jinja2 import Template
from marshmallow import EXCLUDE, ValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._telemetry.activity import ActivityType, monitor_with_activity
from azure.ai.ml._utils.utils import dump_yaml, dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationErrorType, ValidationException
from azure.ai.ml.operations import DatastoreOperations
from azure.core.credentials import TokenCredential

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

ops_logger = _build_logger(__name__)


class FeatureSetSpec:
    """Represents a feature set specification.

    :param source: The underlying source data for this feature set
    :type source: FeatureSourceBase
    :param features: Features in this feature set
    :type features: List[Feature]
    :param index_columns: Index columns for this feature set, required for non-featureset source
    :type index_columns: List[DataColumn], optional
    :param feature_transformation_code: Transformation logic to be applied to the feature set, deprecated
    :type feature_transformation_code: Code, optional
    :param feature_transformation: Transformation logic to be applied to the feature set, can be UDF or DSL
    :type feature_transformation: FeatureTransformation, optional
    :param source_lookback: A datetime representing window of source data fed to the feature transformation function.
                            This is needed for e.g. to calculate 30 day aggregate
    :type source_lookback: Datetime, optional
    :param temporal_join_lookback:  A datetime representing tolerance of the temporal join when the
                                    event data is joined with feature set
    :type temporal_join_lookback: Datetime, optional
    """

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSetSpec.Init", ActivityType.PUBLICAPI)
    def __init__(
        self,
        *,
        source: Union[FeatureSourceBase, FeatureSource],
        index_columns: Optional[List[Column]] = None,
        features: Optional[List[Feature]] = None,
        feature_transformation_code: Optional[TransformationCode] = None,
        feature_transformation: Optional[FeatureTransformation] = None,
        source_lookback: Optional[DateTimeOffset] = None,
        temporal_join_lookback: Optional[DateTimeOffset] = None,
        base_path=None,
        schema_version=1,
        **kwargs,
    ):
        """Initialize a feature set specification.

        :param source: The underlying source data for this feature set
        :type source: Union[FeatureSourceBase, FeatureSource]
        :param features: Features in this feature set
        :type features: List[Feature]
        :param index_columns: Index columns for this feature set
        :type index_columns: List[Column]
        :param feature_transformation_code: Transformation logic to be applied to the feature set, deprecated
        :type feature_transformation_code: Code, optional
        :param feature_transformation: Transformation logic to be applied to the feature set, can be UDF or DSL
        :type feature_transformation: FeatureTransformation, optional
        :param source_lookback: A datetime representing window of source data fed to the feature transformation function
                                This is needed for e.g. to calculate 30 day aggregate.
        :type source_lookback: Datetime, optional
        :param temporal_join_lookback:  A datetime representing tolerance of the temporal join when the
                                        event data is joined with feature set
        :type temporal_join_lookback: Datetime, optional
        """

        self._base_path = base_path
        self.schema_version = schema_version
        if isinstance(source, FeatureSource):
            from azureml.featurestore.feature_source.feature_source_factory import FeatureSourceFactory

            warn(
                "FeatureSource class is deprecated, and will removed in a future release."
                "Please use classes under azureml.featurestore.feature_source"
            )
            credential = kwargs.pop("credential", None)
            feature_source_factory = FeatureSourceFactory(
                type=source.type,
                timestamp_column=source.timestamp_column,
                path=source.path,
                source_delay=source.source_delay,
                credential=credential,
            )
            self.source = feature_source_factory.build_feature_source()
        else:
            self.source = source
        self.features = features or []
        self.index_columns = index_columns or []
        if feature_transformation_code:
            warn(
                "feature_transformation_code is deprecated, and will be removed in a future release."
                "Please use feature_transformation instead.",
                DeprecationWarning,
            )
        self.feature_transformation_code = feature_transformation_code
        self.feature_transformation = feature_transformation if feature_transformation else feature_transformation_code
        self.source_lookback = source_lookback
        self.temporal_join_lookback = temporal_join_lookback
        self._spec_folder_path = None

        # Generated name and version for offline join
        self.__name = hashlib.sha256(self.__str__().encode()).hexdigest()
        self.__version = "1"

        if not self.source:
            raise ValidationException(
                message=MISSING_FEATURE_SOURCE,
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=MISSING_FEATURE_SOURCE,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        if self.source.type != SourceType.FEATURESET and len(self.index_columns) == 0:
            raise ValidationException(
                message=MISSING_INDEX_COLUMN,
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=MISSING_INDEX_COLUMN,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
        if self.source.type == SourceType.FEATURESET and len(self.index_columns) > 0:
            raise ValidationException(
                message=INVALID_DERIVED_FEATURE_SET,
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=INVALID_DERIVED_FEATURE_SET,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if (
            isinstance(feature_transformation, TransformationExpressionCollection)
            and self.feature_transformation.transformation_expressions
        ):
            dsl_output_lookup = {index_column.name for index_column in index_columns}
            dsl_output_lookup.update(
                {
                    transformation_expression.feature_name
                    for transformation_expression in self.feature_transformation.transformation_expressions
                }
            )
            dsl_output_lookup.update(self.get_timestamp_column()[0])
            feature_look_up = {feature.name for feature in features}
            if not feature_look_up.issubset(dsl_output_lookup):
                raise ValidationException(
                    message=FEATURE_NAME_NOT_FOUND_DSL.format(feature_look_up.difference(dsl_output_lookup)),
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message=FEATURE_NAME_NOT_FOUND_DSL,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

    def __repr__(self):
        yaml_serialized = self._to_dict()
        return dump_yaml(yaml_serialized, default_flow_style=False)

    def __str__(self):
        return self.__repr__()

    def get_feature(self, name: str):
        if not isinstance(name, str):
            raise ValidationException(
                message=FEATURE_NAME_NOT_STRING.format(type(name)),
                no_personal_data_message=FEATURE_NAME_NOT_STRING,
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

        for feature in self.features:
            if feature.name == name:
                feature.feature_set_reference = self
                return feature

        raise ValidationException(
            message=FEATURE_NAME_NOT_FOUND.format(name),
            no_personal_data_message=FEATURE_NAME_NOT_FOUND,
            error_type=ValidationErrorType.INVALID_VALUE,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )

    @property
    def name(self):
        return self.__name

    @property
    def version(self):
        return self.__version

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSetSpec.Dump", ActivityType.PUBLICAPI)
    def dump(self, dest: Union[str, PathLike], overwrite: bool = False, **kwargs) -> None: # pylint: disable=too-many-statements
        """Dump the feature set spec into a file in yaml format. Destination can be a folder or a spec file path.

        If the destination is a folder path, the spec file name is assumed as FeatureSetSpec.yaml.

        If the destination is a yaml file path, the spec file name will be the same as the file name provided.

        If there is a transformation code path specified, it will be copied to the destination folder.

        If there is a source transformation code path specified, it will be copied to destination folder, and
        an exception is raised if code folder exists.

        An exception will be thrown if the destination already exists if overwrite == False
        :param dest: The folder path destination to receive this spec.
        :type dest: Union[PathLike, str]
        :param overwrite: Whether to overwrite the destination folder
        :type overwrite: bool, default is False
        """
        import shutil

        path_type, _ = _parse_path_format(dest)
        if path_type != PathType.local:
            raise ValidationException(
                message=DESTINATION_NOT_LOCAL_PATH.format(dest),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=DESTINATION_NOT_LOCAL_PATH,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        dest_folder_path = None
        dest_spec_path = None
        if str(dest).endswith(".yml") or str(dest).endswith(".yaml"):
            dest_folder_path = os.path.dirname(dest)
            dest_spec_path = os.path.join(dest_folder_path, FEATURE_SET_SPEC_YAML_FILENAME)
            if str(os.path.basename(dest)).lower() is not FEATURE_SET_SPEC_YAML_FILENAME.lower():
                warn(f"{dest} will be renamed to {dest_spec_path}")
        else:
            dest_folder_path = dest
            dest_spec_path = os.path.join(dest, FEATURE_SET_SPEC_YAML_FILENAME)

        os.makedirs(dest_folder_path, exist_ok=True)
        if not overwrite and os.path.isfile(dest_spec_path):
            raise FileExistsError(FILE_ALREADY_EXIST.format(dest_spec_path))

        original_feature_transformation_path = None
        if isinstance(self.feature_transformation, TransformationCode):
            relative_path = self.feature_transformation.path
            src_path = relative_path
            if self._spec_folder_path:
                src_path = str(PurePath(self._spec_folder_path, relative_path))
            shutil.copytree(
                src=src_path,
                dst=str(PurePath(dest_folder_path, os.path.basename(relative_path))),
                dirs_exist_ok=True,
            )
            original_feature_transformation_path = self.feature_transformation.path
            self.feature_transformation.path = os.path.join("./", os.path.basename(relative_path))

        original_source_process_code_path = None
        if isinstance(self.source, CustomFeatureSource) and self.source.source_process_code:
            relative_path = self.source.source_process_code.path
            src_path = relative_path
            if self._spec_folder_path:
                src_path = str(PurePath(self._spec_folder_path, relative_path))
            shutil.copytree(
                src=src_path,
                dst=str(PurePath(dest_folder_path, os.path.basename(relative_path))),
                dirs_exist_ok=True,  # True as user can specify the same file for transformation and source process code
            )
            original_source_process_code_path = self.source.source_process_code.path
            self.source.source_process_code.path = os.path.join("./", os.path.basename(relative_path))

        if isinstance(self.source, FeatureSetFeatureSource):
            original_index_columns = self.index_columns
            self.index_columns = None
            original_timestamp_column = self.source.timestamp_column
            self.source.timestamp_column = None
            original_source_delay = self.source.source_delay
            self.source.source_delay = None

        yaml_serialized = self._to_dict()

        dump_yaml_to_file(dest_spec_path, yaml_serialized, default_flow_style=False, **kwargs)

        if isinstance(self.feature_transformation, TransformationCode):
            self.feature_transformation.path = original_feature_transformation_path

        if isinstance(self.source, CustomFeatureSource) and self.source.source_process_code:
            self.source.source_process_code.path = original_source_process_code_path

        if isinstance(self.source, FeatureSetFeatureSource):
            self.index_columns = original_index_columns
            self.source.timestamp_column = original_timestamp_column
            self.source.source_delay = original_source_delay

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return FeatureSetSpecSchema(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @staticmethod
    def _load(config, config_file):
        context = {
            BASE_PATH_CONTEXT_KEY: Path(config_file).parent,
        }

        try:
            config = FeatureSetSpecSchema(context=context).load(config)
        except ValidationError as ex:
            raise ValueError(ex.messages) from ex

        return config

    def _to_feathr_config(self, type: str) -> str:  # pylint: disable=redefined-builtin
        from azureml.featurestore._utils.dsl_utils import _to_feathr_anchor_config, _to_feathr_source_config

        join_keys = [index_column.name for index_column in self.index_columns]
        anchor_string = _to_feathr_anchor_config(feature_set_or_spec=self, join_keys=join_keys)
        source_string = _to_feathr_source_config(feature_set_or_spec=self)

        return anchor_string if type == "anchor" else source_string

    @classmethod
    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSetSpec.FromConfig", ActivityType.PUBLICAPI)
    def from_config(
        cls,
        spec_path: Union[str, PathLike],
        datastore_operations: Optional[DatastoreOperations] = None,
        credential: Optional[TokenCredential] = None,
    ) -> "FeatureSetSpec":
        """Load a feature set spec from yaml config. Spec path must be a folder path, the spec file name is assumed as
         FeatureSetSpec.yaml
        :param spec_path: The path to fetch this spec.
        :type spec_path: Union[str, PathLike]
        :param credential: User credential to initialize the spec.
        :type credential: Optional[TokenCredential]
        """
        try:
            local_spec_path = None
            path = _process_path(path=spec_path, datastore_operations=datastore_operations)

            if (str(path).endswith(".yml") or str(path).endswith(".yaml")) and os.path.isfile(path):
                local_spec_path = path
                spec_folder_path = os.path.dirname(local_spec_path)
            else:
                spec_folder_path = path
                local_spec_path = os.path.join(spec_folder_path, FEATURE_SET_SPEC_YAML_FILENAME)

            if not os.path.isdir(spec_folder_path):
                raise ValidationException(
                    message=PATH_NOT_EXISTING_FOLDER.format(spec_path),
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message=PATH_NOT_EXISTING_FOLDER,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

            try:
                with open(local_spec_path) as f:
                    cfg = yaml.safe_load(f)
            except FileNotFoundError:
                # Fall back to previous naming format
                local_spec_path = os.path.join(spec_folder_path, FEATURE_SET_SPEC_YAML_FILENAME_FALLBACK)
                with open(local_spec_path) as f:
                    cfg = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                raise ValueError(str(ex)) from ex

            spec = FeatureSetSpec._load(cfg, local_spec_path)
            if spec.feature_transformation and isinstance(spec.feature_transformation, TransformationCode):
                spec.feature_transformation._patch_zip(spec_folder_path, datastore_operations)

            if isinstance(spec.source, CustomFeatureSource):
                spec.source.source_process_code._patch_zip(spec_folder_path, datastore_operations)
            if isinstance(spec.source, FeatureSetFeatureSource):
                spec.source._initialize(credential=credential)
                spec.index_columns = spec.source.feature_set.get_index_columns()

            spec._spec_folder_path = spec_folder_path

            return spec
        except ValidationError as ve:
            raise ValueError(
                f"Feature set yaml config validation error: field_name: {ve.field_name}, errors: {ve.messages}"
            )
        except Exception as ex:  # pylint: disable=broad-except
            ops_logger.package_logger.error(f"{PACKAGE_NAME}->FeatureSetSpec.FromConfig, {type(ex).__name__}: {ex}")
            log_and_raise_error(error=ex, debug=True)

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSetSpec.ToSparkDataframe", ActivityType.PUBLICAPI)
    def to_spark_dataframe(
        self,
        *,
        feature_window_start_date_time: Optional[datetime] = None,
        feature_window_end_date_time: Optional[datetime] = None,
        features: Optional[List[str]] = None,
        dedup: bool = False,  # cspell: ignore dedup
        **kwargs,
    ):
        """Display a feature set in a spark dataframe format, after performing necessary transformation
        :param feature_window_start_date_time: The start data time of feature window
        :type feature_window_start_date_time: datetime
        :param feature_window_end_date_time: The end data time of feature window
        :type feature_window_end_date_time: datetime
        :param features: List of feature names to show
        :type features: List[str]
        :return: feature set dataframe
        :rtype: DataFrame
        """
        feature_window_start_date_time = feature_window_start_date_time or kwargs.pop(
            DEPRECATED_FEATURE_START_NAME, None
        )
        feature_window_end_date_time = feature_window_end_date_time or kwargs.pop(DEPRECATED_FEATURE_END_NAME, None)
        query_mode = kwargs.get(DSL_QUERY_MODE_KEY, QUERY_MODE_DSL_SHIM)

        try:
            from azureml.featurestore._utils.spark_utils import _deduplicate_dataframe, _filter_dataframe
            from pyspark.sql import SparkSession

            # check spark session
            try:
                spark = SparkSession.builder.getOrCreate()  # pylint: disable=unused-variable
            except Exception:
                raise RuntimeError("Fail to get spark session, please check if spark environment is set up.")

            timestamp_column, _ = self.get_timestamp_column()
            index_columns = [i.name for i in self.get_index_columns()]
            source_start_date_time = feature_window_start_date_time

            if isinstance(self.feature_transformation, TransformationExpressionCollection):
                if query_mode == QUERY_MODE_DSL:
                    warn("query mode: dsl is deprecated, and will be removed in a future release." "Please use dsl2")
                    df = self._to_spark_dataframe_dsl(
                        feature_window_start_date_time=feature_window_start_date_time,
                        feature_window_end_date_time=feature_window_end_date_time,
                        **kwargs,
                    )
                elif query_mode == QUERY_MODE_DSL_SHIM:
                    df = self._to_spark_dataframe_dsl_shim(
                        feature_window_start_date_time=feature_window_start_date_time,
                        feature_window_end_date_time=feature_window_end_date_time,
                        **kwargs,
                    )
                else:
                    raise ValidationException(
                        message=UNSUPPORTED_QUERY_MODE.format(query_mode),
                        target=ErrorTarget.FEATURE_SET,
                        no_personal_data_message=UNSUPPORTED_QUERY_MODE.format(query_mode),
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )
            else:
                # UDF transform
                # apply source lookback, if source lookback is not provided,
                # assume data does not use aggregation outside the time window
                if self.source_lookback and feature_window_start_date_time:
                    source_start_date_time = feature_window_start_date_time - self.source_lookback.to_timedelta()

                df = self.source._load(
                    start_time=source_start_date_time, end_time=feature_window_end_date_time, **kwargs
                )

                # transform
                if isinstance(self.feature_transformation, TransformationCode):
                    df = self.feature_transformation._apply_spark_transform(transform_function="transform", df=df)

            if "schema_validation" not in kwargs or kwargs["schema_validation"] is not False:
                # data schema check
                self.__validate_schema(df)

                if not features or len(features) == 0:
                    features = [f.name for f in self.features]

                df = _filter_dataframe(
                    df=df,
                    feature_window_start_date_time=feature_window_start_date_time,
                    feature_window_end_date_time=feature_window_end_date_time,
                    index_columns=index_columns,
                    timestamp_column=timestamp_column,
                    features=features,
                )

            if dedup:  # cspell: ignore dedup
                distinct_df, has_dup = _deduplicate_dataframe(
                    df=df, join_keys=index_columns, timestamp_column=timestamp_column
                )
                if has_dup:
                    total_count = df.count()
                    print(
                        "There are multiple rows sharing the same join keys and event timestamp, source data has"
                        f" {total_count} rows, dropped {total_count - distinct_df.count()} duplicated rows"
                    )
                df = distinct_df

            return df
        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, MlException):
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureSetSpec.ToSparkDataframe, {type(ex).__name__}:"
                    f" {ex.no_personal_data_message}"
                )
            else:
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureSetSpec.ToSparkDataframe, {type(ex).__name__}: {ex}"
                )

            log_and_raise_error(error=ex, debug=True)

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->DslLoadSourceDataframe", ActivityType.INTERNALCALL)
    def _load_source_dataframe_dsl(
        self,
        *,
        feature_window_start_date_time: Optional[datetime] = None,
        feature_window_end_date_time: Optional[datetime] = None,
        **kwargs,
    ):
        from pyspark.sql.functions import unix_timestamp

        timestamp_column, _ = self.get_timestamp_column()
        source_start_date_time = feature_window_start_date_time

        if feature_window_start_date_time:
            if self.source_lookback:
                source_start_date_time = feature_window_start_date_time - self.source_lookback.to_timedelta()
            elif isinstance(self.feature_transformation, TransformationExpressionCollection):
                window_minutes_max = max(
                    [feature.window.to_minutes() for feature in self.feature_transformation.transformation_expressions]
                )
                source_start_date_time = feature_window_start_date_time - timedelta(minutes=window_minutes_max)

        df = self.source._load(start_time=source_start_date_time, end_time=feature_window_end_date_time, **kwargs)

        # make a new timestamp column of long type, number of seconds
        df = df.withColumn(COL_OBSERVATION_ENTITY_TIMESTAMP, unix_timestamp(timestamp_column))

        return df

    def _to_spark_dataframe_dsl(
        self,
        *,
        feature_window_start_date_time: Optional[datetime] = None,
        feature_window_end_date_time: Optional[datetime] = None,
        **kwargs,
    ):
        from pyspark.sql import DataFrame
        from pyspark.sql.session import SparkSession

        spark = SparkSession.builder.getOrCreate()
        sc = spark.sparkContext

        start_time = feature_window_start_date_time if feature_window_start_date_time else datetime(1970, 1, 1)
        end_time = feature_window_end_date_time if feature_window_end_date_time else datetime.utcnow()
        time_format = self.source.timestamp_column.format if self.source.timestamp_column.format else "%Y-%m-%d"

        feathr_config_string = _to_feathr_fset_config(feature_sets=[self])

        feathr_ops_tm = Template(
            """
    operational: {
    name: generateWithDefaultParams
    endTime: {{end_time}}
    endTimeFormat: "yyyy-MM-dd"
    resolution: DAILY
    output: []
    }
    features: [{{','.join(feature_names)}}]
    """
        )
        feature_names = [feature.feature_name for feature in self.feature_transformation.transformation_expressions]
        feathr_ops_string = feathr_ops_tm.render(  # pylint: disable=unused-variable
            feature_names=feature_names, end_time=str(end_time)
        )

        join_keys = [index_column.name for index_column in self.index_columns]
        feathr_join_string = _to_feathr_join_config(
            timestamp_col_name=self.source.timestamp_column.name,
            timestamp_col_format=time_format,
            feature_names=feature_names,
            join_keys=join_keys,
            start_time=str(start_time),
            end_time=str(end_time),
        )

        source_df = self.source._load(start_time=start_time, end_time=end_time, **kwargs)

        dsl = sc._jvm.entrypoint.FeatureJobEntryPoint()
        # cspell:disable-next-line
        jdf = dsl.joinFeatures(spark._jsparkSession, feathr_join_string, feathr_config_string, source_df._jdf)

        return DataFrame(jdf, spark)

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->DslShimToSparkDataframe", ActivityType.PUBLICAPI)
    def _to_spark_dataframe_dsl_shim(
        self,
        *,
        feature_window_start_date_time: Optional[datetime] = None,
        feature_window_end_date_time: Optional[datetime] = None,
        **kwargs,
    ):
        from azureml.featurestore._utils.dsl_utils import _to_feathr_shim_config
        from azureml.featurestore._utils.spark_utils import _dsl_shim_transform

        source_df = self._load_source_dataframe_dsl(
            feature_window_start_date_time=feature_window_start_date_time,
            feature_window_end_date_time=feature_window_end_date_time,
            **kwargs,
        )

        scala_features_config = _to_feathr_shim_config(source_df, self, is_materialized=False)

        return _dsl_shim_transform(scala_features_config)

    def _transformation_type(self) -> TransformationType:
        if self.feature_transformation and isinstance(self.feature_transformation, TransformationExpressionCollection):
            return TransformationType.DSL
        return TransformationType.UDF

    def get_index_columns(self):
        return self.index_columns

    def get_timestamp_column(self):
        if not self.source.timestamp_column:
            # TODO: Suppport Non-timeseries data
            raise ValidationException(
                message=MISSING_TIMESTAMP_COLUMN.format(self.name),
                no_personal_data_message=MISSING_TIMESTAMP_COLUMN,
                error_type=ValidationErrorType.MISSING_FIELD,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

        return self.source.timestamp_column.name, self.source.timestamp_column.format

    if _is_private_preview_enabled():

        @monitor_with_activity(
            ops_logger, f"{PACKAGE_NAME}->FeatureSetSpec.ToPandasDataframe", ActivityType.INTERNALCALL
        )
        def _to_pandas_dataframe(
            self,
            *,
            feature_window_start_date_time: Optional[datetime] = None,
            feature_window_end_date_time: Optional[datetime] = None,
            features: Optional[List[str]] = None,
            **kwargs,
        ) -> pd.DataFrame:
            # This is an internal method to get pandas dataframe from feature set spec. It is only intended for use for
            # online on-the-fly feature calculation and join.
            if self.source.type != SourceType.CUSTOM:
                msg = "On the fly feature sets only supports CUSTOM source type, found {}"
                raise ValidationException(
                    message=msg.format(self.source.type),
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )

            if isinstance(self.feature_transformation, TransformationExpressionCollection):
                msg = "Dsl transform is not supported for on the fly calculation"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )

            try:
                # apply source lookback, if source lookback is not provided,
                # assume data does not use aggregation outside the time window
                source_start_date_time = feature_window_start_date_time
                if self.source_lookback and feature_window_start_date_time:
                    source_start_date_time = feature_window_start_date_time - self.source_lookback.to_timedelta()

                # load from source
                df = self.source._load_pandas(
                    start_time=source_start_date_time, end_time=feature_window_end_date_time, **kwargs
                )

                # apply feature transform
                kwargs[ONLINE_ON_THE_FLY] = "true"
                if isinstance(self.feature_transformation, TransformationCode):
                    df = feature_transform(df, self.feature_transformation, **kwargs)

                # apply filter
                index_columns = list(map(lambda i: i.name, self.get_index_columns()))
                if not features or len(features) == 0:
                    features = list(map(lambda f: f.name, self.features))
                timestamp_column, timestamp_format = self.get_timestamp_column()

                df = filter_dataframe(
                    df=df,
                    feature_window_start_datetime=feature_window_start_date_time,
                    feature_window_end_datetime=feature_window_end_date_time,
                    timestamp_column=timestamp_column,
                    timestamp_format=timestamp_format,
                    index_columns=index_columns,
                    features=features,
                )

                return df

            except Exception as ex:  # pylint: disable=broad-except
                if isinstance(ex, MlException):
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureSetSpec.ToPandasDataframe, {type(ex).__name__}:"
                        f" {ex.no_personal_data_message}"
                    )
                else:
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureSetSpec.ToPandasDataframe, {type(ex).__name__}: {ex}"
                    )

                log_and_raise_error(error=ex, debug=True)

    def __validate_schema(self, df: "DataFrame"):
        from azureml.featurestore._utils.type_map import TypeMap

        columns_set = set(df.columns)
        for feature in self.features:
            if feature.name not in columns_set:
                msg = "Schema check errors, no feature column: {} in output dataframe"
                raise ValidationException(
                    message=msg.format(feature.name),
                    no_personal_data_message=msg,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )
            data_type = TypeMap.spark_to_column_type(df.schema[feature.name].dataType.typeName())
            expected_data_type = feature.type
            if data_type != expected_data_type:
                raise ValidationException(
                    message=SCHEMA_ERROR_WRONG_DATA_TYPE.format(feature.name, data_type, expected_data_type),
                    no_personal_data_message=SCHEMA_ERROR_WRONG_DATA_TYPE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.GENERAL,
                )

        for index_column in self.index_columns:
            if index_column.name not in columns_set:
                raise ValidationException(
                    message=SCHEMA_ERROR_NO_INDEX_COLUMN.format(index_column.name),
                    no_personal_data_message=SCHEMA_ERROR_NO_INDEX_COLUMN,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )
            data_type = TypeMap.spark_to_column_type(df.schema[index_column.name].dataType.typeName())
            expected_data_type = index_column.type
            if data_type != expected_data_type:
                raise ValidationException(
                    message=SCHEMA_ERROR_WRONG_DATA_TYPE.format(index_column.name, data_type, expected_data_type),
                    no_personal_data_message=SCHEMA_ERROR_WRONG_DATA_TYPE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.GENERAL,
                )


@monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->CreateFeatureSetSpec", ActivityType.PUBLICAPI)
def create_feature_set_spec(
    *,
    infer_schema: Optional[bool] = False,
    spec_path: Optional[Union[str, PathLike, IO[str]]] = None,
    source: Optional[Union[FeatureSource, FeatureSourceBase]] = None,
    features: Optional[List[Feature]] = None,
    index_columns: Optional[List[Column]] = None,
    transformation_code: Optional[TransformationCode] = None,
    feature_transformation: Optional[FeatureTransformation] = None,
    source_lookback: Optional[DateTimeOffset] = None,
    temporal_join_lookback: Optional[DateTimeOffset] = None,
    credential: Optional[TokenCredential] = None,
    schema_version: Optional[int] = 2,
) -> FeatureSetSpec:
    """Utility for creating a FeatureSetSpec.

    If infer schema is True, infer the type for every column that is not an index column or timestamp column.
    Add all these columns and their column type to the Feature list of the returned FeatureSetSpec.

    :param infer_schema: whether to infer the schema
    :type infer_schema: bool, default: False
    :param spec_path: feature set spec path to infer from, required if other objects are not provided,
            will override other objects if provided.
    :type spec_path: Union[str, PathLike, IO[str]], optional
    :param source: FeatureSource object to be included in feature set spec result
    :type FeatureSource, optional
    :param features: List of Feature object to be included in feature set spec result
    :type features: List[Feature], optional
    :param index_columns: List of Index Column object to be included in feature set spec result
    :type index_columns: List[Column], optional
    :param transformation_code: Transformation code to be included in feature set spec result
    :type transformation_code: TransformationCode, optional, Deprecated
    :param feature_transformation: Transformation logic to be applied to the feature set, can be UDF or DSL
    :type feature_transformation: FeatureTransformation, optional
    :param source_lookback: source lookback to be included in feature set spec result
    :type source_lookback: DateTimeOffset, optional
    :param temporal_join_lookback: temporal join lookback to be included in feature set spec result
    :type temporal_join_lookback: DateTimeOffset, optional
    :param credential: User credential to initialize the spec.
    :type credential: Optional[TokenCredential]
    :returns: Featureset Spec
    :rtype: FeaturesetSpec
    """
    try:
        if spec_path:
            feature_set_spec = FeatureSetSpec.from_config(spec_path=spec_path, credential=credential)
        else:
            feature_set_spec = FeatureSetSpec(
                source=source,
                features=features,
                index_columns=index_columns,
                feature_transformation_code=transformation_code,
                feature_transformation=feature_transformation,
                source_lookback=source_lookback,
                temporal_join_lookback=temporal_join_lookback,
                schema_version=schema_version,
            )
            if isinstance(feature_set_spec.source, FeatureSetFeatureSource):
                feature_set_spec.source._initialize(credential=credential)
                feature_set_spec.index_columns = feature_set_spec.source.feature_set.get_index_columns()

        if infer_schema:
            if isinstance(feature_transformation, TransformationExpressionCollection):
                msg = "Schema inference is not supported for DSL"
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

            from azureml.featurestore._utils.type_map import TypeMap

            timestamp_column, _ = feature_set_spec.get_timestamp_column()
            df = feature_set_spec.to_spark_dataframe(
                feature_window_start_date_time=None,
                feature_window_end_date_time=None,
                features=None,
                dedup=False,  # cspell:ignore dedup
                schema_validation=False,
            )

            features = []
            index_columns_set = {index_column.name for index_column in feature_set_spec.index_columns}

            for column_name in df.columns:
                if column_name != timestamp_column and column_name not in index_columns_set:
                    data_type = TypeMap.spark_to_column_type(df.schema[column_name].dataType.typeName())
                    features.append(Feature(name=column_name, type=data_type))
            feature_set_spec.features = features

        if len(feature_set_spec.features) == 0:
            raise ValidationException(
                message=EMPTY_FEATURE_MESSAGE,
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=EMPTY_FEATURE_MESSAGE,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        return feature_set_spec
    except Exception as ex:  # pylint: disable=broad-except
        if isinstance(ex, MlException):
            ops_logger.package_logger.error(
                f"{PACKAGE_NAME}->CreateFeatureSetSpec, {type(ex).__name__}: {ex.no_personal_data_message}"
            )
        else:
            ops_logger.package_logger.error(f"{PACKAGE_NAME}->CreateFeatureSetSpec, {type(ex).__name__}: {ex}")

        log_and_raise_error(error=ex, debug=True)
