import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock

import mock
import numpy
import pandas as pd
import pyarrow
import pytest
from azureml.featurestore import FeatureSetSpec
from azureml.featurestore.contracts import DateTimeOffset
from azureml.featurestore.grpc._flight_feature_retrieval_server import AuthTokenCredential
from azureml.featurestore.online._online_feature_getter_v2 import OnlineFeatureGetterV2
from pandas.core.dtypes.common import is_datetime64_any_dtype

from azure.core.credentials import AccessToken

spec_path = os.path.join(os.path.dirname(__file__), "scenarios", "test_data", "pandas", "feature_set_spec_custom_source")


@pytest.mark.e2etest
class OnlineOnTheFlyTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def featureset_spec(self):
        self.featureset_spec = FeatureSetSpec.from_config(spec_path=spec_path)

    def test_to_pandas_dataframe_source_transform_only(self):
        self.featureset_spec.transformer_code = None

        test_df = self.featureset_spec._to_pandas_dataframe(
            feature_window_start_date_time=datetime(2020, 1, 1), feature_window_end_date_time=datetime(2023, 1, 2)
        )
        expected_df = pd.DataFrame(
            {
                "timestamp": ["2020-01-01 00:00:00", "2020-01-01 01:12:00", "2020-01-01 02:24:00"],
                "customerID": ["1", "2", "3"],
                "spending": [100.0, 200.0, 300.0],
            }
        )

        numpy.array_equal(test_df.values, expected_df.values)

    def test_to_pandas_dataframe_source_transform_and_feature_transform(self):

        test_df = self.featureset_spec._to_pandas_dataframe(
            feature_window_start_date_time=datetime(2020, 1, 1, 1), feature_window_end_date_time=datetime(2023, 1, 5)
        )

        expected_df = pd.DataFrame(
            {
                "timestamp": [
                    "2020-01-02 03:36:00",
                    "2020-01-03 07:12:00",
                    "2020-01-04 10:48:00",
                ],
                "customerID": [
                    "1",
                    "1",
                    "1",
                ],
                "spending": [
                    400.0,
                    700.0,
                    1000.0,
                ],
            }
        )
        numpy.array_equal(test_df.values, expected_df.values)

    def test_to_pandas_dataframe_source_transform_infer_timestamp(self):
        self.featureset_spec.source.timestamp_column.format = None
        self.featureset_spec.transformer_code = None

        test_df = self.featureset_spec._to_pandas_dataframe(
            feature_window_start_date_time=datetime(2020, 1, 1), feature_window_end_date_time=datetime(2023, 1, 2)
        )

        self.assertTrue(is_datetime64_any_dtype(test_df["timestamp"]))

    def test_to_pandas_dataframe_with_source_lookback(self):
        self.featureset_spec.source_lookback = DateTimeOffset(1, 0, 0)
        test_df = self.featureset_spec._to_pandas_dataframe(
            feature_window_start_date_time=datetime(2020, 1, 3), feature_window_end_date_time=datetime(2023, 1, 4)
        )
        expected_df = pd.DataFrame(
            {
                "timestamp": [
                    "2020-01-03 07:12:00",
                    "2020-01-03 08:24:00",
                    "2020-01-03 09:36:00",
                ],
                "customerID": [
                    "1",
                    "2",
                    "3",
                ],
                "spending": [400.0, 500.0, 600.0],
            }
        )
        numpy.array_equal(test_df.values, expected_df.values)

    @mock.patch("azureml.featurestore.contracts.feature.Feature.uri", "spending")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_hashkey_formats")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_features_map")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_redis_clients")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2.OnlineFeatureGetterV2._fetch_feature_data")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._parse_feature_uris")
    def test_online_feature_getter_single_observation_record(
        self,
        mock_parse_feature_uri,
        mock_fetch_feature_data,
        mock_init_redis_clients,
        mock_init_features_map,
        mock_init_hashkey_formats,
    ):
        mock_credential = MagicMock(AuthTokenCredential)
        mock_credential.get_token.return_value = AccessToken("", 1)
        self.featureset_spec.temporal_join_lookback = DateTimeOffset(2000, 0, 0)
        mock_parse_feature_uri.return_value = [self.featureset_spec.get_feature("spending")], [self.featureset_spec]
        mock_init_redis_clients.return_value = {}
        mock_init_features_map.return_value = {}
        mock_init_hashkey_formats.return_value = {}
        mock_fetch_feature_data.return_value = pyarrow.Table.from_pydict(
            {"timestamp": [], "customerID": [], "spending": []}
        )
        feature_getter = OnlineFeatureGetterV2(
            credential=mock_credential, initial_feature_uris=None, feature_sets_to_recompute=[""]
        )

        feature_uris = [self.featureset_spec.get_feature("spending").uri]
        obs_table = pyarrow.Table.from_pydict({"customerID": ["1"]})
        test_df = feature_getter.get_online_features(feature_uris=feature_uris, observation_df=obs_table)

        expected_df = pyarrow.Table.from_pydict({"customerID": ["1"], "spending": [1000.0]})

        numpy.array_equal(test_df.to_pandas().values, expected_df.to_pandas().values)

    @mock.patch("azureml.featurestore.contracts.feature.Feature.uri", "spending")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_hashkey_formats")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_features_map")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_redis_clients")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2.OnlineFeatureGetterV2._fetch_feature_data")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._parse_feature_uris")
    def test_online_feature_getter_multiple_observation_record(
        self,
        mock_parse_feature_uri,
        mock_fetch_feature_data,
        mock_init_redis_clients,
        mock_init_features_map,
        mock_init_hashkey_formats,
    ):
        mock_credential = MagicMock(AuthTokenCredential)
        mock_credential.get_token.return_value = AccessToken("", 1)
        self.featureset_spec.temporal_join_lookback = DateTimeOffset(2000, 0, 0)
        mock_parse_feature_uri.return_value = [self.featureset_spec.get_feature("spending")], [self.featureset_spec]
        mock_init_redis_clients.return_value = {}
        mock_init_features_map.return_value = {}
        mock_init_hashkey_formats.return_value = {}
        mock_fetch_feature_data.return_value = pyarrow.Table.from_pydict(
            {"timestamp": [], "customerID": [], "spending": []}
        )
        feature_getter = OnlineFeatureGetterV2(
            credential=mock_credential, initial_feature_uris=None, feature_sets_to_recompute=[""]
        )

        feature_uris = [self.featureset_spec.get_feature("spending").uri]
        obs_table = pyarrow.Table.from_pydict({"customerID": ["1", "2"]})
        test_df = feature_getter.get_online_features(feature_uris=feature_uris, observation_df=obs_table)

        expected_df = pyarrow.Table.from_pydict({"customerID": ["1", "2"], "spending": [1000.0, 800.0]})

        numpy.array_equal(test_df.to_pandas().values, expected_df.to_pandas().values)

    @mock.patch("azureml.featurestore.contracts.feature.Feature.uri", "spending")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_hashkey_formats")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_features_map")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_redis_clients")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2.OnlineFeatureGetterV2._fetch_feature_data")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._parse_feature_uris")
    def test_online_feature_getter_exceeds_join_lookback(
        self,
        mock_parse_feature_uri,
        mock_fetch_feature_data,
        mock_init_redis_clients,
        mock_init_features_map,
        mock_init_hashkey_formats,
    ):
        mock_credential = MagicMock(AuthTokenCredential)
        mock_credential.get_token.return_value = AccessToken("", 1)
        self.featureset_spec.temporal_join_lookback = DateTimeOffset(1, 0, 0)
        mock_parse_feature_uri.return_value = [self.featureset_spec.get_feature("spending")], [self.featureset_spec]
        mock_init_redis_clients.return_value = {}
        mock_init_features_map.return_value = {}
        mock_init_hashkey_formats.return_value = {}
        mock_fetch_feature_data.return_value = pyarrow.Table.from_pydict(
            {"timestamp": [], "customerID": [], "spending": []}
        )
        feature_getter = OnlineFeatureGetterV2(
            credential=mock_credential, initial_feature_uris=None, feature_sets_to_recompute=[""]
        )

        feature_uris = [self.featureset_spec.get_feature("spending").uri]
        obs_table = pyarrow.Table.from_pydict({"customerID": ["1", "2"]})
        test_df = feature_getter.get_online_features(feature_uris=feature_uris, observation_df=obs_table)

        expected_df = pyarrow.Table.from_pydict({"customerID": [], "spending": []})

        numpy.array_equal(test_df.to_pandas().values, expected_df.to_pandas().values)

    @mock.patch("azureml.featurestore.contracts.feature.Feature.uri", "spending")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_hashkey_formats")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_features_map")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._init_redis_clients")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2.OnlineFeatureGetterV2._fetch_feature_data")
    @mock.patch("azureml.featurestore.online._online_feature_getter_v2._parse_feature_uris")
    def test_online_feature_getter_override_join_lookback(
        self,
        mock_parse_feature_uri,
        mock_fetch_feature_data,
        mock_init_redis_clients,
        mock_init_features_map,
        mock_init_hashkey_formats,
    ):
        mock_credential = MagicMock(AuthTokenCredential)
        mock_credential.get_token.return_value = AccessToken("", 1)
        self.featureset_spec.temporal_join_lookback = DateTimeOffset(1, 0, 0)
        mock_parse_feature_uri.return_value = [self.featureset_spec.get_feature("spending")], [self.featureset_spec]
        mock_init_redis_clients.return_value = {}
        mock_init_features_map.return_value = {}
        mock_init_hashkey_formats.return_value = {}
        mock_fetch_feature_data.return_value = pyarrow.Table.from_pydict(
            {"timestamp": [], "customerID": [], "spending": []}
        )
        feature_getter = OnlineFeatureGetterV2(
            credential=mock_credential, initial_feature_uris=None, feature_sets_to_recompute=[""]
        )

        feature_uris = [self.featureset_spec.get_feature("spending").uri]
        obs_table = pyarrow.Table.from_pydict({"customerID": ["1", "2"]})
        test_df = feature_getter.get_online_features(
            feature_uris=feature_uris, observation_df=obs_table, apply_temporal_join_lookback=False
        )

        expected_df = pyarrow.Table.from_pydict({"customerID": ["1", "2"], "spending": [1000.0, 800.0]})

        numpy.array_equal(test_df.to_pandas().values, expected_df.to_pandas().values)
