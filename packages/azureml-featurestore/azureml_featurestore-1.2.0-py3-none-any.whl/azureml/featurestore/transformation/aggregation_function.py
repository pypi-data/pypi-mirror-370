# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.ai.ml._utils._experimental import experimental
from azure.core import CaseInsensitiveEnumMeta


@experimental
class AggregationFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """AggregationFunction types to be specified when using TransformationExpression."""

    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    LATEST = "latest"
