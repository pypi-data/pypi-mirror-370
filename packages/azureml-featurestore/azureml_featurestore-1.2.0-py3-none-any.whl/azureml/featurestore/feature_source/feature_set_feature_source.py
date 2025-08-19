# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from azureml.featurestore.contracts.feature_source_type import SourceType

from azure.core.credentials import TokenCredential

from .simple_feature_source import SimpleFeatureSource

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class FeatureSetFeatureSource(SimpleFeatureSource):
    """A derived feature set feature source
    :param path: The source data path
    :type path: str, required
    """

    def __init__(self, *, path: str):
        super().__init__(path=path)
        self.type = SourceType.FEATURESET
        self.__feature_set = None
        self.__credential = None

    @property
    def feature_set(self):
        return self.__feature_set

    def _initialize(self, credential: Optional[TokenCredential] = None):
        from azureml.featurestore import FeatureStoreClient
        from azureml.featurestore._utils.arm_id_utils import FeatureSetVersionedUri

        from azure.ai.ml.identity import AzureMLOnBehalfOfCredential

        if not credential:
            credential = AzureMLOnBehalfOfCredential()
        self.__credential = credential

        uri = FeatureSetVersionedUri(uri=self.path)
        feature_store_client = FeatureStoreClient(
            credential=self.__credential,
            subscription_id=uri.subscription_id,
            resource_group_name=uri.resource_group_name,
            name=uri.workspace_name,
        )
        self.__feature_set = feature_store_client.feature_sets.get(
            name=uri.featureset_name, version=uri.featureset_version
        )
        self.timestamp_column = self.__feature_set.timestamp_column
        self.source_delay = self.__feature_set.source.source_delay

    def _load(self, start_time: datetime = None, end_time: datetime = None, **kwargs) -> "DataFrame":
        credential = kwargs.pop("credential", None)
        if credential and credential != self.__credential or not self.__feature_set:
            self._initialize(credential=credential)

        df = self.__feature_set.to_spark_dataframe(
            feature_window_start_date_time=start_time, feature_window_end_date_time=end_time
        )

        return df

    def __repr__(self):
        formatted_info = ", ".join(["{}: {}".format(k, v) for k, v in self._to_dict().items()])
        return "FeatureSetFeatureSource({})".format(formatted_info)
