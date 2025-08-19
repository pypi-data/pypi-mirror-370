import unittest

import pytest
from azureml.featurestore._utils.error_constants import (
    CUSTOM_SOURCE_VALIDATION,
    FEATURE_SET_SOURCE_VALIDATION,
    SIMPLE_SOURCE_VALIDATION,
)
from azureml.featurestore.contracts import SourceType, TimestampColumn

from azure.ai.ml.exceptions import ValidationException


@pytest.mark.unittest
class FeaturSourceFactoryTest(unittest.TestCase):
    def test_feature_source_factory(self):
        from azureml.featurestore.contracts.transformation_code import SourceProcessCode
        from azureml.featurestore.feature_source import CustomFeatureSource, DeltaTableFeatureSource
        from azureml.featurestore.feature_source.feature_source_factory import FeatureSourceFactory

        feature_source_factory = FeatureSourceFactory(
            type=SourceType.DELTATABLE,
            path="delta_table_path",
            timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d %H:%M:%S"),
        )

        delta_source = feature_source_factory.build_feature_source()

        assert type(delta_source) == DeltaTableFeatureSource
        assert delta_source.path == "delta_table_path"

        feature_source_factory = FeatureSourceFactory(
            type=SourceType.CUSTOM,
            timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d %H:%M:%S"),
            kwargs={"k1": "v1", "k2": "v2"},
            source_process_code=SourceProcessCode(path="test_path", process_class="test_class"),
        )

        custom_source = feature_source_factory.build_feature_source()

        assert type(custom_source) == CustomFeatureSource
        assert feature_source_factory.kwargs == custom_source.kwargs
        assert feature_source_factory.source_process_code.path == "test_path"
        assert feature_source_factory.source_process_code.process_class == "test_class"

        with self.assertRaises(ValidationException) as ve:
            feature_source_factory = FeatureSourceFactory(
                type=SourceType.DELTATABLE,
                path="delta_table_path",
                timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d %H:%M:%S"),
                kwargs={"k1": "v1", "k2": "v2"},
                source_process_code=SourceProcessCode(path="test_path", process_class="test_class"),
            )
        self.assertTrue(SIMPLE_SOURCE_VALIDATION.format("deltaTable") in ve.exception.__repr__())

        with self.assertRaises(ValidationException) as ve:
            feature_source_factory = FeatureSourceFactory(
                type=SourceType.FEATURESET,
                kwargs={"k1": "v1", "k2": "v2"},
            )
            self.assertTrue(SIMPLE_SOURCE_VALIDATION.format(SourceType.FEATURE_SET) in ve.exception.__repr__())

        with self.assertRaises(ValidationException) as ve:
            feature_source_factory = FeatureSourceFactory(
                type=SourceType.CUSTOM,
                path="delta_table_path",
                timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d %H:%M:%S"),
            )
        self.assertTrue(CUSTOM_SOURCE_VALIDATION in ve.exception.__repr__())

        with self.assertRaises(ValidationException) as ve:
            feature_source_factory = FeatureSourceFactory(
                type=SourceType.FEATURESET,
                path="mock_feature_set_arm_id",
                timestamp_column=TimestampColumn(name="timestamp", format="%Y-%m-%d %H:%M:%S"),
            )
            self.assertTrue(FEATURE_SET_SOURCE_VALIDATION.format(SourceType.FEATURESET) in ve.exception.__repr__())
