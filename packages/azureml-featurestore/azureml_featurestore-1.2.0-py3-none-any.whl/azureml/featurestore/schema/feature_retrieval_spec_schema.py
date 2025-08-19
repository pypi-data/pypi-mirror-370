# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta, YamlFileSchema
from marshmallow import fields, post_load


class Feature(metaclass=PatchedSchemaMeta):
    feature_set = fields.Str(required=True)
    feature_name = fields.Str(required=True)
    output_name = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.feature_retrieval_spec import FeatureReference

        return FeatureReference(**data)


class FeatureStore(metaclass=PatchedSchemaMeta):
    uri = fields.Str(required=True)
    location = fields.Str(required=True)
    workspace_id = fields.Str(required=True)
    features = fields.List(NestedField(Feature), required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.feature_retrieval_spec import FeatureStoreReference

        return FeatureStoreReference(**data)


class FeatureRetrievalSpecSchema(YamlFileSchema):
    serialization_version = fields.Integer(required=True)
    feature_stores = fields.List(NestedField(FeatureStore), required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from ..contracts.feature_retrieval_spec import FeatureRetrievalSpec

        return FeatureRetrievalSpec(**data)
