"""Utility functions for converting between pandas and polars DataFrames."""

import pandas as pd
import polars as pl
from typing import Union

from .types import DataFrameType, OutputType, DEFAULT_OUTPUT_TYPE


def to_pandas(df: DataFrameType) -> pd.DataFrame:
    """
    Convert a DataFrame to pandas format.
    
    Args:
        df: DataFrame to convert (pandas or polars)
        
    Returns:
        pd.DataFrame: DataFrame in pandas format
    """
    if isinstance(df, pd.DataFrame):
        return df
    elif isinstance(df, pl.DataFrame):
        return df.to_pandas()
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def to_polars(df: DataFrameType) -> pl.DataFrame:
    """
    Convert a DataFrame to polars format.
    
    Args:
        df: DataFrame to convert (pandas or polars)
        
    Returns:
        pl.DataFrame: DataFrame in polars format
    """
    if isinstance(df, pl.DataFrame):
        return df
    elif isinstance(df, pd.DataFrame):
        return pl.from_pandas(df)
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")


def convert_output(df: DataFrameType, output_type: OutputType = DEFAULT_OUTPUT_TYPE) -> DataFrameType:
    """
    Convert DataFrame to the specified output format.
    
    Args:
        df: DataFrame to convert
        output_type: Target output format ("pandas" or "polars")
        
    Returns:
        DataFrameType: DataFrame in the specified format
    """
    if output_type == "pandas":
        return to_pandas(df)
    elif output_type == "polars":
        return to_polars(df)
    else:
        raise ValueError(f"Unsupported output_type: {output_type}")


def ensure_pandas(df: DataFrameType) -> pd.DataFrame:
    """
    Ensure DataFrame is in pandas format for compatibility with pandas-only operations.
    
    Args:
        df: DataFrame to convert
        
    Returns:
        pd.DataFrame: DataFrame in pandas format
    """
    return to_pandas(df)
