# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import unittest
from unittest import mock
from unittest.mock import MagicMock

import pyarrow
import pytest
from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore.contracts import TimestampColumn
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.grpc._flight_feature_retrieval_server import AuthTokenCredential
from azureml.featurestore.online import _on_the_fly_feature_getter

from azure.ai.ml.entities import FeatureSetSpecification
from azure.core.credentials import AccessToken, AzureKeyCredential

feature_set_spec_yaml_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_on_the_fly")


@pytest.mark.unittest
class OnTheFlyFeatureGetterTest(unittest.TestCase):
    @mock.patch("azureml.featurestore._feature_set.FeatureSet.uri", "test")
    @mock.patch("azureml.featurestore._online_query.point_at_time.PointAtTimeOnTheFlyRetrievalJob.to_pandas_dataframe")
    def test_get_on_the_fly_features(self, mock_pandas):
        fs = FeatureSet(
            name="fs1", version="1", entities=[], specification=FeatureSetSpecification(path=feature_set_spec_yaml_path)
        )
        mock.patch.object(fs, "timestamp_column", "timestamp", "%Y-%m-%d %H:%M:%S")

        feature1 = MagicMock(Feature)
        feature1.name = "feature1"
        feature1.feature_set_reference = fs
        feature1.uri = "feature1"

        feature2 = MagicMock(Feature)
        feature2.name = "feature2"
        feature2.feature_set_reference = fs
        feature2.uri = "feature2"

        mock_credential = MagicMock(AuthTokenCredential)
        mock_credential.get_token.return_value = AccessToken("", 1)

        getter = _on_the_fly_feature_getter.OnTheFlyFeatureGetter(mock_credential, [feature1, feature2], [fs])
        _ = getter.get_on_the_fly_features(
            ["feature1", "feature2"],
            pyarrow.Table.from_pydict({"timestamp": ["2020-01-01 00:00:00"], "customer_id": ["1"]}),
        )

        self.assertEquals(mock_pandas.call_count, 1)
