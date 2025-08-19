from os import getenv
from unittest.mock import MagicMock

import pytest
from azureml.featurestore import FeatureStoreClient

from azure.core.credentials import TokenCredential

from .spark_e2e_test_base import SparkJobE2EBase


@pytest.mark.e2etest
class FeatureStoreJobE2E(SparkJobE2EBase):
    def test_spark_jobs_hobo(self):
        self._test_spark_jobs(sdk_version=getenv("SDK_BUILD_VERSION"), fs_scala_jar=getenv("FS_SCALA_JAR"))

    # Add this test for pipeline coverage to pass
    def test_feature_store_client(self):
        fake_credential = MagicMock(TokenCredential)
        fs_client = FeatureStoreClient(credential=fake_credential)
        with self.assertRaises(Exception) as ve:
            fs_client.feature_stores
        self.assertIn(
            "FeatureStoreClient was not configured with subscription, resource group and workspace information",
            str(ve.exception),
        )
