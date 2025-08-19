# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=client-method-missing-type-annotations,no-self-use

from typing import List

from azure.identity import DeviceCodeCredential

from azureml.featurestore.contracts.feature import Feature
from azureml.featurestore.online._online_feature_getter_v3 import OnlineFeatureGetterV3


class InlineFeatureRetrievalClient:
    # pylint: disable=unused-argument
    def get_online_features(self, features: List[Feature], observation_df: "pandas.DataFrame", **kwargs):
        feature_uris = [feature.uri for feature in features]
        online_feature_getter = OnlineFeatureGetterV3(DeviceCodeCredential())
        return online_feature_getter.get_online_features(feature_uris, observation_df)

    def get_offline_features(
        self, features: List[Feature], observation_df: "pyspark.sql.DataFrame", timestamp_column: str
    ):
        raise NotImplementedError()
