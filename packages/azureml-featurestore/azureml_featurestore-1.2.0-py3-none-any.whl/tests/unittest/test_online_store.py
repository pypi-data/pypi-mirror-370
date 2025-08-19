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
class OnlineStoreTest(unittest.TestCase):
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_online_store_validation(self, mock_copy_rename_and_zip):
        from azureml.featurestore._utils._constants import ONLINE_STORE_CONNECTION_NAME_KEY
        from azureml.featurestore._utils.error_constants import ONLINE_CONNECTION_NAME_MISMATCH

        from azure.ai.ml.entities import FeatureStoreSettings
        from azure.ai.ml.entities._load_functions import load_feature_set, load_feature_store
        from azure.ai.ml.operations import DatastoreOperations

        # set up
        fset_config = load_feature_set(feature_set_yaml_path)
        rest_obj = fset_config._to_rest_object()
        rest_obj.id = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.MachineLearningServices/workspaces/mdcmaster/featuresets/customer_transactions/versions/1"
        rest_obj.properties.specification.path = feature_set_spec_yaml_path
        rest_obj.properties.properties = {ONLINE_STORE_CONNECTION_NAME_KEY: "onlineStoreConnectionName"}

        mock_datastore_ops = MagicMock(DatastoreOperations)
        mock_ml_client = MagicMock(MLClient)
        mock_ml_client._credential = MagicMock(TokenCredential)

        from pyspark.sql import DataFrame

        df = MagicMock(DataFrame)

        fs_config = load_feature_store(feature_store_yaml_path)
        fs_config._feature_store_settings = FeatureStoreSettings(
            offline_store_connection_name="onlineStoreConnectionName1"
        )

        mock_ml_client.feature_stores.get.return_value = fs_config
        mock_ml_client.datastores = mock_datastore_ops
        mock_ml_client.subscription_id = "sub_id"
        mock_ml_client.resource_group_name = "rg"
        mock_ml_client.workspace_name = "ws"

        # test online materialization
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)

        from azureml.featurestore.online._online_feature_materialization import materialize_online

        df = MagicMock()

        with self.assertRaises(ValidationException) as ex:
            materialize_online(feature_set=fset, dataframe_to_store=df)
        assert ONLINE_CONNECTION_NAME_MISMATCH in str(ex.exception)

        fs_config._feature_store_settings = FeatureStoreSettings(
            online_store_connection_name="onlineStoreConnectionName"
        )
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)

        with self.assertRaises(Exception) as ex:
            materialize_online(feature_set=fset, dataframe_to_store=df)
        assert ONLINE_CONNECTION_NAME_MISMATCH not in str(ex.exception)

        # test online get features
        from azureml.featurestore import init_online_lookup

        fs_config._feature_store_settings = FeatureStoreSettings(
            online_store_connection_name="onlineStoreConnectionName1"
        )
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)
        feature1 = fset.get_feature("transactions_6hr_sum")
        feature2 = fset.get_feature("transactions_1day_sum")
        os.environ["AZUREML_FEATURESTORE_SERVICE_ENDPOINT"] = "dummy"
        with self.assertRaises(ValidationException) as ex:
            init_online_lookup(features=[feature1, feature2], credential=MagicMock())
        assert ONLINE_CONNECTION_NAME_MISMATCH in str(ex.exception)

        fs_config._feature_store_settings = FeatureStoreSettings(
            online_store_connection_name="onlineStoreConnectionName"
        )
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)
        feature1 = fset.get_feature("transactions_6hr_sum")
        feature2 = fset.get_feature("transactions_1day_sum")

        with self.assertRaises(Exception) as ex:
            init_online_lookup(features=[feature1, feature2], credential=MagicMock())
        assert ONLINE_CONNECTION_NAME_MISMATCH not in str(ex.exception)

        # test online materialization disabled
        fset = FeatureSet._from_rest_object(rest_obj, mock_ml_client)
        fset._materialization_settings.online_enabled = False

        with self.assertRaises(Exception) as ex:
            materialize_online(feature_set=fset, dataframe_to_store=df)
        assert "online materialization has been disabled" in str(ex.exception)

        feature1 = fset.get_feature("transactions_6hr_sum")
        feature2 = fset.get_feature("transactions_1day_sum")
        with self.assertRaises(Exception) as ex:
            init_online_lookup(features=[feature1, feature2], credential=MagicMock())
        assert "online materialization has been disabled" in str(ex.exception)

        os.environ.pop("AZUREML_FEATURESTORE_SERVICE_ENDPOINT")
