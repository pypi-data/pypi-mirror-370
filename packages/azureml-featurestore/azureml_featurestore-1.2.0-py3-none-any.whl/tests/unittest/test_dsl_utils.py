import unittest

import pytest
from azureml.featurestore import create_feature_set_spec
from azureml.featurestore._utils.dsl_utils import (
    _to_feathr_anchor_config,
    _to_feathr_join_config,
    _to_feathr_source_config,
)
from azureml.featurestore.contracts import (
    Column,
    ColumnType,
    DateTimeOffset,
    FeatureSource,
    SourceType,
    TimestampColumn,
)
from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.transformation import TransformationExpressionCollection, WindowAggregation


@pytest.mark.unittest
class DslUtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feature_set_spec = create_feature_set_spec(
            source=FeatureSource(
                type=SourceType.parquet,
                path="abfss://testing-bits@featurestoretestadlsgen2",
                timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d"),
            ),
            index_columns=[Column(name="id", type=ColumnType.INTEGER)],
            features=[Feature(name="f_f1", type=ColumnType.DOUBLE)],
            feature_transformation=TransformationExpressionCollection(
                transformation_expressions=[
                    WindowAggregation(
                        feature_name="f_f1", source_column="f1", aggregation="sum", window=DateTimeOffset(days=1)
                    )
                ]
            ),
        )

    def test_to_anchor_config(self):
        expected_anchor_name = f"{self.feature_set_spec.name}_1_anchor"
        expected_source_name = f"{self.feature_set_spec.name}_1_source"
        expected = f"""
"{expected_anchor_name}": {{
    source: {expected_source_name}
    key: [id]
    features: {{
            
f_f1: {{
    def: f1
    aggregation: SUM
    window: 1d
}}
    }}
}}"""
        output = _to_feathr_anchor_config(self.feature_set_spec, [self.feature_set_spec.index_columns[0].name])
        self.assertEqual(expected, output)

    def test_to_feathr_join_config(self):
        expected = """
settings: {
    observationDataTimeSettings: {
        absoluteTimeRange: {
            startTime: "2020-01-01"
            endTime: "2020-01-02"
            timeFormat: "yyyy-MM-dd HH:mm:ss"
        }
    },
    joinTimeSettings: {
        timestampColumn: {
            def: "timestamp"
            format: "%Y-%m-%d"
        }
    }
}
features: [
    {
        key: [id, region],
        featureList: [f1, f2]
    }
]"""
        output = _to_feathr_join_config(
            timestamp_col_format="%Y-%m-%d",
            timestamp_col_name="timestamp",
            feature_names=["f1", "f2"],
            join_keys=["id", "region"],
            start_time="2020-01-01",
            end_time="2020-01-02",
        )
        self.assertEqual(expected, output)

    def test_to_feathr_source_config(self):
        expected_source_name = f"{self.feature_set_spec.name}_1_source"
        expected = f"""
"{expected_source_name}": {{
    location: {{path: "abfss://testing-bits@featurestoretestadlsgen2"}}
    timeWindowParameters: {{
        timestampColumn: "timestamp"
        timestampColumnFormat: "%Y-%m-%d"
    }}
    
}}"""

        output = _to_feathr_source_config(self.feature_set_spec)
        self.assertEqual(expected, output)
