# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.ai.ml._utils._experimental import experimental
from azure.core import CaseInsensitiveEnumMeta


@experimental
class JoinType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Join type of a feature set"""

    EQUAL_TIME = "equalTimeJoin"
    POINT_AT_TIME = "pointAtTimeJoin"
