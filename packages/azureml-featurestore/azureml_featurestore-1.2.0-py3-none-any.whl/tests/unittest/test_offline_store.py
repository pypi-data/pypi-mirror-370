# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import unittest
from unittest.mock import MagicMock

import mock
import pytest
from azureml.featurestore._feature_set import FeatureSet

from azure.ai.ml import MLClient
from azure.ai.ml.exceptions import ValidationException
from azure.core.credentials import TokenCredential

feature_set_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_asset.yaml")
feature_set_spec_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")
feature_store_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_store.yaml")


@pytest.mark.unittest
class OfflineStoreTest(unittest.TestCase):
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_offline_store_validation(self, mock_copy_rename_and_zip):
        from azureml.featurestore._utils._constants import OFFLINE_STORE_CONNECTION_NAME_KEY
        from azureml.featurestore._utils.error_constants import OFFLINE_CONNECTION_NAME_MISTMACH

        from azure.ai.ml.entities import FeatureStoreSettings
        from azure.ai.ml.entities._load_functions import load_feature_set, load_feature_store
        from azure.ai.ml.operations import DatastoreOperations

        # set up
        fset_config = load_feature_set(feature_set_yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = feature_set_spec_yaml_path
        rest_obj.properties.properties = {OFFLINE_STORE_CONNECTION_NAME_KEY: "offlineStoreConnectionName"}

        mock_datastore_ops = MagicMock(DatastoreOperations)
        mock_ml_client = MagicMock(MLClient)
        mock_ml_client._credential = MagicMock(TokenCredential)

        from pyspark.sql import DataFrame

        df = MagicMock(DataFrame)

        fs_config = load_feature_store(feature_store_yaml_path)
        fs_config._feature_store_settings = FeatureStoreSettings(
            offline_store_connection_name="offlineStoreConnectionName1"
        )

        mock_ml_client.feature_stores.get.return_value = fs_config
        mock_ml_client.datastores = mock_datastore_ops
        mock_ml_client.subscription_id = "sub_id"
        mock_ml_client.resource_group_name = "rg"
        mock_ml_client.workspace_name = "ws"

        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)

        with self.assertRaises(ValidationException) as ex:
            fset.offline_store.read_data(fset)
        assert OFFLINE_CONNECTION_NAME_MISTMACH in str(ex.exception)

        with self.assertRaises(Exception) as ex:
            fset.offline_store.write_data(feature_set=fset, df=df)
        assert OFFLINE_CONNECTION_NAME_MISTMACH in str(ex.exception)

        fs_config._feature_store_settings = FeatureStoreSettings(
            offline_store_connection_name="offlineStoreConnectionName"
        )
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)

        with self.assertRaises(Exception) as ex:
            fset.offline_store.read_data(fset)
        assert OFFLINE_CONNECTION_NAME_MISTMACH not in str(ex.exception)

        with self.assertRaises(Exception) as ex:
            fset.offline_store.write_data(feature_set=fset, df=df)
        assert OFFLINE_CONNECTION_NAME_MISTMACH not in str(ex.exception)

        # test offline store disabled
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)
        fset._materialization_settings.offline_enabled = False

        with self.assertRaises(Exception) as ex:
            fset.offline_store.read_data(fset)
        assert "offline materialization has been disabled" in str(ex.exception)

        with self.assertRaises(Exception) as ex:
            fset.offline_store.write_data(feature_set=fset, df=df)
        assert "offline materialization has been disabled" in str(ex.exception)
