# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import dump_yaml
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from marshmallow import EXCLUDE

from azureml.featurestore.contracts.feature_transformation import FeatureTransformation
from azureml.featurestore.transformation.transformation_expression import TransformationExpression

@experimental
class TransformationExpressionCollection(FeatureTransformation):
    """Group of Feature transformation expression representations
    :param transformation_expressions: list of transformation expressions
    :type transformation_expressions: list, required
    """

    def __init__(self, *, transformation_expressions: List[TransformationExpression], **kwargs):  # pylint: disable=unused-argument
        self.transformation_expressions = transformation_expressions

    def __repr__(self):
        yaml_serialized = self._to_dict()
        return dump_yaml(yaml_serialized, default_flow_style=False)

    def __str__(self):
        return self.__repr__()

    def _to_dict(self):
        from azureml.featurestore.schema.feature_set_schema import FeatureTransformationSchema

        return FeatureTransformationSchema(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
