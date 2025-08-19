import os
import unittest
from unittest.mock import MagicMock

import mock
import pytest
from azureml.featurestore import FeatureStoreClient
from azureml.featurestore._utils.error_constants import EMPTY_FEATURE_MESSAGE
from requests import Response

from azure.ai.ml.entities._load_functions import load_feature_set, load_feature_store, load_feature_store_entity
from azure.ai.ml.operations import DatastoreOperations
from azure.ai.ml.operations._feature_set_operations import FeatureSetOperations
from azure.ai.ml.operations._feature_store_entity_operations import FeatureStoreEntityOperations
from azure.ai.ml.operations._feature_store_operations import FeatureStoreOperations
from azure.core.credentials import TokenCredential
from azure.core.paging import ItemPaged

root_path = os.path.dirname(__file__)
featurestore_yaml_path = os.path.join(root_path, "data", "feature_store.yaml")


@pytest.mark.unittest
class FeatureStoreClientTest(unittest.TestCase):
    @mock.patch("azureml.featurestore.feature_store_client.MLClient", autospec=True)
    def setUp(self, mock_ml_client):
        self.set_up_mock(mock_ml_client)

        self.fs_client = FeatureStoreClient(
            credential=self.mock_credential, subscription_id="sub_id", resource_group_name="rg", name="ws"
        )

    def set_up_mock(self, mock_ml_client):
        mock_datastore_ops = MagicMock(DatastoreOperations)
        mock_featurestore_ops = MagicMock(FeatureStoreOperations)
        mock_featureset_ops = MagicMock(FeatureSetOperations)
        mock_featurestore_entity_ops = MagicMock(FeatureStoreEntityOperations)

        mock_credential = MagicMock(TokenCredential)
        mock_credential.get_token.return_value.token = "mock_token"

        fs_config = load_feature_store(featurestore_yaml_path)
        mock_ml_client.return_value.datastores = mock_datastore_ops
        mock_ml_client.return_value._credential = mock_credential
        mock_ml_client.return_value.feature_sets = mock_featureset_ops
        mock_ml_client.return_value.feature_store_entities = mock_featurestore_entity_ops
        mock_ml_client.return_value.feature_stores = mock_featurestore_ops
        mock_featurestore_ops.get.return_value = fs_config

        self.mock_ml_client = mock_ml_client
        self.mock_featurestore_ops = mock_featurestore_ops
        self.mock_featurestore_entity_ops = mock_featurestore_entity_ops
        self.mock_featureset_ops = mock_featureset_ops
        self.mock_credential = mock_credential

    def test_init_featurestore(self):
        featurestore = self.fs_client.feature_stores.get()
        self.assertEqual(featurestore.name, "my_featurestore")

    @mock.patch("azureml.featurestore.feature_store_client.MLClient", autospec=True)
    def test_init_featurestore_empty(self, mock_ml_client):
        self.set_up_mock(mock_ml_client)
        self.mock_featurestore_ops.get.return_value = None

        with self.assertRaises(Exception) as ve:
            FeatureStoreClient(
                credential=self.mock_credential, subscription_id="sub_id", resource_group_name="rg", name="ws"
            )
        self.assertTrue("ws is not a Feature Store workspace." in str(ve.exception))

    def test_get_featurestore_entity(self):
        entity_yaml_path = os.path.join(root_path, "data", "feature_store_entity_asset.yaml")
        fs_entity = load_feature_store_entity(source=entity_yaml_path)

        # get success
        self.mock_featurestore_entity_ops.get.return_value = fs_entity
        get_entity = self.fs_client.feature_store_entities.get(name="drvier", version="1")
        self.assertEqual(get_entity.name, "driver")
        self.assertEqual(get_entity.version, "1")

        # get failure
        self.mock_featurestore_entity_ops.get.side_effect = Exception("Failed to get feature entity")
        with self.assertRaises(Exception) as ex:
            self.fs_client.feature_store_entities.get(name="drvier", version="1")
        self.assertTrue("Failed to get feature entity" in ex.exception.__repr__())

        # get with empty version
        with self.assertRaises(Exception) as ex:
            self.fs_client.feature_store_entities.get(name="driver", version=None)
        self.assertTrue("Must provide feature entity version." in ex.exception.__repr__())

    def test_list_featurestore_entity(self):
        yaml_path = os.path.join(root_path, "data", "feature_store_entity_asset.yaml")
        fs_entity = load_feature_store_entity(source=yaml_path)

        def get_next(continuation_token=None):
            return {"nextLink": None, "value": [fs_entity]}

        def extract_data(response):
            return response["nextLink"], iter(response["value"] or [])

        pager = ItemPaged(get_next, extract_data)
        self.mock_featurestore_entity_ops.list.return_value = iter(pager)

        # list success
        result = self.fs_client.feature_store_entities.list(name="drvier")
        entity = result.next()
        self.assertTrue(entity.name, "driver")
        self.assertTrue(entity.version, "1")

        # list failure
        self.mock_featurestore_entity_ops.list.side_effect = Exception("Failed to list feature entity")
        with self.assertRaises(Exception) as re:
            self.fs_client.feature_store_entities.list(name="driver")
        self.assertTrue("Failed to list feature entity" in re.exception.__repr__())

    @mock.patch("azureml.featurestore._feature_set.requests")
    @mock.patch("azureml.featurestore._utils.utils._download_file")
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_get_featureset(self, mock_copy_rename_and_zip, mock_download_file, mock_requests):
        yaml_path = os.path.join(root_path, "data", "feature_set_asset.yaml")
        spec_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")

        self.mock_credential.get_token.return_value.token = "mock_token"
        mock_response = MagicMock(Response)
        mock_requests.get.return_value = mock_response
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"properties": {"workspaceId": "dummy_guid"}}

        fset_config = load_feature_set(yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = "wasbs://test@storage.blob.core.windows.net/spec_path"

        mock_download_file.return_value = spec_yaml_path

        entity_yaml_path = os.path.join(root_path, "data", "feature_store_entity_asset.yaml")
        driver_entity = load_feature_store_entity(entity_yaml_path)
        customer_entity = load_feature_store_entity(entity_yaml_path)
        customer_entity.name = "customer"
        customer_entity.description = "customer entity"

        self.mock_featurestore_entity_ops.get.side_effect = [customer_entity, driver_entity]

        # get success
        self.mock_featureset_ops._get.return_value = rest_obj
        get_featureset = self.fs_client.feature_sets.get(name="customer_transactions", version="1")
        self.assertEqual(get_featureset.name, "customer_transactions")
        self.assertEqual(get_featureset.version, "1")
        self.assertEqual(get_featureset.entities[0].name, "customer")
        self.assertEqual(get_featureset.entities[0].version, "1")
        self.assertEqual(get_featureset.entities[1].name, "driver")
        self.assertEqual(get_featureset.entities[1].version, "1")

        # get failure
        self.mock_featureset_ops._get.side_effect = Exception("Failed to get feature set")
        with self.assertRaises(Exception) as re:
            self.fs_client.feature_sets.get(name="customer_transactions", version="1")
        self.assertTrue("Failed to get feature set" in re.exception.__repr__())

        # get with empty version
        with self.assertRaises(Exception) as re:
            self.fs_client.feature_sets.get(name="customer_transactions", version=None)
        self.assertTrue("Must provide version." in re.exception.__repr__())

    def test_list_featureset(self):
        yaml_path = os.path.join(root_path, "data", "feature_set_asset.yaml")

        fset_config = load_feature_set(yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = "wasbs://test@storage.blob.core.windows.net/spec_path"

        mock_list_result = MagicMock(ItemPaged)
        mock_featureset_version_ops = MagicMock()
        self.mock_featureset_ops._operation = mock_featureset_version_ops
        mock_featureset_version_ops.list.return_value = mock_list_result
        self.mock_featureset_ops.list.return_value = mock_list_result

        # list success
        mock_list_result.next.return_value = rest_obj
        featureset_list = self.fs_client.feature_sets.list(name="customer_transactions")
        item = featureset_list.next()
        self.assertEqual(item.name, None)
        self.assertEqual(
            item.id,
            "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1",
        )

        mock_list_result.next.return_value = fset_config
        featureset_list = self.fs_client.feature_sets.list()
        item = featureset_list.next()
        self.assertEqual(item.name, "customer_transactions")
        self.assertEqual(item.version, "1")

        # list failure
        self.mock_featureset_ops._operation.list.side_effect = Exception("Failed to list feature set")
        with self.assertRaises(Exception) as re:
            self.fs_client.feature_sets.list(name="customer_transactions")
        self.assertTrue("Failed to list feature set" in re.exception.__repr__())

        # list failure no name
        self.mock_featureset_ops.list.side_effect = Exception("Failed to list feature set")
        with self.assertRaises(Exception) as re:
            self.fs_client.feature_sets.list()
        self.assertTrue("Failed to list feature set" in re.exception.__repr__())

    @mock.patch("azureml.featurestore._feature_set.requests")
    @mock.patch("azureml.featurestore._utils.utils._download_file")
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_resolve_feature_uri(self, mock_copy_rename_and_zip, mock_download_file, mock_requests):
        from azureml.featurestore.contracts.column import ColumnType

        yaml_path = os.path.join(root_path, "data", "feature_set_asset.yaml")
        spec_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")

        self.mock_credential.get_token.return_value.token = "mock_token"
        mock_response = MagicMock(Response)
        mock_requests.get.return_value = mock_response
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"properties": {"workspaceId": "dummy_guid"}}

        fset_config = load_feature_set(yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = "wasbs://test@storage.blob.core.windows.net/spec_path"

        mock_download_file.return_value = spec_yaml_path
        self.mock_featureset_ops._get.return_value = rest_obj

        entity_yaml_path = os.path.join(root_path, "data", "feature_store_entity_asset.yaml")
        driver_entity = load_feature_store_entity(entity_yaml_path)
        driver_entity_rest_obj = driver_entity._to_rest_object()
        driver_entity_rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featurestoreentities/driver/versions/1"
        customer_entity = load_feature_store_entity(entity_yaml_path)
        customer_entity.name = "customer"
        customer_entity.description = "customer entity"
        customer_entity_rest_obj = customer_entity._to_rest_object()
        customer_entity_rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featurestoreentities/customer/versions/1"

        self.mock_featurestore_entity_ops.get.side_effect = [
            customer_entity_rest_obj,
            driver_entity_rest_obj,
            customer_entity_rest_obj,
            driver_entity_rest_obj,
            customer_entity_rest_obj,
            driver_entity_rest_obj,
            customer_entity_rest_obj,
            driver_entity_rest_obj,
        ]

        # resolve url success
        feature_uris = [
            "customer_transactions:1:transactions_6hr_sum",
            "customer_transactions:1:transactions_1day_sum",
            "customer_transactions:1:spend_6hr_sum",
            "customer_transactions:1:spend_1day_sum",
        ]
        features = self.fs_client.resolve_feature_uri(feature_uris=feature_uris)

        self.assertEqual(features[0].name, "transactions_6hr_sum")
        self.assertEqual(features[0].type, ColumnType.INTEGER)
        self.assertEqual(features[1].name, "transactions_1day_sum")
        self.assertEqual(features[1].type, ColumnType.INTEGER)
        self.assertEqual(features[2].name, "spend_6hr_sum")
        self.assertEqual(features[2].type, ColumnType.FLOAT)
        self.assertEqual(features[3].name, "spend_1day_sum")
        self.assertEqual(features[3].type, ColumnType.FLOAT)

        # fail to get featureset
        self.mock_featureset_ops._get.side_effect = Exception("Failed to get feature set")
        with self.assertRaises(Exception) as ex:
            self.fs_client.resolve_feature_uri(feature_uris=feature_uris)
        self.assertIn("Failed to get feature set", str(ex.exception))

        # feature urls none
        with self.assertRaises(Exception) as ex:
            self.fs_client.resolve_feature_uri(feature_uris=None)
        self.assertIn(EMPTY_FEATURE_MESSAGE, str(ex.exception))
