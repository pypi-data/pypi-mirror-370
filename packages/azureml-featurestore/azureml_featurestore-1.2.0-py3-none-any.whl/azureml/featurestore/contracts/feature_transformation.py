# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC, abstractmethod


class FeatureTransformation(ABC):
    """Represents the base class for all feature transformations.
    You should not work with this class directly.
    """

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
