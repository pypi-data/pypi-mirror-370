# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore abfs, adls

import re

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


class FeatureStoreArmId(object):
    """Parser for FeatureStore arm id: e.g. /subscription/.../featurestore/...

    :param arm_id: The versioned ARM id.
    :type arm_id: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the ARM id is incorrectly formatted.
    """

    REGEX_PATTERN = (
        r"^azureml://subscriptions/([a-zA-Z0-9_\-]+)/resourcegroups/([a-zA-Z0-9_\-]+)/workspaces/([a-zA-Z0-9_\-]+)$"
    )

    def __init__(self, arm_id=None):
        self.is_registry_id = None
        if arm_id:
            match = re.match(FeatureStoreArmId.REGEX_PATTERN, arm_id, re.IGNORECASE)
            if match:
                self.subscription_id = match.group(1)
                self.resource_group_name = match.group(2)
                self.workspace_name = match.group(3)
            else:
                msg = "Invalid AzureML ARM versioned Id {}"
                raise ValidationException(
                    message=msg.format(arm_id),
                    no_personal_data_message=msg.format("[arm_id]"),
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.ARM_RESOURCE,
                )

    @staticmethod
    def to_uri(subscription_id, resource_group_name, workspace_name):
        return (
            f"azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group_name}/workspaces/"
            f"{workspace_name}".lower()
        )


class FeatureSetVersionedArmId(object):
    """Parser for FeatureSet versioned arm id: e.g. /subscription/.../featurestore/.../featureset/my-
    featureset/versions/1.

    :param arm_id: The versioned feature set ARM id.
    :type arm_id: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the ARM id is incorrectly formatted.
    """

    REGEX_PATTERN = (
        "^(.+)/?subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.MachineLearningServices/"
        "workspaces/([^/]+)/featuresets/([^/]+)/versions/([^/]+)"
    )

    def __init__(self, arm_id=None):
        self.is_registry_id = None
        if arm_id:
            match = re.match(FeatureSetVersionedArmId.REGEX_PATTERN, arm_id, re.IGNORECASE)
            if match:
                self.subscription_id = match.group(2)
                self.resource_group_name = match.group(3)
                self.workspace_name = match.group(4)
                self.featureset_name = match.group(5)
                self.featureset_version = match.group(6)
            else:
                msg = "Invalid AzureML ARM versioned Id {}"
                raise ValidationException(
                    message=msg.format(arm_id),
                    no_personal_data_message=msg.format("[arm_id]"),
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.ARM_RESOURCE,
                )

    def __str__(self) -> str:
        return (
            "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/"
            "workspaces/{}/featuresets/{}/versions/{}".format(
                self.subscription_id,
                self.resource_group_name,
                self.workspace_name,
                self.featureset_name,
                self.featureset_version,
            )
        )

    def __repr__(self) -> str:
        return self.__str__()


class FeatureSetVersionedUri(object):
    """Parser for FeatureSet versioned uri: e.g. azureml://subscriptions/.../resourcegroups
    /.../workspaces/.../featuresets/featureset/my-featureset/versions/1.
    :param uri: The versioned feature set uri.
    :type uri: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the uri is incorrectly formatted.
    """

    REGEX_PATTERN = (
        "^azureml://subscriptions/([^/]+)/resourcegroups/([^/]+)/"
        "workspaces/([^/]+)/featuresets/([^/]+)/versions/([^/]+)"
    )

    def __init__(self, uri=None):
        if uri:
            match = re.match(FeatureSetVersionedUri.REGEX_PATTERN, uri, re.IGNORECASE)
            if match:
                self.subscription_id = match.group(1)
                self.resource_group_name = match.group(2)
                self.workspace_name = match.group(3)
                self.featureset_name = match.group(4)
                self.featureset_version = match.group(5)
            else:
                msg = "Invalid AzureML feature set uri {}"
                raise ValidationException(
                    message=msg.format(uri),
                    no_personal_data_message=msg.format("[uri]"),
                    error_type=ValidationErrorType.INVALID_VALUE,
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.ARM_RESOURCE,
                )

    def __str__(self) -> str:
        return (
            "/subscriptions/{}/resourcegroups/{}/workspaces/{}/featuresets/{}/versions/{}".format(
                self.subscription_id,
                self.resource_group_name,
                self.workspace_name,
                self.featureset_name,
                self.featureset_version,
            )
        )

    def __repr__(self) -> str:
        return self.__str__()


class FeatureStoreEntityVersionedArmId(object):
    """Parser for FeatureStoreEntity versioned arm id: e.g. /subscriptions/.../.../featureentities/my-
    featureentity/versions/1.

    :param arm_id: The versioned feature entity ARM id.
    :type arm_id: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the ARM id is incorrectly formatted.
    """

    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.MachineLearningServices/"
        "workspaces/([^/]+)/featurestoreentities/([^/]+)/versions/([^/]+)"
    )

    def __init__(self, arm_id):
        match = re.match(FeatureStoreEntityVersionedArmId.REGEX_PATTERN, arm_id, re.IGNORECASE)
        if match:
            self.subscription_id = match.group(1)
            self.resource_group_name = match.group(2)
            self.workspace_name = match.group(3)
            self.feature_store_entity_name = match.group(4)
            self.feature_store_entity_version = match.group(5)
        else:
            msg = "Invalid AzureML Feature Entity ARM versioned Id {}"
            raise ValidationException(
                message=msg.format(arm_id),
                no_personal_data_message=msg.format("[arm_id]"),
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.ARM_RESOURCE,
            )

    def __str__(self) -> str:
        return (
            "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/"
            "workspaces/{}/featurestoreentities/{}/versions/{}".format(
                self.subscription_id,
                self.resource_group_name,
                self.workspace_name,
                self.feature_store_entity_name,
                self.feature_store_entity_version,
            )
        )

    def __repr__(self) -> str:
        return self.__str__()


class OfflineStoreTargetArmId(object):
    """Parser for offline store arm id: e.g. /subscriptions/.../storageAccounts/.../containers/my-offlinesore-container

    :param arm_id: The offline store target ARM id.
    :type arm_id: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if the ARM id is incorrectly formatted.
    """

    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.Storage/"
        "storageAccounts/([^/]+)/blobServices/default/containers/([^/]+)"
    )

    def __init__(self, arm_id: str):
        match = re.match(OfflineStoreTargetArmId.REGEX_PATTERN, arm_id, re.IGNORECASE)
        if match:
            self.subscription_id = match.group(1)
            self.resource_group_name = match.group(2)
            self.storage_account = match.group(3)
            self.container_name = match.group(4)
        else:
            msg = "Invalid AzureML offlinestore target ARM Id {}"
            raise ValidationException(
                message=msg.format(arm_id),
                no_personal_data_message=msg.format("[arm_id]"),
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.ARM_RESOURCE,
            )

    def __str__(self) -> str:
        return (
            "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/"
            "{}/blobServices/default/containers/{}".format(
                self.subscription_id,
                self.resource_group_name,
                self.storage_account,
                self.container_name,
            )
        )

    def __repr__(self) -> str:
        return self.__str__()

    def to_abfs_path(self, region: str) -> str:
        from azureml.featurestore._utils._constants import (
            CHINA_ADLS_GEN2_URL_FORMAT,
            CHINA_EAST2,
            CHINA_NORTH3,
            GLOBAL_ADLS_GEN2_URL_FORMAT,
            US_GOV_ADLS_GEN2_URL_FORMAT,
            US_GOV_ARIZONA,
            US_GOV_VIRGINIA,
            US_NAT_ADLS_GEN2_URL_FORMAT,
            US_NAT_EAST,
            US_NAT_WEST,
            US_SEC_ADLS_GEN2_URL_FORMAT,
            US_SEC_EAST,
            US_SEC_WEST,
        )

        if region in [US_GOV_ARIZONA, US_GOV_VIRGINIA]:
            return US_GOV_ADLS_GEN2_URL_FORMAT.format(self.container_name, self.storage_account)
        if region in [CHINA_EAST2, CHINA_NORTH3]:
            return CHINA_ADLS_GEN2_URL_FORMAT.format(self.container_name, self.storage_account)
        if region in [US_SEC_EAST, US_SEC_WEST]:
            return US_SEC_ADLS_GEN2_URL_FORMAT.format(self.container_name, self.storage_account)
        if region in [US_NAT_EAST, US_NAT_WEST]:
            return US_NAT_ADLS_GEN2_URL_FORMAT.format(self.container_name, self.storage_account)

        return GLOBAL_ADLS_GEN2_URL_FORMAT.format(self.container_name, self.storage_account)
