# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import urllib.parse

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from azureml.featurestore.contracts import ColumnType


class Feature(object):
    """Feature class

    :param name: The feature name
    :type name: str
    :param type: Feature data type
    :type type: DataType
    :param output_name: Feature output column name
    :type output_name: str
    :param tags: ARM resource id of feature store containing this feature set
    :type tags: Dict[str, str], optional
    :param description: Description of this feature
    :type description: str, optional
    """

    def __init__(self, *, name, type: ColumnType, output_name=None, tags=None, description=None):  # pylint: disable=redefined-builtin
        self.name = name
        self.type = type
        self.output_name = output_name
        self.tags = tags
        self.description = description
        self.__feature_set_reference = None

    def __repr__(self):
        return f"Feature(Name={self.name},Type={self.type})"

    def __str__(self):
        return self.__repr__()

    def _to_dict(self):
        from azureml.featurestore.schema.feature_set_schema import Feature  # pylint: disable=redefined-outer-name
        from marshmallow import EXCLUDE

        return dict(Feature(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))  # pylint: disable=no-member

    @property
    def feature_set_reference(self):
        return self.__feature_set_reference

    @feature_set_reference.setter
    def feature_set_reference(self, value):
        self.__feature_set_reference = value

    @classmethod
    def from_uri(cls, uri, credential):
        from azureml.featurestore import FeatureStoreClient

        parsed_uri = urllib.parse.urlsplit(uri)
        parsed_qs = dict(urllib.parse.parse_qsl(parsed_uri.query))

        feature_id = uri.lstrip("azureml://")

        parts = feature_id.split("/")
        subscription_id = parts[1]
        resource_group = parts[3]
        provider = parts[5]  # pylint: disable=unused-variable
        workspace = parts[7]
        feature_set_name = parts[9]
        feature_set_version = parts[11]
        feature_name = parts[13].split("?")[0]

        fs_client = FeatureStoreClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            name=workspace,
        )
        feature_set = fs_client.feature_sets.get(feature_set_name, feature_set_version)

        feature = feature_set.get_feature(feature_name)
        feature.output_name = parsed_qs.get("output_name", feature.output_name)
        feature.type = parsed_qs.get("type", feature.type)

        return feature

    @property
    def uri(self):
        if self.output_name:
            query_string = f"?output_name={self.output_name}&type={self.type}"
        else:
            query_string = f"?type={self.type}"

        feature_set_id = self.feature_set_reference.arm_id
        return (
            f"azureml://subscriptions/{feature_set_id.subscription_id}/resourceGroups/"
            f"{feature_set_id.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/"
            f"{feature_set_id.workspace_name}/{feature_set_id.asset_type}/{feature_set_id.asset_name}/versions/"
            f"{feature_set_id.asset_version}/features/{self.name}{query_string}"
        )
