# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import unittest
from unittest.mock import MagicMock

import mock
import pytest
from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._utils.error_constants import FEATURE_NAME_NOT_FOUND_FEATURE_SET, FEATURE_SET_NOT_REGISTERED
from azureml.featurestore.contracts import ColumnType
from azureml.featurestore.offline_store import AzureDataLakeOfflineStore

from azure.ai.ml import MLClient
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.exceptions import ValidationException
from azure.core.credentials import TokenCredential

feature_set_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_asset.yaml")
feature_set_spec_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")
feature_store_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_store.yaml")


@pytest.mark.unittest
class FeaturesetTest(unittest.TestCase):
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set(self, mock_copy_rename_and_zip):
        from azure.ai.ml.entities._load_functions import load_feature_set, load_feature_store
        from azure.ai.ml.operations import DatastoreOperations

        # set up
        fset_config = load_feature_set(feature_set_yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = feature_set_spec_yaml_path

        mock_datastore_ops = MagicMock(DatastoreOperations)
        mock_ml_client = MagicMock(MLClient)

        fs_config = load_feature_store(feature_store_yaml_path)
        mock_ml_client.feature_stores.get.return_value = fs_config
        mock_ml_client.datastores = mock_datastore_ops
        mock_ml_client.subscription_id = "sub_id"
        mock_ml_client.resource_group_name = "rg"
        mock_ml_client.workspace_name = "ws"
        mock_ml_client._credential = MagicMock(TokenCredential)

        # build featureset
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)

        timestamp_column, timestamp_column_format = fset.get_timestamp_column()

        # verify
        assert fset.name == "customer_transactions"
        assert fset.version == "1"
        assert fset.description == "retail customer feature-set"
        assert fset.specification.path == feature_set_spec_yaml_path

        assert fset.entities == ["azureml:customer:1", "azureml:driver:1"]

        assert fset.materialization_settings.schedule.type == "Recurrence"
        assert fset.materialization_settings.schedule.interval == 5
        assert fset.materialization_settings.schedule.frequency == "hour"
        assert fset.materialization_settings.resource.instance_type == "Standard_E8S_V3"
        assert fset.materialization_settings.notification.email_on == ["JobCompleted", "JobFailed", "JobCancelled"]
        assert fset.materialization_settings.notification.emails == ["alice@microsoft.com", "bob@contoso.com"]

        assert fset.materialization_settings.spark_configuration["spark.driver.cores"] == 1
        assert fset.materialization_settings.spark_configuration["spark.driver.memory"] == "2g"
        assert fset.materialization_settings.spark_configuration["spark.executor.cores"] == 2
        assert fset.materialization_settings.spark_configuration["spark.executor.memory"] == "2g"
        assert fset.materialization_settings.spark_configuration["spark.executor.instances"] == 2

        assert rest_obj.properties.materialization_settings.store_type.name == "ONLINE_AND_OFFLINE"
        assert fset.materialization_settings.offline_enabled is True
        assert fset.materialization_settings.online_enabled is True

        assert timestamp_column == "timestamp"
        assert timestamp_column_format == "%Y-%m-%d %H:%M:%S"

        assert fset.get_feature(name="transactions_6hr_sum").type == ColumnType.INTEGER
        assert fset.get_feature(name="transactions_1day_sum").type == ColumnType.INTEGER
        assert fset.get_feature(name="spend_6hr_sum").type == ColumnType.FLOAT
        assert fset.get_feature(name="spend_1day_sum").type == ColumnType.FLOAT

        assert type(fset.offline_store) == AzureDataLakeOfflineStore
        assert (
            fset.offline_store.target
            == "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/offlinestore"
        )

        assert (
            str(fset.uri) == "azureml://subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a"
            "/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices"
            "/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        )

        # no features
        with self.assertRaises(ValidationException) as ve:
            fset.get_feature(name="dummy_feature")
        self.assertIn(FEATURE_NAME_NOT_FOUND_FEATURE_SET, str(ve.exception.no_personal_data_message))

        # only str feature name
        with self.assertRaises(ValidationException) as ve:
            fset.get_feature(name=1)
        assert "Name must be the string name of a feature in this feature set." in str(ve.exception)

        # update path azure datalake
        asset_artifact = ArtifactStorageInfo(
            name=None,
            version=None,
            datastore_arm_id="datastores/dummy_datastore",
            relative_path="data/path",
            storage_account_url="storage_account.dfs.core.windows.net",
            container_name="container",
        )
        fset._update_path(asset_artifact)

        assert fset.path == "azureml://datastores/dummy_datastore/paths/data/path"
        assert fset.path == fset._specification.path

    @mock.patch("azureml.featurestore._feature_set.requests")
    @mock.patch("azureml.featurestore.feature_store_client.MLClient", autospec=True)
    @mock.patch("azureml.featurestore._utils.utils._download_file")
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_failure(self, mock_copy_rename_and_zip, mock_download_file, mock_ml_client, mock_requests):
        from azure.ai.ml.entities._load_functions import load_feature_set, load_feature_store
        from azure.ai.ml.operations import DatastoreOperations

        # build featureset
        fset_config = load_feature_set(feature_set_yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = feature_set_spec_yaml_path

        mock_datastore_ops = MagicMock(DatastoreOperations)
        mock_ml_client = MagicMock(MLClient)

        fs_config = load_feature_store(feature_store_yaml_path)
        mock_ml_client.feature_stores.get.return_value = fs_config
        mock_ml_client.datastores = mock_datastore_ops
        mock_ml_client._credential = MagicMock(TokenCredential)

        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)

        # no features
        with self.assertRaises(ValidationException) as ex:
            fset.get_feature(name="dummy_feature")
        assert "Feature 'dummy_feature' not found in this feature set." in str(ex.exception)

        # validate
        with self.assertRaises(ValidationException) as ex:
            from azure.ai.ml.entities._feature_set.feature_set_specification import FeatureSetSpecification
            from azure.ai.ml.entities._feature_store_entity.data_column import DataColumn
            from azure.ai.ml.entities._feature_store_entity.data_column_type import DataColumnType
            from azure.ai.ml.entities._feature_store_entity.feature_store_entity import FeatureStoreEntity

            local_fset = FeatureSet(
                name="test_feature_set",
                entities=[
                    FeatureStoreEntity(
                        name="test_entity",
                        version="1",
                        index_columns=[DataColumn(name="id", type=DataColumnType.long)],
                    )
                ],
                version="1",
                specification=FeatureSetSpecification(path=feature_set_spec_yaml_path),
            )
            local_fset.validate()
        self.assertIn(FEATURE_SET_NOT_REGISTERED, str(ex.exception))

        # download fail
        rest_obj.properties.specification.path = "wasbs://test@storage.blob.core.windows.net/spec_path"
        mock_download_file.side_effect = Exception("Fail to download file")
        with self.assertRaises(Exception) as ex:
            FeatureSet._from_rest_object(rest_obj, mock_ml_client)
        assert "Fail to download file" in str(ex.exception)
        mock_download_file.side_effect = None

        # copy and rename fail
        mock_download_file.return_value = feature_set_spec_yaml_path
        mock_copy_rename_and_zip.side_effect = Exception("Fail to copy and rename file")
        with self.assertRaises(Exception) as ex:
            FeatureSet._from_rest_object(rest_obj, mock_ml_client)
        assert "Fail to copy and rename file" in str(ex.exception)

    def _create_feature_set(self, name: str, mock_requests) -> FeatureSet:
        from azure.ai.ml.entities._load_functions import load_feature_set, load_feature_store
        from azure.ai.ml.operations import DatastoreOperations

        fset_config = load_feature_set(feature_set_yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = (
            "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/"
            + name
            + "/versions/1"
        )
        rest_obj.properties.specification.path = feature_set_spec_yaml_path

        mock_datastore_ops = MagicMock(DatastoreOperations)
        mock_ml_client = MagicMock(MLClient)

        fs_config = load_feature_store(feature_store_yaml_path)
        mock_ml_client.feature_stores.get.return_value = fs_config
        mock_ml_client.datastores = mock_datastore_ops
        mock_ml_client.subscription_id = "sub_id"
        mock_ml_client.resource_group_name = "rg"
        mock_ml_client.workspace_name = "ws"
        mock_ml_client._credential = MagicMock(TokenCredential)

        return FeatureSet._from_rest_object(rest_obj, mock_ml_client)

    @mock.patch("azureml.featurestore._feature_set.requests")
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_eq(self, mock_copy_rename_and_zip, mock_requests):
        fs1 = self._create_feature_set("fs1", mock_requests)
        fs2 = self._create_feature_set("fs1", mock_requests)
        fs3 = self._create_feature_set("fs2", mock_requests)
        assert fs1 == fs2
        assert fs1 != fs3

    @mock.patch("azureml.featurestore._feature_set.requests")
    def test_feature_set_to_pandas_dataframe(self, mock_requests):
        fs = self._create_feature_set("fs1", mock_requests)
        fs._to_pandas_dataframe = MagicMock()
        _ = fs._to_pandas_dataframe()
        self.assertEquals(1, fs._to_pandas_dataframe.call_count)
