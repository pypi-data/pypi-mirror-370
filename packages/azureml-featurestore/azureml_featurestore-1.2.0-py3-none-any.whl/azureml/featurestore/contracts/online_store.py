# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.featurestore.contracts.store_connection import OnlineStoreType


class OnlineStore:
    def __init__(self, target: str, type: OnlineStoreType, connection_name: str) -> None:  # pylint: disable=redefined-builtin
        self.__target = target
        self.__type = type
        self.__connection_name = connection_name

    @property
    def target(self):
        return self.__target

    @property
    def type(self):
        return self.__type

    @property
    def connection_name(self):
        return self.__connection_name


class OnlineStoreFactory:
    @staticmethod
    def make_online_store(
        online_store_type: OnlineStoreType, online_store_target: str, connection_name: str
    ) -> OnlineStore:
        return OnlineStore(target=online_store_target, type=online_store_type, connection_name=connection_name)
