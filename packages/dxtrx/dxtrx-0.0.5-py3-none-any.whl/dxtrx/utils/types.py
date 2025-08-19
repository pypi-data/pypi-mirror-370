"""Common type definitions for the dxtrx package."""

import pandas as pd
import polars as pl
from typing import Union, Literal

# DataFrame types
DataFrameType = Union[pd.DataFrame, pl.DataFrame]
OutputType = Literal["pandas", "polars"]

# Default output type
DEFAULT_OUTPUT_TYPE: OutputType = "polars"
