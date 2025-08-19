# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=logging-fstring-interpolation

import os
from collections import defaultdict
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Union

import yaml
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity

from azureml.featurestore._utils._constants import FEATURE_RETRIEVAL_SPEC_YAML_FILENAME, PACKAGE_NAME
from azureml.featurestore._utils.arm_id_utils import FeatureSetVersionedArmId, FeatureStoreArmId
from azureml.featurestore._utils.utils import PathType, _build_logger, _parse_path_format, _process_path
from azureml.featurestore.contracts.feature import Feature

if TYPE_CHECKING:
    from azureml.featurestore import FeatureStoreClient

ops_logger = _build_logger(__name__)


class FeatureReference(object):
    def __init__(self, feature_set: str, feature_name: str, output_name: str = None):
        self.feature_set = feature_set
        self.feature_name = feature_name
        self.output_name = output_name


class FeatureStoreReference(object):
    def __init__(self, uri: str, location: str, workspace_id: str, features: List[FeatureReference]):
        self.uri = uri
        self.location = location
        self.workspace_id = workspace_id
        self.features = features


class FeatureRetrievalSpec(object):
    """A feature set specification
    :param path: The path to the folder containing feature set spec
    :type path: str, required"""

    def __init__(self, serialization_version, feature_stores: List[FeatureStoreReference]):
        self.serialization_version = serialization_version
        self.feature_stores = feature_stores

    @staticmethod
    def _load(config, config_file):
        from marshmallow import ValidationError

        context = {
            BASE_PATH_CONTEXT_KEY: Path(config_file).parent,
        }

        try:
            from ..schema.feature_retrieval_spec_schema import FeatureRetrievalSpecSchema

            config = FeatureRetrievalSpecSchema(context=context).load(config)
        except ValidationError as ex:
            raise ValueError(ex.messages) from ex

        return config

    @staticmethod
    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureRetrievalSpec.FromConfig", ActivityType.PUBLICAPI)
    def from_config(spec_path: Union[str, PathLike]):
        """Load a feature retrieval spec from yaml config. Spec path must be a folder path, the spec file name is
        assumed as feature_retrieval_spec.yaml

        :param spec_path: The path to fetch this spec.
        :type spec_path: Union[str, PathLike]
        """
        try:
            local_spec_path = _process_path(path=spec_path)

            if not os.path.isdir(local_spec_path):
                msg = "Spec path {} must be an existing folder path"
                raise ValidationException(
                    message=msg.format(spec_path),
                    target=ErrorTarget.FEATURE_SET,
                    no_personal_data_message="Spec path must be an existing folder path",
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

            local_spec_path = os.path.join(local_spec_path, FEATURE_RETRIEVAL_SPEC_YAML_FILENAME)

            try:
                with open(local_spec_path, "r") as f:
                    cfg = yaml.safe_load(f)
            except yaml.YAMLError as ex:
                raise ValueError(str(ex)) from ex

            return FeatureRetrievalSpec._load(cfg, local_spec_path)
        except Exception as ex:  # pylint: disable=broad-except
            ops_logger.package_logger.error(
                f"{PACKAGE_NAME}->FeatureRetrievalSpec.FromConfig, {type(ex).__name__}: {ex}"
            )
            log_and_raise_error(error=ex, debug=True)

    @classmethod
    def serialize_to_file(cls, feature_store_client: "FeatureStoreClient", path: str, features: List[Feature]):
        from azureml.featurestore import FeatureStoreClient

        credentials = feature_store_client._credential  # pylint: disable=protected-access
        feature_stores = defaultdict(list)

        for feature in features:
            feature_ref = FeatureReference(
                feature_set=f"{feature.feature_set_reference.name}:{feature.feature_set_reference.version}",
                feature_name=feature.name,
                output_name=None,
            )
            arm_id = FeatureSetVersionedArmId(feature.feature_set_reference.id)
            feature_store_uri = FeatureStoreArmId.to_uri(
                arm_id.subscription_id, arm_id.resource_group_name, arm_id.workspace_name
            )

            feature_stores[feature_store_uri].append(feature_ref)

        feature_store_refs = []
        for feature_store_uri, feature_refs in feature_stores.items():
            fs_id = FeatureStoreArmId(feature_store_uri)
            fs_client = FeatureStoreClient(
                credential=credentials,
                subscription_id=fs_id.subscription_id,
                resource_group_name=fs_id.resource_group_name,
                name=fs_id.workspace_name,
            )
            fs = fs_client.feature_stores.get()
            feature_store_ref = FeatureStoreReference(
                uri=feature_store_uri,
                location=fs.location,
                workspace_id=fs._workspace_id,  # pylint: disable=protected-access
                features=feature_refs,
            )
            feature_store_refs.append(feature_store_ref)

        spec = cls(serialization_version=2, feature_stores=feature_store_refs)
        spec.dump(dest=path)

    def resolve_to_features(self, credential):
        from azureml.featurestore import FeatureStoreClient

        features = []

        for feature_store_ref in self.feature_stores:
            arm_id = FeatureStoreArmId(feature_store_ref.uri)
            fs_client = FeatureStoreClient(
                credential=credential,
                subscription_id=arm_id.subscription_id,
                resource_group_name=arm_id.resource_group_name,
                name=arm_id.workspace_name,
            )
            for feature_ref in feature_store_ref.features:
                feature_set_name, version = feature_ref.feature_set.split(":")
                feature_set = fs_client.feature_sets.get(feature_set_name, version)
                f = feature_set.get_feature(feature_ref.feature_name)
                features.append(f)

        return features

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        from ..schema.feature_retrieval_spec_schema import FeatureRetrievalSpecSchema

        return FeatureRetrievalSpecSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureRetrievalSpec.Dump", ActivityType.PUBLICAPI)
    def dump(self, dest: Union[str, PathLike], **kwargs) -> None:
        """Dump the feature retrieval spec into a file in yaml format.
        Destination path must be a folder path, the spec file name is assumed as feature_retrieval_spec.yaml, and an
        exception is raised if the file exists.

        :param dest: The destination to receive this spec.
        :type dest: Union[PathLike, str]
        """
        path_type, _ = _parse_path_format(dest)
        if path_type != PathType.local:
            msg = "Destination {} must be local path"
            raise ValidationException(
                message=msg.format(dest),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message="Destination must be a local path",
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if not os.path.isdir(dest):
            msg = "Destination {} must be an existing folder path"
            raise ValidationException(
                message=msg.format(dest),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message="Destination must be an existing folder path",
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        dest = os.path.join(dest, FEATURE_RETRIEVAL_SPEC_YAML_FILENAME)

        if os.path.isfile(dest):
            msg = "Spec file {} already exists"
            raise ValidationException(
                message=msg.format(dest),
                target=ErrorTarget.FEATURE_SET,
                no_personal_data_message="Spec file already exists",
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, **kwargs)
