# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import os
from pathlib import Path

from azure.ai.ml._schema import NestedField, StringTransformedEnum
from azure.ai.ml._schema._feature_set import FeatureSetSpecificationSchema, MaterializationSettingsSchema
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta, YamlFileSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from marshmallow import fields, post_dump, post_load, validates, validates_schema

from azureml.featurestore._utils.utils import PathType, _parse_path_format
from azureml.featurestore.contracts import SourceType
from azureml.featurestore.contracts.column import ColumnType
from azureml.featurestore.feature_source.feature_source_factory import FeatureSourceFactory


class DateTimeOffsetSchema(metaclass=PatchedSchemaMeta):
    days = fields.Integer(strict=True)
    hours = fields.Integer(strict=True)
    minutes = fields.Integer(strict=True)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.datetimeoffset import DateTimeOffset

        return DateTimeOffset(**data)


class TimestampColumnSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(required=True, allow_none=False)
    format = fields.Str(required=False, allow_none=True)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.timestamp_column import TimestampColumn

        return TimestampColumn(**data)


class SourceProcessCodeSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=True, allow_none=False)
    process_class = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.transformation_code import SourceProcessCode

        return SourceProcessCode(**data)


class ColumnSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(required=True, allow_none=False)
    type = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.column import Column

        data["type"] = ColumnType[data["type"]]
        return Column(**data)


class Feature(metaclass=PatchedSchemaMeta):
    name = fields.Str(required=True, allow_none=False)
    type = fields.Str(required=True, allow_none=False)
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.feature import Feature  # pylint: disable=redefined-outer-name

        data["type"] = ColumnType[data["type"]]
        return Feature(**data)


class TransformationCodeSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str(required=True, allow_none=False)
    transformer_class = fields.Str(required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.transformation_code import TransformationCode

        return TransformationCode(**data)


class TransformationExpressionSchema(metaclass=PatchedSchemaMeta):
    from azureml.featurestore.transformation.aggregation_function import AggregationFunction

    transformation_type = fields.Str(default="window", load_only=True)
    feature_name = fields.Str(required=True, allow_none=False)
    source_column = fields.Str(required=False, allow_none=True)
    aggregation = StringTransformedEnum(
        allowed_values=[e.value for e in AggregationFunction], required=True, allow_none=False
    )
    window = NestedField(DateTimeOffsetSchema, required=False, allow_none=True)

    @validates("transformation_type")
    def validate_transformation_type(self, transformation_type):
        if transformation_type.lower() != "window":
            raise ValidationException(
                message="Only `window` transformation type is supported",
                no_personal_data_message="Only `window` transformation type is supported",
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.FEATURE_SET,
            )

    @post_load
    def make(self, data, **kwargs):
        from ..transformation.window_aggregation import WindowAggregation

        return WindowAggregation(**data)


class FeatureTransformationSchema(metaclass=PatchedSchemaMeta):
    transformation_code = NestedField(TransformationCodeSchema, required=False, allow_none=True)
    transformation_expressions = fields.List(
        NestedField(TransformationExpressionSchema), required=False, allow_none=True
    )

    @validates_schema
    def validate_transformation(self, data, **kwargs):
        if data.get("transformation_code") and data.get("transformation_expressions"):
            raise ValidationException(
                message="Feature transformation can't have both transformation_code and transformation_expressions",
                no_personal_data_message=(
                    "Feature transformation can't have both transformation_code and transformation_expressions"
                ),
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.FEATURE_SET,
            )

    @post_load
    def make(self, data, **kwargs):
        if "transformation_code" in data:
            return data["transformation_code"]
        if "transformation_expressions" in data:
            from ..transformation.transformation_expression_collection import TransformationExpressionCollection

            return TransformationExpressionCollection(**data)

    @post_dump
    def dump(self, data, **kwargs):
        from ..contracts.transformation_code import TransformationCode

        if isinstance(data, TransformationCode):
            return {"transformation_code": TransformationCodeSchema().dump(data)}  # pylint: disable=no-member

        from ..transformation.transformation_expression_collection import TransformationExpressionCollection

        if isinstance(data, TransformationExpressionCollection):
            return {
                "transformation_expressions": TransformationExpressionSchema(many=True).dump(  # pylint: disable=no-member
                    data.transformation_expressions
                )
            }


class Source(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=True, allow_none=False)
    path = fields.Str(required=False)
    timestamp_column = NestedField(TimestampColumnSchema, required=False)
    source_delay = NestedField(DateTimeOffsetSchema)
    source_process_code = fields.Nested(SourceProcessCodeSchema, required=False)
    dict = fields.Dict(keys=fields.Str(), values=fields.Str(), data_key="kwargs", required=False)

    @validates("path")
    def validate_specification_path(self, path):
        if path:
            path_type, _ = _parse_path_format(path)
            if path_type == PathType.local:
                raise ValidationException(
                    message="Feature source path: {} must be cloud path".format(path),
                    no_personal_data_message="Feature source path must be cloud path",
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.FEATURE_SET,
                )

    @post_load
    def make(self, data, **kwargs):
        data["type"] = SourceType[data["type"]]

        feature_source_factory = FeatureSourceFactory(**data)
        return feature_source_factory.build_feature_source()


class FeatureSetSpecSchema(YamlFileSchema):
    source = NestedField(Source, required=True, allow_none=False)
    feature_transformation_code = NestedField(TransformationCodeSchema, required=False, allow_none=True, load_only=True)
    feature_transformation = NestedField(FeatureTransformationSchema, required=False, allow_none=True)
    features = fields.List(NestedField(Feature), required=False, allow_none=True)
    index_columns = fields.List(NestedField(ColumnSchema), required=False)
    source_lookback = NestedField(DateTimeOffsetSchema)
    temporal_join_lookback = NestedField(DateTimeOffsetSchema)
    schema_version = fields.Integer(required=False, default=1, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from ..feature_set_spec import FeatureSetSpec

        return FeatureSetSpec(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)


class FeatureSetSchema(YamlFileSchema):
    name = fields.Str(required=True, allow_none=False)
    version = fields.Str(required=True, allow_none=False)
    specification = NestedField(FeatureSetSpecificationSchema, required=True, allow_none=False)
    entities = fields.List(fields.Str, required=True, allow_none=False)
    stage = fields.Str()
    description = fields.Str()
    tags = fields.Dict(keys=fields.Str(), values=fields.Str())
    materialization_settings = NestedField(MaterializationSettingsSchema)

    @validates("specification")
    def validate_specification_path(self, specification):
        pass

    @post_load
    def make(self, data, **kwargs):
        from .._feature_set import FeatureSet

        spec_path = Path(data["specification"].path)
        if not spec_path.is_absolute():
            spec_path = Path(self.context.get(BASE_PATH_CONTEXT_KEY, os.getcwd()), spec_path).resolve()
        data["specification"].path = spec_path.as_posix()
        return FeatureSet(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
