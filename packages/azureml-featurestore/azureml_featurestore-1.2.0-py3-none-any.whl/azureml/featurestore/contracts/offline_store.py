# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from azureml.featurestore._feature_set import FeatureSet
from azureml.featurestore.contracts.store_connection import OfflineStoreType

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class OfflineStore(ABC):
    def __init__(self, *, target: str, connection_name: str) -> None:
        self.__target = target
        self.__connection_name = connection_name

    @abstractmethod
    def read_data(
        self,
        feature_set: FeatureSet,
        feature_window_start_time: datetime = None,
        feature_window_end_time: datetime = None,
    ) -> "DataFrame":
        pass

    @abstractmethod
    def write_data(
        self,
        feature_set: FeatureSet,
        df: "DataFrame",
        feature_window_start_time: datetime = None,
        feature_window_end_time: datetime = None,
        **kwargs,
    ) -> int:
        pass

    @abstractmethod
    def validate_data(
        self,
        feature_set: FeatureSet,
        feature_window_start_time: datetime = None,
        feature_window_end_time: datetime = None,
        **kwargs,
    ) -> "DataFrame":
        pass

    @property
    def connection_name(self):
        return self.__connection_name

    @property
    def target(self):
        return self.__target


class OfflineStoreFactory:
    @staticmethod
    def make_offline_store(
        offline_store_type: OfflineStoreType, offline_store_target: str, connection_name: str, location: str = None
    ) -> OfflineStore:
        if offline_store_type == OfflineStoreType.AZURE_DATA_LAKE_GEN2:
            from azureml.featurestore.offline_store.azure_data_lake_offline_store import AzureDataLakeOfflineStore

            return AzureDataLakeOfflineStore(
                target=offline_store_target, connection_name=connection_name, location=location
            )

        raise NotImplementedError(f"Offline store type:{offline_store_type.name} is not supported")
