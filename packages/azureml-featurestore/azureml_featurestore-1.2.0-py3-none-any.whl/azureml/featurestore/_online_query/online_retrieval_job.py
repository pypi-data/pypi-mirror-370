# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    import pyarrow


class OnlineRetrievalJob(ABC):
    @abstractmethod
    def to_pandas_dataframe(self) -> "pd.DataFrame":
        pass

    @abstractmethod
    def to_pyarrow_table(self) -> "pyarrow.Table":
        pass
