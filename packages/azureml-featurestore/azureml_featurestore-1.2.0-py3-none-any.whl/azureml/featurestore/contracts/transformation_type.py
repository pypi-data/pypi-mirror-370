# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.ai.ml._utils._experimental import experimental
from azure.core import CaseInsensitiveEnumMeta


@experimental
class TransformationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Transformation type of a feature set"""

    DSL = "dsl"
    UDF = "udf"
