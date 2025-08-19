# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import unittest
from unittest.mock import MagicMock

import pytest
from azureml.featurestore.grpc import _flight_helper
from azureml.featurestore.grpc._flight_feature_retrieval_server import AuthTokenCredential

from azure.core.credentials import AccessToken, AzureKeyCredential


@pytest.mark.unittest
class GrpcFlightHelperTest(unittest.TestCase):
    def setup_method(self, test_method):
        _flight_helper.shutdown()

    def teardown_method(self, test_method):
        _flight_helper.shutdown()

    def test_grpc_flight_helper(self):
        mock_credential = MagicMock(AuthTokenCredential)
        mock_credential.get_token.return_value = AccessToken("", 1)

        _flight_helper.initialize([], mock_credential, False, on_the_fly_feature_sets=[])
