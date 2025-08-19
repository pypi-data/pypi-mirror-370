import pandas as pd

from typing import List

def standardize_column_names(columns: List[str]) -> List[str]:
    """
    Standardize column names by converting them to lowercase and only keeping alphanumeric characters.
    
    Args:
        columns: A list of column names to standardize

    Returns:
        List[str]: A list of standardized column names
    """
    return pd.Series(columns).str.lower().str.replace(r"[^a-z0-9]", "", regex=True).tolist()

def clean_text_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
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
        pd.DataFrame: A new DataFrame with the cleaned text column
    """
    df = df.copy()
    df[column] = df[column].str.lower()
    df[column] = df[column].str.replace(r'[^\w\s]', ' ', regex=True)
    df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
    df[column] = df[column].str.strip()
    return df
