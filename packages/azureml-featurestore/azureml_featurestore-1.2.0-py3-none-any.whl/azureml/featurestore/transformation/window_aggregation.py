# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union

from azureml.featurestore._utils.error_constants import (
    DUPLICATE_DSL_FEATURE_WITH_SOURCE_COLUMN,
    INVALID_AGGREGATION,
    INVALID_AGGREGATION_WINDOW,
    INVALID_COUNT_AGGREGATION,
)
from azureml.featurestore.contracts import DateTimeOffset
from azureml.featurestore.transformation.aggregation_function import AggregationFunction
from azureml.featurestore.transformation.transformation_expression import TransformationExpression
from jinja2 import Template
from marshmallow import EXCLUDE

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import dump_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


@experimental
class WindowAggregation(TransformationExpression):
    """Feature transformation expression representation for window aggregation
    :param feature_name: The feature name e.g. 3d_sum_of_column1
    :type feature_name: str, required
    :param source_column: The source data path e.g. column1
    :type source_column: str, required
    :param aggregation: The aggregation being performed e.g. SUM, AVG etc.
    :type aggregation: Enum, required
    :param window: The aggregation window e.g. 3d, 5d etc.
    :type window: DateTimeOffset, required
    """

    def __init__(
        self,
        *,
        feature_name: str,
        source_column: str = None,
        aggregation: Union[AggregationFunction, str],
        window: DateTimeOffset = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        if feature_name == source_column:
            raise ValidationException(
                message=DUPLICATE_DSL_FEATURE_WITH_SOURCE_COLUMN.format(feature_name),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=DUPLICATE_DSL_FEATURE_WITH_SOURCE_COLUMN,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        self.feature_name = feature_name
        self.source_column = source_column
        if isinstance(aggregation, str):
            self.aggregation = AggregationFunction(aggregation)
        else:
            self.aggregation = aggregation
        self.window = window if window else DateTimeOffset(0, 0, 1)
        if self.window.to_minutes() <= 0:
            raise ValidationException(
                message=INVALID_AGGREGATION_WINDOW.format(self.window),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=INVALID_AGGREGATION_WINDOW,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if aggregation == AggregationFunction.COUNT and source_column:
            raise ValidationException(
                message=INVALID_COUNT_AGGREGATION,
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=INVALID_COUNT_AGGREGATION,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if aggregation != AggregationFunction.COUNT and not source_column:
            raise ValidationException(
                message=INVALID_AGGREGATION.format(aggregation),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message=INVALID_AGGREGATION,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def __repr__(self):
        yaml_serialized = self._to_dict()
        return dump_yaml(yaml_serialized, default_flow_style=False)

    def __str__(self):
        return self.__repr__()

    def _to_dict(self):
        from azureml.featurestore.schema.feature_set_schema import TransformationExpressionSchema

        # pylint: disable=no-member
        return TransformationExpressionSchema(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_feathr_config(self) -> str:
        tm = Template(
            """
{{window_aggregation.feature_name}}: {
    def: {{window_aggregation.source_column}}
    aggregation: {{window_aggregation.aggregation.name}}
    window: {{window_aggregation.window.to_feathr_window()}}
}"""
        )

        return tm.render(window_aggregation=self)
