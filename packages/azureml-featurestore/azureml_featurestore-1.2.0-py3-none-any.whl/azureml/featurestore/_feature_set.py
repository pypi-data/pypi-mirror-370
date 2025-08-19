# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# cspell: ignore dedup
# pylint: disable=too-many-instance-attributes,unused-argument,protected-access,redefined-builtin,too-many-public-methods,logging-fstring-interpolation,no-member

import json
import re
from collections import OrderedDict
from datetime import datetime
from os import PathLike
from typing import Dict, List, Optional, Union

import pandas as pd

# Used for tests
import requests  # pylint: disable=unused-import
from azureml.featurestore import FeatureSetSpec
from azureml.featurestore._utils._constants import (
    DEPRECATED_FEATURE_END_NAME,
    DEPRECATED_FEATURE_START_NAME,
    OFFLINE_MATERIALIZATION_VERSION_KEY,
    OFFLINE_STORE_CONNECTION_NAME_KEY,
    ONLINE_MATERIALIZATION_VERSION_KEY,
    ONLINE_STORE_CONNECTION_NAME_KEY,
    PACKAGE_NAME,
    PARTITION_COLUMN,
)
from azureml.featurestore._utils._preview_method import _is_private_preview_enabled
from azureml.featurestore._utils.error_constants import (
    FEATURE_NAME_NOT_FOUND_FEATURE_SET,
    FEATURE_NAME_NOT_STRING_FEATURE_SET,
    FEATURE_SET_NOT_REGISTERED,
    MISSING_TIMESTAMP_COLUMN,
    SCHEMA_ERROR_ENTITY_NOT_MATCH,
)
from azureml.featurestore._utils.utils import _build_logger
from azureml.featurestore.contracts import SourceType
from azureml.featurestore.contracts.column import Column, ColumnType
from azureml.featurestore.contracts.transformation_type import TransformationType
from marshmallow import EXCLUDE

from azure.ai.ml import MLClient
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_04_01_preview.models import FeaturesetVersion
from azure.ai.ml._schema._feature_set import MaterializationSettingsSchema
from azure.ai.ml._telemetry.activity import ActivityType, monitor_with_activity
from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, SHORT_URI_FORMAT
from azure.ai.ml.entities import FeatureSetSpecification, FeatureStoreEntity, MaterializationSettings
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationErrorType, ValidationException
from azure.ai.ml.operations import DatastoreOperations

ops_logger = _build_logger(__name__)


class FeatureSet(Artifact):
    """Represents a data plane feature set asset.

    You should not instantiate this class directly. Instead, you should create a FeatureStoreClient instance and get it
    for you by calling FeatureStoreClient.feature_sets.get().
    """

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSet.Init", ActivityType.PUBLICAPI)
    def __init__(
        self,
        *,
        name: str,
        version: str,
        entities: Union[List[str], List[FeatureStoreEntity]],
        materialization_settings: Optional[MaterializationSettings] = None,
        specification: Optional[FeatureSetSpecification] = None,
        description: Optional[str] = None,
        stage: Optional[str] = None,
        datastore_operations: Optional[DatastoreOperations] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Initialize a feature set asset.

        :param name: The feature set asset name
        :type name: str
        :param version: The feature set asset version
        :type version: str
        :param description: The feature set asset description
        :type description: str
        :param specification: Path to feature set specification folder. Can be local or cloud
        :type specification: FeatureSetSpecification
        :param entities: List of entities in the feature set
        :type entities: List[FeatureStoreEntity]
        :param materialization_settings: Materialization settings control the strategy and
                                        frequency to materialize feature set to feature store.
        :type materialization_settings: MaterializationSettings, optional
        :param stage: Stage of the asset
        :type stage: str, optional
        :param datastore_operations: operation to access workspace datastore
        :type datastore_operations: DatastoreOperations, optional
        :param tags: The feature set asset description
        :type tags: Dict(str, str)
        """

        self._entities = entities
        self._specification = specification
        self._materialization_settings = materialization_settings
        self._stage = stage
        self.__feature_set_spec = None

        if self._specification:
            credential = kwargs.pop("credential", None)
            self.__feature_set_spec = FeatureSetSpec.from_config(
                spec_path=self._specification.path, datastore_operations=datastore_operations, credential=credential
            )

        if self.__feature_set_spec is not None and hasattr(self.__feature_set_spec, "schema_version"):
            self.schema_version = self.__feature_set_spec.schema_version
        else:
            self.schema_version = 1

        properties = kwargs.get("properties", {})
        self.__offline_store_connection_name = properties.get(OFFLINE_STORE_CONNECTION_NAME_KEY, None)
        self.__online_store_connection_name = properties.get(ONLINE_STORE_CONNECTION_NAME_KEY, None)
        self.__offline_materialization_version = properties.get(OFFLINE_MATERIALIZATION_VERSION_KEY, None)
        self.__online_materialization_version = properties.get(ONLINE_MATERIALIZATION_VERSION_KEY, None)
        self.__offline_store = None
        self.__online_store = None
        self.__partition = None
        self.__is_registered = False
        self.__arm_id = None

        super().__init__(
            name=name,
            version=version,
            path=specification.path if specification else None,
            description=description,
            tags=tags,
            **kwargs,
        )

    def __repr__(self):
        info = OrderedDict()
        info["name"] = self.name.__repr__()
        info["version"] = self.version.__repr__()
        info["specification"] = self.specification.__repr__()
        info["source"] = self.source.__repr__()
        info["entities"] = [e.__repr__() for e in self.entities]
        info["features"] = [f.__repr__() for f in self.features]
        info["feature_transformation"] = self.feature_transformation.__repr__()
        info["feature_transformation_code"] = self.feature_transformation_code.__repr__()
        info["timestamp_column"] = self.timestamp_column.__repr__()
        info["source_lookback"] = self.source_lookback.__repr__()
        info["temporal_join_lookback"] = self.temporal_join_lookback.__repr__()
        info["materialization_settings"] = self.materialization_settings.__repr__()
        info["description"] = self.description.__repr__()
        info["tags"] = self.tags.__repr__()
        info["stage"] = self.stage.__repr__()

        formatted_info = json.dumps(info, indent=2)
        return "FeatureSet\n{}".format(formatted_info)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other) -> bool:
        return self.uri == other.uri

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def get_feature(self, name: str):
        if not isinstance(name, str):
            raise ValidationException(
                message=FEATURE_NAME_NOT_STRING_FEATURE_SET.format(type(name)),
                no_personal_data_message=FEATURE_NAME_NOT_STRING_FEATURE_SET,
                error_type=ValidationErrorType.INVALID_VALUE,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

        for feature in self.features:
            if feature.name == name:
                return feature

        raise ValidationException(
            message=FEATURE_NAME_NOT_FOUND_FEATURE_SET.format(name),
            no_personal_data_message=FEATURE_NAME_NOT_FOUND_FEATURE_SET,
            error_type=ValidationErrorType.INVALID_VALUE,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.GENERAL,
        )

    def __hash__(self):
        return hash(self.uri)

    def _to_dict(self):
        d = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "specification": {"path": self.specification.path},
            "entities": [e if isinstance(e, str) else f"azureml:{e.name}:{e.version}" for e in self.entities],
            "stage": self._stage,
        }
        if self.materialization_settings:
            d["materialization_settings"] = json.loads(
                json.dumps(
                    MaterializationSettingsSchema(unknown=EXCLUDE, context={BASE_PATH_CONTEXT_KEY: "./"}).dump(
                        self.materialization_settings
                    )
                )
            )

        return d

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ):
        return NotImplementedError("FeatureSet asset load should be done via `load_feature_set` helper method.")

    @property
    def arm_id(self):
        return self.__arm_id

    @property
    def uri(self) -> str:
        return (
            f"azureml://subscriptions/{self.__arm_id.subscription_id}/resourceGroups/"
            f"{self.__arm_id.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/"
            f"{self.__arm_id.workspace_name}/{self.__arm_id.asset_type}/{self.__arm_id.asset_name}/versions/"
            f"{self.__arm_id.asset_version}"
        )

    @property
    def feature_store_guid(self):
        return self.__feature_store_guid

    @property
    def entities(self):
        return self._entities

    @property
    def features(self):
        def with_feature_set_ref(feature):
            feature.feature_set_reference = self
            return feature

        return [with_feature_set_ref(feature) for feature in self.__feature_set_spec.features]

    @property
    def timestamp_column(self):
        return self.__feature_set_spec.source.timestamp_column

    @property
    def stage(self):
        return self._stage

    @property
    def source(self):
        return self.__feature_set_spec.source

    @property
    def materialization_settings(self):
        return self._materialization_settings

    @property
    def feature_transformation_code(self):
        return self.__feature_set_spec.feature_transformation_code

    @property
    def feature_transformation(self):
        return self.__feature_set_spec.feature_transformation

    @property
    def source_lookback(self):
        return self.__feature_set_spec.source_lookback

    @property
    def temporal_join_lookback(self):
        return self.__feature_set_spec.temporal_join_lookback

    @property
    def specification(self):
        return self._specification

    @property
    def offline_store(self):
        return self.__offline_store

    @property
    def offline_store_connection_name(self):
        return self.__offline_store_connection_name

    @property
    def online_store_connection_name(self):
        return self.__online_store_connection_name

    @property
    def online_materialization_version(self):
        return self.__online_materialization_version

    @property
    def online_store(self):
        return self.__online_store

    @property
    def partition(self):
        return self.__partition

    def get_index_columns(self):
        return [
            Column(index_col.name, ColumnType[index_col.type.name.lower()])
            for e in self.entities
            for index_col in e.index_columns
        ]

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSet.ToSparkDataframe", ActivityType.PUBLICAPI)
    def to_spark_dataframe(
        self,
        *,
        feature_window_start_date_time: Optional[datetime] = None,
        feature_window_end_date_time: Optional[datetime] = None,
        features: List[str] = None,
        use_materialized_data: bool = True,
        **kwargs,
    ):
        """Display a featureset in spark dataframe format, after performing necessary transformation

        :param feature_window_start_date_time: feature window start time
        :type feature_window_start_date_time: datetime, optional, default: None
        :param feature_window_end_date_time: feature window end time
        :type feature_window_end_date_time: datetime, optional, default: None
        :param features: list of feature names to display
        :type features: List(str), optional, default: empty (include all features)
        :param direct_inject: flag to indicate whether to direct inject data from source
        :type direct_inject: bool, optional, default: False
        :param dedup: flag to indicate whether to deduplicate (multiple rows share the same join keys
            and event timestamp) when loading from source data
        :type dedup: bool, optional, default: False

        Returns:
            Dataframe: Spark Dataframe which can be used to show the results and do further operations.
        """
        feature_window_start_date_time = feature_window_start_date_time or kwargs.pop(
            DEPRECATED_FEATURE_START_NAME, None
        )
        feature_window_end_date_time = feature_window_end_date_time or kwargs.pop(DEPRECATED_FEATURE_END_NAME, None)
        try:
            self.validate()

            from azureml.featurestore._utils.spark_utils import _filter_dataframe
            from pyspark.sql import SparkSession

            # check spark session
            try:
                spark = SparkSession.builder.getOrCreate()  # pylint: disable=unused-variable
            except Exception:
                raise RuntimeError("Fail to get spark session, please check if spark environment is set up.")

            timestamp_column, _ = self.get_timestamp_column()
            df = None

            # load from materialized data
            if use_materialized_data:
                # check materialization settings
                if not self.offline_store:
                    print(
                        "FeatureSet: {}, version: {}, offline store is not configured for its feature store..".format(
                            self.name, self.version
                        )
                    )
                    use_materialized_data = False
                if not self._materialization_settings:
                    print(
                        "FeatureSet: {}, version: {}, does not have materialization settings..".format(
                            self.name, self.version
                        )
                    )
                    use_materialized_data = False
                elif not self._materialization_settings.offline_enabled:
                    print(
                        "FeatureSet: {}, version: {}, does not have offline materialization enabled..".format(
                            self.name, self.version
                        )
                    )
                    use_materialized_data = False

            if use_materialized_data:
                index_columns = list(map(lambda i: i.name, self.get_index_columns()))

                df = self.offline_store.read_data(
                    feature_set=self,
                    feature_window_start_time=feature_window_start_date_time,
                    feature_window_end_time=feature_window_end_date_time,
                    materialization_version=self.__offline_materialization_version,
                )

                if df:
                    print(
                        "FeatureSet: {}, version: {}, was materialized, load data from offline store: {}".format(
                            self.name, self.version, self.offline_store.target
                        )
                    )
                    if not features or len(features) == 0:
                        features = list(map(lambda f: f.name, self.features))

                    df = _filter_dataframe(
                        df=df,
                        feature_window_start_date_time=feature_window_start_date_time,
                        feature_window_end_date_time=feature_window_end_date_time,
                        index_columns=index_columns,
                        timestamp_column=timestamp_column,
                        features=features,
                    )
                    return df

                print(
                    "FeatureSet: {}, version: {}, was not materialized, please check offline store: {}".format(
                        self.name, self.version, self.offline_store.target
                    )
                )
                use_materialized_data = False
            # load from source data
            if not use_materialized_data:
                print("FeatureSet: {}, version: {} load data from source..".format(self.name, self.version))
                dedup = kwargs.pop("dedup", False)

                if self.source.type == SourceType.FEATURESET:
                    spec_idx_set = {col.__repr__() for col in self.__feature_set_spec.index_columns}
                    fset_idx_set = {col.__repr__() for col in self.get_index_columns()}
                    if fset_idx_set != spec_idx_set:
                        raise ValidationException(
                            message=SCHEMA_ERROR_ENTITY_NOT_MATCH.format(
                                self.get_index_columns(), self.__feature_set_spec.index_columns
                            ),
                            target=ErrorTarget.GENERAL,
                            no_personal_data_message=SCHEMA_ERROR_ENTITY_NOT_MATCH,
                            error_category=ErrorCategory.USER_ERROR,
                            error_type=ValidationErrorType.INVALID_VALUE,
                        )

                df = self.__feature_set_spec.to_spark_dataframe(
                    feature_window_start_date_time=feature_window_start_date_time,
                    feature_window_end_date_time=feature_window_end_date_time,
                    features=features,
                    dedup=dedup,
                    **kwargs,
                )

            return df

        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, MlException):
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureSet.ToSparkDataframe, {type(ex).__name__}: {ex.no_personal_data_message}"
                )
            else:
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureSet.ToSparkDataframe, {type(ex).__name__}: {ex}"
                )

            log_and_raise_error(error=ex, debug=True)

    @classmethod
    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSet.FromRestObject", ActivityType.INTERNALCALL)
    def _from_rest_object(
        cls,
        featureset_rest_object: FeaturesetVersion,
        ml_client: MLClient,
    ) -> "FeatureSet":
        featureset_rest_object_details = featureset_rest_object.properties
        arm_id_object = get_arm_id_object_from_id(featureset_rest_object.id)
        featureset = FeatureSet(
            id=featureset_rest_object.id,
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            description=featureset_rest_object_details.description,
            tags=featureset_rest_object_details.tags,
            properties=featureset_rest_object_details.properties,
            entities=featureset_rest_object_details.entities,
            materialization_settings=MaterializationSettings._from_rest_object(
                featureset_rest_object_details.materialization_settings
            ),
            specification=FeatureSetSpecification._from_rest_object(featureset_rest_object_details.specification),
            stage=featureset_rest_object_details.stage,
            datastore_operations=ml_client.datastores,
            credential=ml_client._credential,
        )
        featureset.__is_registered = True
        featureset.__arm_id = arm_id_object

        # partition strategy can be overridden by user in future
        from azureml.featurestore.offline_store.partition import TimestampPartition

        featureset.__partition = TimestampPartition(
            source_column=featureset.timestamp_column.name,
            partition_column=PARTITION_COLUMN,
            partition_strategy=TimestampPartition.PartitionStrategy.DAY,
        )

        featurestore = ml_client.feature_stores.get(name=ml_client.workspace_name)
        featureset.__feature_store_guid = featurestore._workspace_id  # pylint: disable=attribute-defined-outside-init

        if featurestore:
            if featurestore.offline_store:
                from azureml.featurestore.contracts.offline_store import OfflineStoreFactory
                from azureml.featurestore.contracts.store_connection import OfflineStoreType

                featureset.__offline_store = OfflineStoreFactory.make_offline_store(
                    offline_store_type=OfflineStoreType[featurestore.offline_store.type],
                    offline_store_target=featurestore.offline_store.target,
                    connection_name=featurestore._feature_store_settings.offline_store_connection_name,
                    location=featurestore.location,
                )
            if featurestore.online_store:
                from azureml.featurestore.contracts.online_store import OnlineStoreFactory
                from azureml.featurestore.contracts.store_connection import OnlineStoreType

                featureset.__online_store = OnlineStoreFactory.make_online_store(
                    online_store_type=OnlineStoreType[featurestore.online_store.type],
                    online_store_target=featurestore.online_store.target,
                    connection_name=featurestore._feature_store_settings.online_store_connection_name,
                )

        return featureset

    def validate(self):
        if not self.__is_registered:
            raise ValidationException(
                message=FEATURE_SET_NOT_REGISTERED,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=FEATURE_SET_NOT_REGISTERED,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.CANNOT_PARSE,
            )

    def get_timestamp_column(self):
        if not self.timestamp_column:
            # TODO: Suppport Non-timeseries data [prp2]
            raise ValidationException(
                message=MISSING_TIMESTAMP_COLUMN.format(self.name),
                no_personal_data_message=MISSING_TIMESTAMP_COLUMN,
                error_type=ValidationErrorType.MISSING_FIELD,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.GENERAL,
            )

        return self.timestamp_column.name, self.timestamp_column.format

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSet.LoadDfDsl", ActivityType.INTERNALCALL)
    def _load_dataframe_dsl(
        self,
        *,
        feature_window_start_date_time: Optional[datetime] = None,
        feature_window_end_date_time: Optional[datetime] = None,
        use_materialized_data: bool = False,
        **kwargs,
    ):
        if use_materialized_data:
            from azureml.featurestore._utils._constants import COL_OBSERVATION_ENTITY_TIMESTAMP
            from pyspark.sql.functions import unix_timestamp

            timestamp_column, _ = self.get_timestamp_column()
            df = self.to_spark_dataframe(
                feature_window_start_date_time=feature_window_start_date_time,
                feature_window_end_date_time=feature_window_end_date_time,
                use_materialized_data=True,
            )
            df = df.withColumn(COL_OBSERVATION_ENTITY_TIMESTAMP, unix_timestamp(timestamp_column))
            return df

        return self.__feature_set_spec._load_source_dataframe_dsl(
            feature_window_start_date_time=feature_window_start_date_time,
            feature_window_end_date_time=feature_window_end_date_time,
            **kwargs,
        )

    def _to_feathr_config(self, type: str) -> str:
        from azureml.featurestore._utils.dsl_utils import _to_feathr_anchor_config, _to_feathr_source_config

        join_keys = [index_column.name for index_column in self.get_index_columns()]
        anchor_string = _to_feathr_anchor_config(feature_set_or_spec=self, join_keys=join_keys)
        source_string = _to_feathr_source_config(feature_set_or_spec=self)

        return anchor_string if type == "anchor" else source_string

    def _transformation_type(self) -> TransformationType:
        return self.__feature_set_spec._transformation_type()

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        regex = r"datastores\/(.+)"
        groups = re.search(regex, asset_artifact.datastore_arm_id)
        if groups:
            datastore_name = groups.group(1)
            self.path = SHORT_URI_FORMAT.format(datastore_name, asset_artifact.relative_path)
            self._specification.path = self.path

    if _is_private_preview_enabled():

        @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSet.ToPandasDf", ActivityType.PUBLICAPI)
        def _to_pandas_dataframe(
            self,
            *,
            feature_window_start_date_time: Optional[datetime] = None,
            feature_window_end_date_time: Optional[datetime] = None,
            features: Optional[List[str]] = None,
            **kwargs,
        ) -> pd.DataFrame:
            """Display a featureset in pandas dataframe format, after performing necessary transformation.
            This is only intended for debugging online on-the-fly scenarios.

            :param feature_window_start_date_time: feature window start time
            :type feature_window_start_date_time: datetime, optional, default: None
            :param feature_window_end_date_time: feature window end time
            :type feature_window_end_date_time: datetime, optional, default: None
            :param features: list of feature names to display
            :type features: List(str), optional, default: empty (include all features)

            Returns:
                Dataframe: Pandas Dataframe which can be used to show the results and do further operations.
            """

            # Pandas case will always be run-through
            df = self.__feature_set_spec._to_pandas_dataframe(
                feature_window_start_date_time=feature_window_start_date_time,
                feature_window_end_date_time=feature_window_end_date_time,
                features=features,
                **kwargs,
            )
            return df
