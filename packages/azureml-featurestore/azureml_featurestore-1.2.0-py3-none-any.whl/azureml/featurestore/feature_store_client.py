# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access,logging-fstring-interpolation,client-accepts-api-version-keyword,no-member,client-method-missing-type-annotations,client-incorrect-naming-convention,missing-client-constructor-parameter-credential

from os import PathLike
from typing import IO, AnyStr, Dict, List, Optional, Union

from azure.ai.ml import MLClient
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_02_01_preview.models import ListViewType
from azure.ai.ml._telemetry.activity import ActivityType, monitor_with_activity
from azure.ai.ml.entities import FeatureStore, FeatureStoreEntity
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationErrorType, ValidationException
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._offline_query import PointAtTimeRetrievalJob
from azureml.featurestore._offline_query.equal_time import EqualTimeRetrievalJob
from azureml.featurestore._utils._constants import DSL_QUERY_MODE_KEY, PACKAGE_NAME, QUERY_MODE_DSL, QUERY_MODE_DSL_SHIM
from azureml.featurestore._utils.error_constants import (
    EMPTY_FEATURE_MESSAGE,
    FEATURE_STORE_CLIENT_INCORRECT_SETUP,
    FEATURE_WRONG_TYPE,
    NOT_A_FEATURE_STORE,
)
from azureml.featurestore._utils.utils import (
    _build_logger,
    feature_uri_parser_with_rename,
    resolve_features,
    validate_features,
)
from azureml.featurestore.abstract_feature_store import AbstractFeatureStore
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.contracts.feature_retrieval_spec import FeatureRetrievalSpec
from azureml.featurestore.contracts.transformation_type import TransformationType
from azureml.featurestore.contracts.join_type import JoinType

ops_logger = _build_logger(__name__)


class FeatureStoreClient(AbstractFeatureStore):
    """Represents a feature store client.

    :param credential: Credential to use for authentication, optional for local features tore.
    :type credential: ~azure.core.credentials.TokenCredential
    :param subscription_id: Azure subscription ID, optional for local feature store.
    :type subscription_id: str, optional
    :param resource_group_name: Azure resource group, optional for local feature store.
    :type resource_group_name: str, optional
    :param name: Feature store workspace name to use in the client, optional for local feature store.
        Defaults to None
    :type name: str, optional
    """

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureStore.Init", ActivityType.PUBLICAPI)
    def __init__(
        self,
        *,
        credential: TokenCredential,
        subscription_id: str = None,
        resource_group_name: str = None,
        name: str = None,
        **kwargs: Dict,
    ):
        """Initialize a feature store client

        :param credential: Credential to use for authentication.
        :type credential: ~azure.core.credentials.TokenCredential
        :param subscription_id: Azure subscription ID.
        :type subscription_id: str, Required
        :param resource_group_name: Azure resource group.
        :type resource_group_name: str, Required
        :param name: Feature store workspace name to use in the client.
        :type name: str, Required
        """
        try:
            super().__init__(name, "managed")

            self._credential = credential
            self._subscription_id = subscription_id
            self._resource_group_name = resource_group_name
            self._workspace_name = name
            self._ml_client = None
            self._feature_stores = None
            self._feature_store_entities = None
            self._feature_sets = None

            if subscription_id and resource_group_name and name:
                self._ml_client = MLClient(credential, subscription_id, resource_group_name, name, **kwargs)

                self._feature_stores = FeatureStoreClient.FeatureStoreDataPlaneOperations(ml_client=self._ml_client)
                self._feature_store_entities = FeatureStoreClient.FeatureStoreEntityDataPlaneOperations(
                    ml_client=self._ml_client
                )
                self._feature_sets = FeatureStoreClient.FeatureSetDataPlaneOperations(ml_client=self._ml_client)

                if not self._feature_stores.get():
                    raise ValidationException(
                        message=NOT_A_FEATURE_STORE.format(name),
                        target=ErrorTarget.WORKSPACE,
                        no_personal_data_message=NOT_A_FEATURE_STORE,
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
                    )

        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, MlException):
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureStoreClient.Init, {type(ex).__name__}: {ex.no_personal_data_message}"
                )
            else:
                ops_logger.package_logger.error(f"{PACKAGE_NAME}->FeatureStoreClient.Init, {type(ex).__name__}: {ex}")

            log_and_raise_error(error=ex, debug=True)

    @monitor_with_activity(
        ops_logger, f"{PACKAGE_NAME}->FeatureStoreClient.Generate_Feature_Retrieval_Spec", ActivityType.PUBLICAPI
    )
    # pylint: disable=specify-parameter-names-in-call
    def generate_feature_retrieval_spec(self, path: Union[str, PathLike, IO[AnyStr]], features: List[Feature]):
        FeatureRetrievalSpec.serialize_to_file(self, path, features)

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->Resolve_FeatureRetrievalSpec", ActivityType.PUBLICAPI)
    def resolve_feature_retrieval_spec(self, path: Union[str, PathLike, IO[AnyStr]]):
        feature_retrieval_spec = FeatureRetrievalSpec.from_config(path)
        features = feature_retrieval_spec.resolve_to_features(self._credential)
        return features

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureStoreClient.Resolve_FeatureUri", ActivityType.PUBLICAPI)
    def resolve_feature_uri(self, feature_uris: List[str], **kwargs: Dict) -> List[Feature]:
        try:
            if not feature_uris:
                raise ValidationException(
                    message=EMPTY_FEATURE_MESSAGE,
                    target=ErrorTarget.GENERAL,
                    no_personal_data_message=EMPTY_FEATURE_MESSAGE,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.MISSING_FIELD,
                )

            features = []

            for uri in feature_uris:
                feature_set_name, version, feature_name = feature_uri_parser_with_rename(uri)
                feature_set = self.feature_sets.get(name=feature_set_name, version=version, **kwargs)
                f = feature_set.get_feature(name=feature_name)
                features.append(f)

            return features
        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, MlException):
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureStoreClient.Resolve_FeatureUri, {type(ex).__name__}:"
                    f" {ex.no_personal_data_message}"
                )
            else:
                ops_logger.package_logger.error(
                    f"{PACKAGE_NAME}->FeatureStoreClient.Resolve_FeatureUri, {type(ex).__name__}: {ex}"
                )

            log_and_raise_error(error=ex, debug=True)

    class FeatureStoreDataPlaneOperations:
        def __init__(self, ml_client: MLClient):
            self._ml_client = ml_client

        @monitor_with_activity(
            ops_logger, f"{PACKAGE_NAME}->FeatureStoreDataPlaneOperations.Get", ActivityType.PUBLICAPI
        )
        def get(self, **kwargs) -> FeatureStore:
            """Get a feature store object

            :return: feature store workspace object.
            :rtype: FeatureStore
            """

            try:
                features_store = self._ml_client.feature_stores.get(name=self._ml_client.workspace_name, **kwargs)

                return features_store
            except Exception as ex:  # pylint: disable=broad-except
                if isinstance(ex, MlException):
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureStoreDataPlaneOperations.Get, {type(ex).__name__}:"
                        f" {ex.no_personal_data_message}"
                    )
                else:
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureStoreDataPlaneOperations.Get, {type(ex).__name__}: {ex}"
                    )

                log_and_raise_error(error=ex, debug=True)

    class FeatureStoreEntityDataPlaneOperations:
        def __init__(self, ml_client: MLClient):
            self._ml_client = ml_client

        @monitor_with_activity(
            ops_logger, f"{PACKAGE_NAME}->FeatureStoreEntityDataPlaneOperations.Get", ActivityType.PUBLICAPI
        )
        def get(self, name: str, version: str, **kwargs: Dict) -> FeatureStoreEntity:
            """Get the specified FeatureStoreEntity asset.

            :param name: Name of FeatureStoreEntity asset.
            :type name: str
            :param version: Version of FeatureStoreEntity asset.
            :type version: str
            :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureStoreEntity cannot be successfully
                identified and retrieved. Details will be provided in the error message.
            :return: FeatureStoreEntity asset object.
            :rtype: ~azure.ai.ml.entities.FeatureStoreEntity
            """

            try:
                if not version:
                    msg = "Must provide feature entity version."
                    raise ValidationException(
                        message=msg,
                        target=ErrorTarget.ASSET,
                        no_personal_data_message=msg,
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.MISSING_FIELD,
                    )
                featurestore_entity = self._ml_client.feature_store_entities.get(
                    name=name,
                    version=version,
                    **kwargs,
                )

                return featurestore_entity
            except Exception as ex:  # pylint: disable=broad-except
                if isinstance(ex, MlException):
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureStoreEntityDataPlaneOperations.Get, {type(ex).__name__}:"
                        f" {ex.no_personal_data_message}"
                    )
                else:
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureStoreEntityDataPlaneOperations.Get, {type(ex).__name__}: {ex}"
                    )

                log_and_raise_error(error=ex, debug=True)

        @monitor_with_activity(
            ops_logger, f"{PACKAGE_NAME}->FeatureStoreEntityDataPlaneOperations.List", ActivityType.PUBLICAPI
        )
        def list(
            self,
            name: Optional[str] = None,
            *,
            list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
            **kwargs: Dict,
        ) -> ItemPaged[FeatureStoreEntity]:
            """List the FeatureStoreEntity assets of the workspace.

            :param name: Name of a specific FeatureStoreEntity asset, optional.
            :type name: Optional[str]
            :param list_view_type: View type for including/excluding (for example) archived FeatureStoreEntity assets.
            Default: ACTIVE_ONLY.
            :type list_view_type: Optional[ListViewType]
            :return: An iterator like instance of FeatureStoreEntity objects
            :rtype: ~azure.core.paging.ItemPaged[FeatureStoreEntity]
            """

            try:
                featurestore_entities = self._ml_client.feature_store_entities.list(
                    name=name,
                    list_view_type=list_view_type,
                    **kwargs,
                )

                return featurestore_entities
            except Exception as ex:  # pylint: disable=broad-except
                if isinstance(ex, MlException):
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureStoreEntityDataPlaneOperations.List, {type(ex).__name__}:"
                        f" {ex.no_personal_data_message}"
                    )
                else:
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureStoreEntityDataPlaneOperations.List, {type(ex).__name__}: {ex}"
                    )

                log_and_raise_error(error=ex, debug=True)

    class FeatureSetDataPlaneOperations:
        def __init__(self, ml_client: MLClient):
            self._ml_client = ml_client

        @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->FeatureSetDataPlaneOperations.Get", ActivityType.PUBLICAPI)
        def get(self, name: str, version: str, **kwargs: Dict) -> FeatureSet:
            """Get the specified FeatureSet asset.

            :param name: Name of FeatureSet asset.
            :type name: str
            :param version: Version of FeatureSet asset.
            :type version: str
            :raises ~azure.ai.ml.exceptions.ValidationException: Raised if FeatureSet cannot be successfully
                identified and retrieved. Details will be provided in the error message.
            :return: FeatureSet asset object.
            :rtype: FeatureSet
            """

            try:
                if not version:
                    msg = "Must provide version."
                    raise ValidationException(
                        message=msg,
                        target=ErrorTarget.ASSET,
                        no_personal_data_message=msg,
                        error_category=ErrorCategory.USER_ERROR,
                        error_type=ValidationErrorType.MISSING_FIELD,
                    )
                feature_set_version_resource = self._ml_client.feature_sets._get(name=name, version=version, **kwargs)

                feature_set = FeatureSet._from_rest_object(
                    feature_set_version_resource, self._ml_client
                )
                entities_dto = []
                for e in feature_set.entities:
                    assert isinstance(e, str)
                    # Entity string in short form format ex. azureml:customer:1
                    parts = e.split(":")
                    dto = self._ml_client.feature_store_entities.get(name=parts[1], version=parts[2], **kwargs)
                    entities_dto.append(dto)

                feature_set._entities = entities_dto
                return feature_set
            except Exception as ex:  # pylint: disable=broad-except
                if isinstance(ex, MlException):
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureSetDataPlaneOperations.Get, {type(ex).__name__}:"
                        f" {ex.no_personal_data_message}"
                    )
                else:
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureSetDataPlaneOperations.Get, {type(ex).__name__}: {ex}"
                    )

                log_and_raise_error(error=ex, debug=True)

        @monitor_with_activity(
            ops_logger, f"{PACKAGE_NAME}->FeatureSetDataPlaneOperations.List", ActivityType.PUBLICAPI
        )
        def list(
            self, name=None, *, list_view_type: ListViewType = ListViewType.ACTIVE_ONLY, **kwargs: Dict
        ) -> ItemPaged[FeatureSet]:
            """List the FeatureSet assets of the workspace.

            :param name: Name of a specific FeatureSet asset, optional.
            :type name: Optional[str]
            :param list_view_type: View type for including/excluding (for example) archived FeatureSet assets.
            Default: ACTIVE_ONLY.
            :type list_view_type: Optional[ListViewType]
            :return: An iterator like instance of FeatureSet objects
            :rtype: ~azure.core.paging.ItemPaged[FeatureSet]
            """

            try:
                if name:
                    return self._ml_client.feature_sets._operation.list(
                        resource_group_name=self._ml_client.resource_group_name,
                        workspace_name=self._ml_client.workspace_name,
                        name=name,
                        list_view_type=list_view_type,
                        **kwargs,
                    )

                return self._ml_client.feature_sets.list()
            except Exception as ex:  # pylint: disable=broad-except
                if isinstance(ex, MlException):
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureSetDataPlaneOperations.List, {type(ex).__name__}:"
                        f" {ex.no_personal_data_message}"
                    )
                else:
                    ops_logger.package_logger.error(
                        f"{PACKAGE_NAME}->FeatureSetDataPlaneOperations.List, {type(ex).__name__}: {ex}"
                    )

                log_and_raise_error(error=ex, debug=True)

    @property
    def feature_stores(self) -> FeatureStoreDataPlaneOperations:
        """A collection of feature store related operations.

        :return: Feature store operations
        :rtype: FeatureStoreDataPlaneOperations
        """
        if not self._feature_stores:
            raise ValidationException(
                message=FEATURE_STORE_CLIENT_INCORRECT_SETUP,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=FEATURE_STORE_CLIENT_INCORRECT_SETUP,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        return self._feature_stores

    @property
    def feature_store_entities(self) -> FeatureStoreEntityDataPlaneOperations:
        """A collection of workspace related operations.

        :return: Feature store entity operations
        :rtype: FeatureStoreEntityDataPlaneOperations
        """
        if not self._feature_store_entities:
            raise ValidationException(
                message=FEATURE_STORE_CLIENT_INCORRECT_SETUP,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=FEATURE_STORE_CLIENT_INCORRECT_SETUP,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        return self._feature_store_entities

    @property
    def feature_sets(self) -> FeatureSetDataPlaneOperations:
        """A collection of workspace related operations.

        :return: Feature set operations
        :rtype: FeatureSetDataPlaneOperations
        """
        if not self._feature_sets:
            raise ValidationException(
                message=FEATURE_STORE_CLIENT_INCORRECT_SETUP,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=FEATURE_STORE_CLIENT_INCORRECT_SETUP,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        return self._feature_sets


@monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->Get_OfflineFeatures", ActivityType.PUBLICAPI)
def get_offline_features(
    *, features: List[Feature], observation_data, timestamp_column: str, use_materialized_data: bool = True, **kwargs
):
    """Join offline features in a spark dataframe. Requires spark context.

    Enrich an entity dataframe with historical feature values for either training or batch scoring.
    This method joins historical feature data from one or more feature sets to an entity dataframe by using a time
    travel join.

    Each feature set is joined to the entity dataframe using all entities configured for the respective feature set.

    All configured entities must be available in the entity dataframe. Therefore, the entity dataframe must
    contain all entities found in all feature sets, but the individual feature sets can have different entities.

    Time travel is based on the configured temporal join lookback for each feature set. A shorter lookback will limit
    the amount of scanning that will be done in order to find feature data for a specific entity key. Setting a short
    lookback period may result in null values being returned.
    Args:
        observation_data: (Spark.Sql.Dataframe): An entity dataframe is a collection of rows containing all entity
            columns (e.g., customer_id, driver_id) on which features need to be joined, as well as an event_timestamp
            column used to ensure point-in-time correctness. The entity dataframe is a Spark Dataframe.
        features: The list of features that should be retrieved from the offline store. Feature is obtained by
            featuresetspec['feature_name']
        timestamp_column: The name of the timestamp column of the entity dataframe
        use_materialized_data: When set to true, sdk will first try to pull feature data from offline store and fallback
            to run the query through if None is in offline store
    Returns:
        Spark Dataframe which can be used to show the results.
    """

    try:
        if not all(isinstance(n, Feature) for n in features):
            raise ValidationException(
                message=FEATURE_WRONG_TYPE,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=FEATURE_WRONG_TYPE,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        validate_features(features)

        # create the retrieval job
        dsl_query_mode = kwargs.get(DSL_QUERY_MODE_KEY, QUERY_MODE_DSL_SHIM)

        # resolve features to jobs
        job_map = resolve_features(features)
        result_df = observation_data

        for transformation_type, details in job_map.items():
            for join_type, val in details.items():
                features, feature_references, feature_sets = val
                if transformation_type == TransformationType.DSL:
                    from azureml.featurestore._offline_query import DslFeathrRetrievalJob, DslFeathrShimRetrievalJob

                    if dsl_query_mode == QUERY_MODE_DSL:
                        job = DslFeathrRetrievalJob(
                            features=features,
                            feature_references=feature_references,
                            feature_sets=feature_sets,
                            observation_data=result_df,
                            timestamp_column=timestamp_column,
                            use_materialized_data=use_materialized_data,
                            **kwargs,
                        )
                    else:
                        job = DslFeathrShimRetrievalJob(
                            features=features,
                            feature_references=feature_references,
                            feature_sets=feature_sets,
                            observation_data=result_df,
                            timestamp_column=timestamp_column,
                            use_materialized_data=use_materialized_data,
                            **kwargs,
                        )
                else:
                    if join_type == JoinType.EQUAL_TIME:
                        job = EqualTimeRetrievalJob(
                            features=features,
                            feature_references=feature_references,
                            feature_sets=feature_sets,
                            observation_data=result_df,
                            timestamp_column=timestamp_column,
                            use_materialized_data=use_materialized_data,
                            **kwargs
                        )
                    else:
                        job = PointAtTimeRetrievalJob(
                            features=features,
                            feature_references=feature_references,
                            feature_sets=feature_sets,
                            observation_data=result_df,
                            timestamp_column=timestamp_column,
                            use_materialized_data=use_materialized_data,
                            **kwargs,
                        )
                result_df = job.to_spark_dataframe()

        return result_df
    except Exception as ex:  # pylint: disable=broad-except
        if isinstance(ex, MlException):
            ops_logger.package_logger.error(
                f"{PACKAGE_NAME}->Get_OfflineFeatures, {type(ex).__name__}: {ex.no_personal_data_message}"
            )
        else:
            ops_logger.package_logger.error(f"{PACKAGE_NAME}->Get_OfflineFeatures, {type(ex).__name__}: {ex}")

        log_and_raise_error(error=ex, debug=True)


@monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->Init_OnlineLookup", ActivityType.PUBLICAPI)
def init_online_lookup(features: List[Feature], credential=None, force=False, **kwargs):
    if not credential:
        from azure.identity import ManagedIdentityCredential
        credential = ManagedIdentityCredential()

    from azureml.featurestore.grpc import initialize
    initialize(features, credential, force, **kwargs)


@monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->Shutdown_OnlineLookup", ActivityType.PUBLICAPI)
def shutdown_online_lookup():
    from azureml.featurestore.grpc import shutdown

    shutdown()


def get_online_features(features: List[Feature], observation_data: "pyarrow.Table", **kwargs) -> "pyarrow.Table":
    """Join online features in a dataframe.

    Enrich an entity dataframe with online feature values for batch scoring.
    This method joins online feature data from one or more feature sets to an entity dataframe.
    Each feature set is joined to the entity dataframe using all entities configured for the respective feature set.
    All configured entities must be available in the entity dataframe. Therefore, the entity dataframe must
    contain all entities found in all feature sets, but the individual feature sets can have different entities.
    Args:
        observation_data: (pyarrow.Table): An entity dataframe is a collection of rows containing all entity
            columns (e.g., customer_id, driver_id) on which features need to be joined.
            The entity dataframe is a pyarrow Table.
        features: The list of features that should be retrieved from the online store.
            Feature is obtained by featuresetspec['feature_name']
    Returns:
        pyarrow Table which can be used to show the results.
    """

    try:
        if not all(isinstance(n, Feature) for n in features):
            msg = "Features must be of type 'Feature'. Did you run `resolve_feature_uri()`?"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.GENERAL,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )

        from azureml.featurestore.grpc import get_online_features as get_online_features_impl
        from azureml.featurestore.grpc import is_initialized

        validate_features(features)

        if not is_initialized():
            init_online_lookup(features)

        return get_online_features_impl(features, observation_data, **kwargs)
    except Exception as ex:  # pylint: disable=broad-except
        if isinstance(ex, MlException):
            ops_logger.package_logger.error(
                f"{PACKAGE_NAME}->Get_OnlineFeatures, {type(ex).__name__}: {ex.no_personal_data_message}"
            )
        else:
            ops_logger.package_logger.error(f"{PACKAGE_NAME}->Get_OnlineFeatures, {type(ex).__name__}: {ex}")

        log_and_raise_error(error=ex, debug=True)
