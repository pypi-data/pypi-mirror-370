# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod

from azure.ai.ml._utils._experimental import experimental

@experimental
class TransformationExpression(ABC):
    """Feature transformation expression representation"""

    @abstractmethod
    def _to_feathr_config(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
