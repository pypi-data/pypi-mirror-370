import pandas as pd
import polars as pl

from typing import List

from .types import DataFrameType
from .dataframe_conversion import ensure_pandas, to_polars, convert_output

def standardize_column_names(columns: List[str]) -> List[str]:
    """
    Standardize column names by converting them to lowercase and only keeping alphanumeric characters.
    
    Args:
        columns: A list of column names to standardize

    Returns:
        List[str]: A list of standardized column names
    """
    # This function doesn't need DataFrame type support since it operates on a list
    return pd.Series(columns).str.lower().str.replace(r"[^a-z0-9]", "", regex=True).tolist()

def clean_text_column(df: DataFrameType, column: str) -> DataFrameType:
    """
    Clean text data in a specified column by:
    - Converting to lowercase
    - Replacing non-alphanumeric characters with spaces
    - Replacing multiple spaces with a single space
    - Stripping leading and trailing spaces
    
    Args:
        df: The DataFrame containing the text column to clean
        column: The name of the column to clean

    Returns:
        DataFrameType: A new DataFrame with the cleaned text column (same type as input)
    """
    if isinstance(df, pd.DataFrame):
        result_df = df.copy()
        result_df[column] = result_df[column].str.lower()
        result_df[column] = result_df[column].str.replace(r'[^\w\s]', ' ', regex=True)
        result_df[column] = result_df[column].str.replace(r'\s+', ' ', regex=True)
        result_df[column] = result_df[column].str.strip()
        return result_df
    elif isinstance(df, pl.DataFrame):
        return df.with_columns([
            pl.col(column)
            .str.to_lowercase()
            .str.replace_all(r'[^\w\s]', ' ')
            .str.replace_all(r'\s+', ' ')
            .str.strip_chars()
            .alias(column)
        ])
    else:
        raise TypeError(f"Unsupported DataFrame type: {type(df)}")
