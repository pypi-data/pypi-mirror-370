# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from enum import Enum
from typing import Union

from azure.core import CaseInsensitiveEnumMeta


class OfflineStoreType(Enum, metaclass=CaseInsensitiveEnumMeta):
    """Represents online store type for offline store connections."""

    AZURE_DATA_LAKE_GEN2 = 1


class OnlineStoreType(Enum, metaclass=CaseInsensitiveEnumMeta):
    """Represents online store type for online store connections."""

    REDIS = 1


class AbstractStoreConnection(ABC):
    """Represents the base class for all store connections.

    :param type: store type
    :type type: str, required
    :param target: store url
    :type target: str, required
    """

    def __init__(self, type: Union[OfflineStoreType, OnlineStoreType], target):  # pylint: disable=redefined-builtin
        """Represents the base class for all store connections.

        :param type: store type
        :type type: str, required
        :param target: store url
        :type target: str, required
        """

        self.type = type
        self.target = target
