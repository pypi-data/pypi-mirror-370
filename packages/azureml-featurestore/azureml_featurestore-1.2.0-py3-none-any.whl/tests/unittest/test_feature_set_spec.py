import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from tempfile import gettempdir

import mock
import pandas as pd
import pytest
import shutil
import uuid
from azureml.featurestore import FeatureSetSpec, create_feature_set_spec
from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._utils._constants import FEATURE_SET_SPEC_YAML_FILENAME, ONLINE_ON_THE_FLY
from azureml.featurestore._utils.error_constants import (
    DUPLICATE_DSL_FEATURE_WITH_SOURCE_COLUMN,
    EMPTY_FEATURE_MESSAGE,
    FEATURE_NAME_NOT_FOUND_DSL,
    FEATURE_SET_SOURCE_VALIDATION,
    INVALID_DERIVED_FEATURE_SET,
    MISSING_INDEX_COLUMN
)
from azureml.featurestore.contracts import Column, ColumnType, DateTimeOffset, FeatureSource, SourceType
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.contracts.timestamp_column import TimestampColumn
from azureml.featurestore.contracts.transformation_code import SourceProcessCode, TransformationCode
from azureml.featurestore.feature_source import CustomFeatureSource, FeatureSetFeatureSource
from azureml.featurestore.feature_source.parquet_feature_source import ParquetFeatureSource
from azureml.featurestore.transformation import TransformationExpressionCollection, WindowAggregation

from azure.ai.ml._utils._feature_store_utils import read_feature_set_metadata
from azure.ai.ml.entities._feature_set.featureset_spec_metadata import FeaturesetSpecMetadata
from azure.ai.ml.exceptions import ValidationException
from azure.core.credentials import TokenCredential

spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")
spec_path_local_source = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_local_source")


@pytest.mark.unittest
class FeatureSetSpecTest(unittest.TestCase):
    @mock.patch("azureml.featurestore._utils.utils._download_file")
    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_load_feature_set_spec(self, mock_copy_rename_and_zip, mock_download_file):
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        fset_spec = FeatureSetSpec.from_config(spec_path=spec_path)

        assert fset_spec.source.type == SourceType.MLTABLE
        assert "data_sources/customer_transactions/mltable" in fset_spec.source.path
        assert fset_spec.source.timestamp_column.name == "timestamp"
        assert fset_spec.source.timestamp_column.format == "%Y-%m-%d %H:%M:%S"
        assert fset_spec.source.source_delay == DateTimeOffset(days=1, hours=0, minutes=0)
        assert len(fset_spec.index_columns) == 1
        assert fset_spec.index_columns[0].name == "customer_id"
        assert fset_spec.index_columns[0].type == ColumnType.STRING
        assert fset_spec.feature_transformation_code.path == "./code"
        assert fset_spec.feature_transformation_code.transformer_class == "foo.CustomerTransactionsTransformer"
        assert fset_spec.source_lookback == DateTimeOffset(days=30, hours=0, minutes=0)
        assert fset_spec.temporal_join_lookback == DateTimeOffset(days=2, hours=0, minutes=0)

        # local feature source
        with self.assertRaises(Exception) as ex:
            FeatureSetSpec.from_config(spec_path=spec_path_local_source)
        assert "must be cloud path" in str(ex.exception)

        # copy and rename fail
        mock_copy_rename_and_zip.side_effect = Exception("Fail to copy and rename file")
        with self.assertRaises(Exception) as ex:
            FeatureSetSpec.from_config(spec_path=spec_path)
        assert "Fail to copy and rename file" in str(ex.exception)

        # download fail
        cloud_yaml_path = "wasbs://test@storage.blob.core.windows.net/spec_path"
        mock_download_file.side_effect = Exception("Fail to download file")
        with self.assertRaises(Exception) as ex:
            FeatureSetSpec.from_config(spec_path=cloud_yaml_path)
        assert "Fail to download file" in str(ex.exception)

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_spec_repr(self, mock_copy_rename_and_zip):
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        fset_spec = FeatureSetSpec.from_config(spec_path=spec_path)

        expected = """feature_transformation:
  transformation_code:
    path: ./code
    transformer_class: foo.CustomerTransactionsTransformer
features:
- description: customer rolling 6 hour transaction count
  name: transactions_6hr_sum
  tags:
    feature-type: customer_transaction
  type: integer
- description: customer rolling 6 hour transaction count
  name: transactions_1day_sum
  tags:
    feature-type: customer_transaction
  type: integer
- name: spend_6hr_sum
  type: float
- name: spend_1day_sum
  type: float
- name: is_sunny
  type: boolean
index_columns:
- name: customer_id
  type: string
source:
  path: abfss://container@storage.dfs.core.windows.net/data_sources/customer_transactions/mltable
  source_delay:
    days: 1
    hours: 0
    minutes: 0
  timestamp_column:
    format: '%Y-%m-%d %H:%M:%S'
    name: timestamp
  type: mltable
source_lookback:
  days: 30
  hours: 0
  minutes: 0
temporal_join_lookback:
  days: 2
  hours: 0
  minutes: 0
"""
        assert fset_spec.__repr__() == expected
        assert fset_spec.__str__() == expected

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_spec(self, mock_copy_rename_and_zip):
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        fset_spec = FeatureSetSpec.from_config(spec_path=spec_path)

        timestamp_column, timestamp_column_format = fset_spec.get_timestamp_column()

        assert timestamp_column == "timestamp"
        assert timestamp_column_format == "%Y-%m-%d %H:%M:%S"

        index_columns = fset_spec.get_index_columns()

        assert len(index_columns) == 1
        assert index_columns[0].name == "customer_id"
        assert index_columns[0].type == ColumnType.STRING

        assert fset_spec.get_feature(name="transactions_6hr_sum").type == ColumnType.INTEGER
        assert fset_spec.get_feature(name="transactions_1day_sum").type == ColumnType.INTEGER
        assert fset_spec.get_feature(name="spend_6hr_sum").type == ColumnType.FLOAT
        assert fset_spec.get_feature(name="spend_1day_sum").type == ColumnType.FLOAT

        # no features
        with self.assertRaises(ValidationException) as ve:
            fset_spec.get_feature(name="dummy_feature")
        assert "Feature 'dummy_feature' not found in this feature set spec." in ve.exception.message

        # only str feature name
        with self.assertRaises(ValidationException) as ve:
            fset_spec.get_feature(name=1)
        assert "Name must be the string name of a feature in this feature set spec." in ve.exception.message

        # init failure
        with self.assertRaises(ValidationException) as ve:
            fset_spec = FeatureSetSpec(source=None, index_columns=[Column("id", ColumnType.INTEGER)])
        assert "Feature source is required for a feature set, please provide a feature source" in ve.exception.message

        with self.assertRaises(ValidationException) as ve:
            from azureml.featurestore.contracts.feature_source import FeatureSource
            from azureml.featurestore.contracts.timestamp_column import TimestampColumn

            fset_spec = FeatureSetSpec(
                source=FeatureSource(type=SourceType.CSV, path="test", timestamp_column=TimestampColumn("timestamp")),
                index_columns=None,
            )
        assert (
            MISSING_INDEX_COLUMN in ve.exception.message
        )

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_spec_custom_source(self, mock_copy_rename_and_zip):
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_custom_source")
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        fset_spec = FeatureSetSpec.from_config(spec_path=spec_path)

        assert len(fset_spec.source.kwargs) == 3
        assert fset_spec.source.kwargs["k1"] == "v1"
        assert fset_spec.source.kwargs["k2"] == "v2"
        assert fset_spec.source.kwargs["k3"] == "v3"
        assert fset_spec.source.source_process_code.path == "./source_process_code"
        assert fset_spec.source.source_process_code.process_class == "bar.CustomerTransactionsTransformer"

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    @mock.patch("azureml.featurestore.FeatureStoreClient")
    def test_feature_set_spec_feature_set_source(self, mock_feature_store_client, mock_copy_rename_and_zip):
        mock_feature_set_arm_id = "azureml://subscriptions/sub/resourceGroups/rg/workspaces/fs/featuresets/source_feature_set_name/versions/version1"
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_feature_set_source")
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        mock_index_columns = [Column(name="account", type=ColumnType.STRING)]
        mock_transformation_code = TransformationCode(path=os.path.join(spec_path, "code"), transformer_class="foo.CustomerTransactionsTransformer")
        mock_timestamp_column = TimestampColumn(name="timestamp", format="%s")
        mock_source_delay = DateTimeOffset(1, 2, 3)
        mock_credential = MagicMock(TokenCredential)
        mock_feature_set = MagicMock(FeatureSet)
        mock_feature_store_client.return_value.feature_sets.get.side_effect=mock_feature_set
        mock_feature_set.return_value.get_index_columns.return_value=mock_index_columns
        mock_feature_set.return_value.timestamp_column=mock_timestamp_column
        mock_feature_set.return_value.source.source_delay=mock_source_delay

        # test from config
        fset_spec = FeatureSetSpec.from_config(spec_path=spec_path, credential=mock_credential)

        self.assertEqual(fset_spec.source.type, SourceType.FEATURESET)
        self.assertEqual(fset_spec.source.path, mock_feature_set_arm_id)
        self.assertEqual(fset_spec.index_columns, mock_index_columns)
        self.assertEqual(fset_spec.get_timestamp_column(), ('timestamp', '%s'))
        self.assertEqual(fset_spec.source.source_delay, mock_source_delay)
        self.assertEqual(fset_spec.feature_transformation.path, "./code")
        self.assertEqual(fset_spec.feature_transformation.transformer_class, "foo.CustomerTransactionsTransformer")

        # test create feature set spec
        fset_spec = create_feature_set_spec(
            source=FeatureSetFeatureSource(
                path = mock_feature_set_arm_id
            ),
            features=[Feature(name="f1", type=ColumnType.string), Feature(name="f2", type=ColumnType.string)],
            transformation_code=mock_transformation_code,
            source_lookback=DateTimeOffset(days=7, hours=0, minutes=0),
            temporal_join_lookback=DateTimeOffset(days=1, hours=0, minutes=0),
            infer_schema=False,
            credential=mock_credential,
        )

        self.assertEqual(fset_spec.source.type, SourceType.FEATURESET)
        self.assertEqual(fset_spec.source.path, mock_feature_set_arm_id)
        self.assertEqual(fset_spec.index_columns, mock_index_columns)
        self.assertEqual(fset_spec.get_timestamp_column(), ('timestamp', '%s'))
        self.assertEqual(fset_spec.source.source_delay, mock_source_delay)
        self.assertEqual(fset_spec.feature_transformation.path, mock_transformation_code.path)
        self.assertEqual(fset_spec.feature_transformation.transformer_class, mock_transformation_code.transformer_class)

        # test derived feature set spec load/dump
        temp_folder = uuid.uuid4().hex
        dump_path = os.path.join(gettempdir(), temp_folder)
        fset_spec.dump(dump_path)

        # TODO: Uncomment control plane load test here after control plane version bump
        #fs_spec_contents = read_feature_set_metadata(path=dump_path)
        #fs_spec_yaml_path = Path(dump_path, "FeatureSetSpec.yaml")
        #fspec = FeaturesetSpecMetadata._load(fs_spec_contents, fs_spec_yaml_path)
        shutil.rmtree(dump_path)

        with self.assertRaises(Exception) as e:
            fset_spec = create_feature_set_spec(
                source=FeatureSetFeatureSource(
                    timestamp_column=TimestampColumn(name="timestamp"),
                    path = mock_feature_set_arm_id
                ),
                features=[Feature(name="f1", type=ColumnType.string), Feature(name="f2", type=ColumnType.string)],
                source_lookback=DateTimeOffset(days=7, hours=0, minutes=0),
                temporal_join_lookback=DateTimeOffset(days=1, hours=0, minutes=0),
                infer_schema=False,
                credential=mock_credential,
            )
        self.assertIn("got an unexpected keyword argument 'timestamp_column'", str(e.exception))

        spec_path = os.path.join(os.path.dirname(__file__), "data", "invalid_feature_set_spec_feature_set_source")
        with self.assertRaises(Exception) as e:
            fset_spec = create_feature_set_spec(
                spec_path=spec_path,
                infer_schema=False,
                credential=mock_credential,
            )
        self.assertIn(FEATURE_SET_SOURCE_VALIDATION, str(e.exception))

        with self.assertRaises(Exception) as e:
            fset_spec = create_feature_set_spec(
                source=FeatureSetFeatureSource(
                    timestamp_column=TimestampColumn(name="timestamp"),
                    path = mock_feature_set_arm_id
                ),
                features=[Feature(name="f1", type=ColumnType.string), Feature(name="f2", type=ColumnType.string)],
                source_lookback=DateTimeOffset(days=7, hours=0, minutes=0),
                temporal_join_lookback=DateTimeOffset(days=1, hours=0, minutes=0),
                infer_schema=False,
                credential=mock_credential,
            )
        self.assertIn("got an unexpected keyword argument 'timestamp_column'", str(e.exception))

        with self.assertRaises(Exception) as e:
            fset_spec = create_feature_set_spec(
                source=FeatureSetFeatureSource(
                    path = mock_feature_set_arm_id
                ),
                features=[Feature(name="f1", type=ColumnType.string), Feature(name="f2", type=ColumnType.string)],
                index_columns=[Column(name="customer_id", type=ColumnType.STRING)],
                source_lookback=DateTimeOffset(days=7, hours=0, minutes=0),
                temporal_join_lookback=DateTimeOffset(days=1, hours=0, minutes=0),
                infer_schema=False,
                credential=mock_credential,
            )
        self.assertIn(INVALID_DERIVED_FEATURE_SET, str(e.exception))


    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    @mock.patch("azureml.featurestore.feature_set_spec.FeatureSetSpec.to_spark_dataframe")
    def test_create_feature_set_spec(self, mock_to_spark_dataframe, mock_copy_rename_and_zip):
        from pyspark.sql import DataFrame
        from pyspark.sql.types import FloatType, IntegerType, StringType, StructField, StructType

        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_no_features")
        mock_copy_rename_and_zip.return_value = "./code/test.zip"

        # not infer
        with self.assertRaises(Exception) as e:
            fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        self.assertIn(EMPTY_FEATURE_MESSAGE, str(e.exception))

        # infer
        mock_df = MagicMock(DataFrame)
        mock_to_spark_dataframe.return_value = mock_df
        mock_df.columns = [
            "transactions_6hr_sum",
            "transactions_1day_sum",
            "spend_6hr_sum",
            "spend_1day_sum",
            "customer_id",
            "driver_id",
            "timestamp",
        ]
        mock_df.schema = StructType(
            [
                StructField(name="transactions_6hr_sum", dataType=IntegerType()),
                StructField(name="transactions_1day_sum", dataType=IntegerType()),
                StructField(name="spend_6hr_sum", dataType=FloatType()),
                StructField(name="spend_1day_sum", dataType=FloatType()),
                StructField(name="customer_id", dataType=IntegerType()),
                StructField(name="driver_id", dataType=IntegerType()),
                StructField(name="timestamp", dataType=StringType()),
            ]
        )
        fset_spec = create_feature_set_spec(infer_schema=True, spec_path=spec_path)

        self.assertEqual(fset_spec.source.type, SourceType.MLTABLE)
        self.assertIn("data_sources/customer_transactions/mltable", fset_spec.source.path)
        self.assertEqual(fset_spec.source.timestamp_column.name, "timestamp")
        self.assertEqual(fset_spec.source.timestamp_column.format, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(fset_spec.source.source_delay, DateTimeOffset(days=1, hours=0, minutes=0))

        self.assertEqual(len(fset_spec.index_columns), 2)
        self.assertEqual(len(fset_spec.features), 4)
        self.assertEqual(fset_spec.get_feature(name="transactions_6hr_sum").type, ColumnType.INTEGER)
        self.assertEqual(fset_spec.get_feature(name="transactions_1day_sum").type, ColumnType.INTEGER)
        self.assertEqual(fset_spec.get_feature(name="spend_6hr_sum").type, ColumnType.FLOAT)
        self.assertEqual(fset_spec.get_feature(name="spend_1day_sum").type, ColumnType.FLOAT)

        self.assertEqual(fset_spec.feature_transformation_code.path, "./code")
        self.assertEqual(fset_spec.feature_transformation_code.transformer_class, "foo.CustomerTransactionsTransformer")
        self.assertEqual(fset_spec.source_lookback, DateTimeOffset(days=30, hours=0, minutes=0))
        self.assertEqual(fset_spec.temporal_join_lookback, DateTimeOffset(days=2, hours=0, minutes=0))

        # infer empty
        mock_df.columns = [
            "customer_id",
            "driver_id",
            "timestamp",
        ]
        mock_df.schema = StructType(
            [
                StructField(name="customer_id", dataType=IntegerType()),
                StructField(name="driver_id", dataType=IntegerType()),
                StructField(name="timestamp", dataType=StringType()),
            ]
        )
        with self.assertRaises(Exception) as ve:
            fset_spec = create_feature_set_spec(infer_schema=True, spec_path=spec_path)
        self.assertIn(EMPTY_FEATURE_MESSAGE, str(ve.exception))

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_spec_dump(self, mock_copy_rename_and_zip):
        # test feature set spec with custom feature source dump
        temp_folder = uuid.uuid4().hex
        dump_path = os.path.join(gettempdir(), temp_folder)
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_custom_source")
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        os.makedirs(dump_path)

        fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        fset_spec.dump(dump_path)
        dumped_spec = create_feature_set_spec(infer_schema=False, spec_path=dump_path)

        self.assertEqual(fset_spec.__repr__(), dumped_spec.__repr__())
        shutil.rmtree(dump_path)

        # test feature set spec with mltable feature source dump, create from file
        temp_folder = uuid.uuid4().hex
        dump_path = os.path.join(gettempdir(), temp_folder)
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")
        os.makedirs(dump_path)

        fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        fset_spec.dump(dump_path)
        dumped_spec = create_feature_set_spec(infer_schema=False, spec_path=dump_path)

        self.assertEqual(fset_spec.__repr__(), dumped_spec.__repr__())

        # dump overwrite
        fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        new_source_path = "abfss://container@storage.dfs.core.windows.net/data_sources/customer_transactions/mltable1"
        fset_spec.source.path = new_source_path
        fset_spec.dump(dump_path, overwrite=True)
        dumped_spec = create_feature_set_spec(infer_schema=False, spec_path=dump_path)

        self.assertEqual(dumped_spec.source.path, new_source_path)
        self.assertEqual(dumped_spec.feature_transformation, fset_spec.feature_transformation)

        # dump overwrite not allowed
        fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        with self.assertRaises(Exception) as ex:
            fset_spec.dump(dump_path, overwrite=False)
        self.assertIn("FeatureSetSpec.yaml already exists", str(ex.exception))

        shutil.rmtree(dump_path)

        # load and dump with custom file name
        temp_folder = uuid.uuid4().hex
        dump_path = os.path.join(gettempdir(), temp_folder, "myfeaturesetspec.yaml")
        fset_spec = create_feature_set_spec(
            source=CustomFeatureSource(
                kwargs={"k1": "v1"},
                source_process_code=SourceProcessCode(
                    path=os.path.join(
                        os.path.dirname(__file__), "data", "feature_set_spec_custom_source", "source_process_code"
                    ),
                    process_class="transaction_transform.SourceProcessor",
                ),
                timestamp_column=TimestampColumn(name="timestamp"),
            ),
            transformation_code=TransformationCode(
                path=os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_custom_source", "code"),
                transformer_class="transaction_transform.TransactionFeatureTransformer",
            ),
            index_columns=[Column(name="accountID", type=ColumnType.string)],
            features=[Feature(name="f1", type=ColumnType.DOUBLE)],
            infer_schema=False,
        )
        fset_spec.dump(dump_path)
        dumped_spec = create_feature_set_spec(
            infer_schema=False, spec_path=os.path.join(gettempdir(), temp_folder, FEATURE_SET_SPEC_YAML_FILENAME)
        )
        self.assertEqual(dumped_spec.feature_transformation.path, "./code")
        self.assertEqual(dumped_spec.source.source_process_code.path, "./source_process_code")

        shutil.rmtree(os.path.dirname(dump_path))

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_create_feature_set_spec_constructor_dump(self, mock_copy_rename_and_zip):
        import shutil
        import uuid
        from tempfile import gettempdir

        transactions_featureset_code_path = os.path.join(
            os.path.dirname(__file__), "data", "feature_set_spec_custom_source", "code"
        )
        source_process_code_path = os.path.join(
            os.path.dirname(__file__), "data", "feature_set_spec_custom_source", "source_process_code"
        )

        # test feature set spec with custom feature source dump, create from constructor
        custom_featureset_spec = create_feature_set_spec(
            source=CustomFeatureSource(
                timestamp_column=TimestampColumn(name="timestamp"),
                source_delay=DateTimeOffset(days=0, hours=0, minutes=20),
                source_process_code=SourceProcessCode(
                    path=source_process_code_path, process_class="source_process.MyDataSourceLoader"
                ),
                kwargs={"k1": "v1", "k2": "v2", "k3": "v3"},
            ),
            transformation_code=TransformationCode(
                path=transactions_featureset_code_path,
                transformer_class="transaction_transform.TransactionFeatureTransformer",
            ),
            index_columns=[Column(name="accountID", type=ColumnType.string)],
            features=[Feature(name="f1", type=ColumnType.string), Feature(name="f2", type=ColumnType.string)],
            source_lookback=DateTimeOffset(days=7, hours=0, minutes=0),
            temporal_join_lookback=DateTimeOffset(days=1, hours=0, minutes=0),
            infer_schema=False,
        )

        temp_folder = uuid.uuid4().hex
        custom_dump_path = os.path.join(gettempdir(), temp_folder)
        os.makedirs(custom_dump_path)

        custom_featureset_spec.dump(custom_dump_path)
        # test double dump
        custom_featureset_spec.dump(custom_dump_path, overwrite=True)
        custom_dumped_spec = create_feature_set_spec(infer_schema=False, spec_path=custom_dump_path)
        self.assertEqual(custom_featureset_spec.feature_transformation.path, transactions_featureset_code_path)
        self.assertEqual(custom_featureset_spec.source.source_process_code.path, source_process_code_path)
        custom_featureset_spec.feature_transformation.path = "./code"
        custom_featureset_spec.source.source_process_code.path = "./source_process_code"

        self.assertEqual(custom_featureset_spec.__repr__(), custom_dumped_spec.__repr__())
        shutil.rmtree(custom_dump_path)

        # test feature set spec with parquet feature source dump, create from contructor
        parquet_featureset_spec = create_feature_set_spec(
            source=ParquetFeatureSource(
                path="abfss://test_path",
                timestamp_column=TimestampColumn(name="timestamp"),
                source_delay=DateTimeOffset(days=0, hours=0, minutes=20),
            ),
            transformation_code=TransformationCode(
                path=transactions_featureset_code_path,
                transformer_class="transaction_transform.TransactionFeatureTransformer",
            ),
            index_columns=[Column(name="accountID", type=ColumnType.string)],
            features=[Feature(name="f1", type=ColumnType.string), Feature(name="f2", type=ColumnType.string)],
            source_lookback=DateTimeOffset(days=7, hours=0, minutes=0),
            temporal_join_lookback=DateTimeOffset(days=1, hours=0, minutes=0),
            infer_schema=False,
        )

        temp_folder = uuid.uuid4().hex
        parquet_dump_path = os.path.join(gettempdir(), temp_folder)
        os.makedirs(parquet_dump_path)

        parquet_featureset_spec.dump(parquet_dump_path)
        # test double dump
        parquet_featureset_spec.dump(parquet_dump_path, overwrite=True)
        parquet_dumped_spec = create_feature_set_spec(infer_schema=False, spec_path=parquet_dump_path)
        self.assertEqual(parquet_featureset_spec.feature_transformation.path, transactions_featureset_code_path)
        parquet_featureset_spec.feature_transformation.path = "./code"

        self.assertEqual(parquet_featureset_spec.__repr__(), parquet_dumped_spec.__repr__())
        shutil.rmtree(parquet_dump_path)

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    def test_feature_set_to_pandas_failure(self, mock_copy_rename_and_zip):
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec")
        mock_copy_rename_and_zip.return_value = "./code/test.zip"

        fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        with self.assertRaises(Exception) as e:
            fset_spec._to_pandas_dataframe()
        self.assertIn("On the fly feature sets only supports CUSTOM source type", str(e.exception))

    @mock.patch("azureml.featurestore.contracts.transformation_code.copy_rename_and_zip")
    @mock.patch("azureml.featurestore.feature_set_spec.filter_dataframe")
    @mock.patch("azureml.featurestore.feature_set_spec.feature_transform")
    def test_feature_set_to_pandas(self, mock_feature_transform, mock_filter_dataframe, mock_copy_rename_and_zip):
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_custom_source")
        mock_copy_rename_and_zip.return_value = "./code/test.zip"
        mock_filter_dataframe.return_value = MagicMock(pd.DataFrame)
        mock_feature_transform.return_value = MagicMock(pd.DataFrame)

        fset_spec = create_feature_set_spec(infer_schema=False, spec_path=spec_path)
        fset_spec.source_lookback = DateTimeOffset(1, 0, 0)
        feature_start_time = datetime(2020, 1, 1)
        feature_end_time = datetime(2020, 1, 5)

        fset_spec.source._load_pandas = MagicMock(pd.DataFrame)

        _ = fset_spec._to_pandas_dataframe(
            feature_window_start_date_time=feature_start_time, feature_window_end_date_time=feature_end_time
        )

        self.assertIsInstance(fset_spec.source, CustomFeatureSource)
        fset_spec.source._load_pandas.assert_called_once()
        args, kwargs = fset_spec.source._load_pandas.call_args
        self.assertEqual(feature_start_time - fset_spec.source_lookback.to_timedelta(), kwargs["start_time"])
        self.assertEqual(feature_end_time, kwargs["end_time"])

        mock_filter_dataframe.assert_called_once()
        args, kwargs = mock_filter_dataframe.call_args
        self.assertEqual(feature_start_time, kwargs["feature_window_start_datetime"])
        self.assertEqual(feature_end_time, kwargs["feature_window_end_datetime"])
        self.assertIsNotNone(kwargs["timestamp_column"])
        self.assertIsNotNone(kwargs["timestamp_format"])
        self.assertIsNotNone(kwargs["index_columns"])
        self.assertIsNotNone(kwargs["features"])

        mock_feature_transform.assert_called_once()
        args, kwargs = mock_feature_transform.call_args
        self.assertEqual("true", kwargs[ONLINE_ON_THE_FLY])

    def test_feature_set_spec_dsl(self):
        spec_path = os.path.join(os.path.dirname(__file__), "data", "feature_set_spec_dsl")
        fset_spec = FeatureSetSpec.from_config(spec_path=spec_path)

        self.assertEqual(len(fset_spec.features), 1)
        self.assertEqual(type(fset_spec.feature_transformation), TransformationExpressionCollection)
        self.assertEqual(len(fset_spec.feature_transformation.transformation_expressions), 1)

        # test custom source with dsl
        fset_spec = create_feature_set_spec(
            source=CustomFeatureSource(
                kwargs={"k1": "v1", "k2": "v2", "k3": "v3"},
                timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d %H:%M:%S"),
                source_process_code=SourceProcessCode(
                    path="./source_process_code", process_class="bar.CustomerTransactionsTransformer"
                ),
            ),
            index_columns=[Column(name="accountID", type=ColumnType.STRING)],
            features=[
                Feature(name="f_transaction_3d_count", type=ColumnType.LONG),
            ],
            feature_transformation=TransformationExpressionCollection(
                transformation_expressions=[
                    WindowAggregation(
                        feature_name="f_transaction_3d_count",
                        aggregation="count",
                        window=DateTimeOffset(days=3, hours=1),
                    ),
                ]
            ),
        )

        self.assertEqual(fset_spec.source.type, SourceType.CUSTOM)
        self.assertEqual(len(fset_spec.features), 1)
        self.assertEqual(type(fset_spec.feature_transformation), TransformationExpressionCollection)
        self.assertEqual(len(fset_spec.feature_transformation.transformation_expressions), 1)

        fset_spec = create_feature_set_spec(
            source=FeatureSource(
                type=SourceType.parquet,
                path="wasbs://data@account.blob.core.windows.net/*.parquet",
                timestamp_column=TimestampColumn(name="timestamp"),
            ),
            temporal_join_lookback=DateTimeOffset(1),
            index_columns=[Column(name="accountID", type=ColumnType.string)],
            features=[
                Feature(name="f_transaction_3d_count", type=ColumnType.LONG),
            ],
            feature_transformation=TransformationExpressionCollection(
                transformation_expressions=[
                    WindowAggregation(
                        feature_name="f_transaction_3d_count",
                        aggregation="count",
                        window=DateTimeOffset(days=3, hours=1),
                    ),
                ]
            ),
        )
        self.assertEqual(fset_spec.temporal_join_lookback, DateTimeOffset(1))

        fset_spec = create_feature_set_spec(
            source=FeatureSource(
                type=SourceType.parquet,
                path="wasbs://data@account.blob.core.windows.net/*.parquet",
                timestamp_column=TimestampColumn(name="timestamp"),
            ),
            source_lookback=DateTimeOffset(1, 1, 1),
            index_columns=[Column(name="accountID", type=ColumnType.string)],
            features=[
                Feature(name="f_transaction_3d_count", type=ColumnType.LONG),
            ],
            feature_transformation=TransformationExpressionCollection(
                transformation_expressions=[
                    WindowAggregation(
                        feature_name="f_transaction_3d_count",
                        aggregation="count",
                        window=DateTimeOffset(days=3, hours=1),
                    ),
                ]
            ),
        )
        self.assertEqual(fset_spec.source_lookback, DateTimeOffset(1, 1, 1))

        fset_spec = create_feature_set_spec(
            source=FeatureSource(
                type=SourceType.parquet,
                path="wasbs://data@account.blob.core.windows.net/*.parquet",
                timestamp_column=TimestampColumn(name="timestamp"),
                source_delay=DateTimeOffset(1, 1, 1),
            ),
            index_columns=[Column(name="accountID", type=ColumnType.string)],
            features=[
                Feature(name="f_transaction_3d_count", type=ColumnType.LONG),
            ],
            feature_transformation=TransformationExpressionCollection(
                transformation_expressions=[
                    WindowAggregation(
                        feature_name="f_transaction_3d_count",
                        aggregation="count",
                        window=DateTimeOffset(days=3, hours=1),
                    ),
                ]
            ),
        )
        self.assertEqual(fset_spec.source.source_delay, DateTimeOffset(1, 1, 1))

    def test_feature_set_spec_dsl_validation(self):

        with self.assertRaises(Exception) as ex:
            create_feature_set_spec(
                source=FeatureSource(
                    type=SourceType.parquet,
                    path="wasbs://data@account.blob.core.windows.net/*.parquet",
                    timestamp_column=TimestampColumn(name="timestamp"),
                ),
                temporal_join_lookback=DateTimeOffset(1),
                index_columns=[Column(name="accountID", type=ColumnType.string)],
                features=[
                    Feature(name="f_transaction_3d_count", type=ColumnType.LONG),
                    Feature(name="transactionID", type=ColumnType.LONG),
                ],
                feature_transformation=TransformationExpressionCollection(
                    transformation_expressions=[
                        WindowAggregation(
                            feature_name="f_transaction_3d_count",
                            aggregation="count",
                            window=DateTimeOffset(days=3, hours=1),
                        ),
                    ]
                ),
            )

        self.assertIn(FEATURE_NAME_NOT_FOUND_DSL.format({"transactionID"}), str(ex.exception))

        with self.assertRaises(Exception) as ex:
            create_feature_set_spec(
                source=FeatureSource(
                    type=SourceType.parquet,
                    path="wasbs://data@account.blob.core.windows.net/*.parquet",
                    timestamp_column=TimestampColumn(name="timestamp"),
                ),
                temporal_join_lookback=DateTimeOffset(1),
                index_columns=[Column(name="accountID", type=ColumnType.string)],
                features=[
                    Feature(name="f_transaction_3d_count", type=ColumnType.LONG),
                ],
                feature_transformation=TransformationExpressionCollection(
                    transformation_expressions=[
                        WindowAggregation(
                            feature_name="f_transaction_3d_count",
                            aggregation="count",
                            window=DateTimeOffset(days=3, hours=1),
                        ),
                        WindowAggregation(
                            feature_name="transaction_amount",
                            source_column="transaction_amount",
                            aggregation="latest",
                            window=DateTimeOffset(days=3, hours=1),
                        ),
                    ]
                ),
            )

        self.assertIn(DUPLICATE_DSL_FEATURE_WITH_SOURCE_COLUMN.format("transaction_amount"), str(ex.exception))
