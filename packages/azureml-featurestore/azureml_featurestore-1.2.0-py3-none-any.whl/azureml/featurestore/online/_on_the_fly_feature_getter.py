# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List

import pyarrow
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore._online_query import PointAtTimeOnTheFlyRetrievalJob
from azureml.featurestore._utils._constants import PACKAGE_NAME
from azureml.featurestore._utils.utils import _build_logger
from azureml.featurestore.contracts.feature import Feature

ops_logger = _build_logger(__name__)


@experimental
class OnTheFlyFeatureGetter:
    """Feature getter for on the fly feature sets"""

    def __init__(self, credential, initial_features: List[Feature], on_the_fly_feature_sets: List[FeatureSet]):
        self.credential = credential
        self.initial_features = initial_features
        self.on_the_fly_feature_sets = on_the_fly_feature_sets

        self.initial_feature_map = {}
        for feature in initial_features:
            self.initial_feature_map[feature.uri] = feature

    @monitor_with_activity(ops_logger, f"{PACKAGE_NAME}->GetOnTheFlyFeatures", ActivityType.INTERNALCALL)
    def get_on_the_fly_features(
        self, feature_uris: List[str], observation_df: pyarrow.Table, on_the_fly_entities: str = None, **kwargs
    ) -> pyarrow.Table:
        features_map = self._get_features_to_fetch(feature_uris)

        observation_df_pandas = observation_df.to_pandas()

        job = PointAtTimeOnTheFlyRetrievalJob(
            features_map=features_map,
            observation_data=observation_df_pandas,
            on_the_fly_entities=on_the_fly_entities,
            **kwargs,
        )

        return job.to_pyarrow_table()

    def _get_features_to_fetch(self, feature_uris: List[str]) -> Dict[FeatureSet, List[str]]:
        features_map = {}
        for feature_uri in feature_uris:
            if feature_uri not in self.initial_feature_map:
                msg = "Feature uri not part of init list"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )

            feature = self.initial_feature_map[feature_uri]
            if feature.feature_set_reference not in self.on_the_fly_feature_sets:
                msg = "Feature uri not part of on the fly feature set list"
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.FEATURE_SET,
                    error_category=ErrorCategory.USER_ERROR,
                )

            if feature.feature_set_reference not in features_map:
                features_map[feature.feature_set_reference] = [feature.name]
            else:
                features_map[feature.feature_set_reference].append(feature.name)

        return features_map
