# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import unittest
from datetime import datetime

import numpy
import pandas as pd
import pytest
from azureml.featurestore._utils._constants import CREATE_TIMESTAMP_COLUMN
from azureml.featurestore._utils.pandas_utils import _get_module, filter_dataframe, infer_event_timestamp_range
from azureml.featurestore.contracts import DateTimeOffset, TimestampColumn, TransformationCode
from azureml.featurestore.transformation.aggregation_function import AggregationFunction
from azureml.featurestore.transformation.window_aggregation import WindowAggregation


@pytest.mark.unittest
class PandasUtilsTest(unittest.TestCase):
    def test_get_module(self):
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")

        # Test with a valid transformer code and class name
        transformer_class = "foo.CustomerTransactionsTransformer"
        transformer_code = TransformationCode(
            path="./code",
            transformer_class=transformer_class,
        )
        transformer_code._patch_zip(spec_path)

        _class = _get_module(transformer_code, transformer_class)
        assert _class.__name__ == "CustomerTransactionsTransformer"

        # Test with a non-existent module
        transformer_class = "nonexistent_module.NonexistentClass"
        with pytest.raises(ImportError):
            _get_module(transformer_code, transformer_class)

        # Test with a non-existent class
        transformer_class = "foo.NonexistentClass"
        with pytest.raises(AttributeError):
            _get_module(transformer_code, transformer_class)

    def test_filter_dataframe(self):
        input_df = pd.DataFrame(
            {
                "timestamp": ["2023-01-01 00:00:00"],
                "customer_id": ["1"],
                "feature1": ["value1"],
                "feature2": ["value2"],
                "feature3": ["value3"],
                CREATE_TIMESTAMP_COLUMN: ["2023-02-01 00:00:00"],
            }
        )

        # timestamp and customer_id are different from the previous item
        input_df2 = pd.DataFrame(
            {
                "timestamp": ["2023-01-02 00:00:00"],
                "customer_id": ["2"],
                "feature1": ["value1"],
                "feature2": ["value2"],
                "feature3": ["value3"],
                CREATE_TIMESTAMP_COLUMN: ["2023-02-01 00:00:00"],
            }
        )

        input_df = pd.concat([input_df, input_df2])

        df = filter_dataframe(
            input_df,
            feature_window_start_datetime=datetime(2023, 1, 1),
            feature_window_end_datetime=datetime(2023, 1, 2),
            timestamp_column="timestamp",
            index_columns=["customer_id"],
            features=["feature1", "feature2"],
        )

        assert df[df.columns[0]].count() == 1  # only 1 row returned
        assert df["customer_id"].values[0] == "1"
        assert df["timestamp"].values[0] == numpy.datetime64("2023-01-01T00:00:00.000000000")
        assert df["feature1"].values[0] == "value1"
        assert df["feature2"].values[0] == "value2"
        assert df[CREATE_TIMESTAMP_COLUMN].values[0] == "2023-02-01 00:00:00"

        # test with timestamp format
        input_df["timestamp"] = ["2023-01-01 00:00:00", "2023-01-02 00:00:00"]
        df = filter_dataframe(
            input_df,
            feature_window_start_datetime=datetime(2023, 1, 1),
            feature_window_end_datetime=datetime(2023, 1, 3),
            timestamp_column="timestamp",
            timestamp_format="%Y-%m-%d %H:%M:%S",
            index_columns=["customer_id"],
            features=["feature1", "feature2"],
        )

        assert df[df.columns[0]].count() == 2  # 2 row returned
        assert df["customer_id"].values[0] == "1"
        assert df["timestamp"].values[0] == numpy.datetime64("2023-01-01T00:00:00.000000000")
        assert df["feature1"].values[0] == "value1"
        assert df["feature2"].values[0] == "value2"
        assert df[CREATE_TIMESTAMP_COLUMN].values[0] == "2023-02-01 00:00:00"

        assert df["customer_id"].values[1] == "2"
        assert df["timestamp"].values[1] == numpy.datetime64("2023-01-02T00:00:00.000000000")
        assert df["feature1"].values[1] == "value1"
        assert df["feature2"].values[1] == "value2"
        assert df[CREATE_TIMESTAMP_COLUMN].values[1] == "2023-02-01 00:00:00"

    def test_infer_event_timestamp_range(self):
        # Test with a DataFrame containing a single row
        df = pd.DataFrame({"timestamp": ["2022-01-01T00:00:00Z"]})
        result = infer_event_timestamp_range(df, "timestamp")
        assert result == (
            pd.Timestamp("2022-01-01T00:00:00Z"),
            pd.Timestamp("2022-01-01T00:00:00Z"),
        )

        # Test with a DataFrame containing multiple rows
        df = pd.DataFrame(
            {
                "timestamp": [
                    "2022-01-01T00:00:00Z",
                    "2022-01-02T00:00:00Z",
                    "2022-01-03T00:00:00Z",
                ]
            }
        )
        result = infer_event_timestamp_range(df, "timestamp")
        assert result == (
            pd.Timestamp("2022-01-01T00:00:00Z"),
            pd.Timestamp("2022-01-03T00:00:00Z"),
        )

        # Test with a DataFrame containing non-UTC timestamps
        df = pd.DataFrame({"timestamp": ["2022-01-01T00:00:00-05:00"]})
        result = infer_event_timestamp_range(df, "timestamp")
        assert result == (
            pd.Timestamp("2022-01-01T05:00:00Z"),
            pd.Timestamp("2022-01-01T05:00:00Z"),
        )

        # Test with an empty DataFrame
        df = pd.DataFrame(columns=["timestamp"])
        with pytest.raises(ValueError):
            infer_event_timestamp_range(df, "timestamp")
