import numpy as np
import pandas as pd
import dagster as dg

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, Iterable, List, Any, Union, Dict, Tuple

from dxtrx.utils.jinja import Jinja2TemplateEngine
from dxtrx.utils.sql import format_sql_multistatement


class SQLBaseResource(dg.ConfigurableResource, ABC):
    """
    Abstract base class for SQL database resources.
    
    This class defines the common interface and shared functionality for
    different SQL database resources like SQLAlchemy and BigQuery.
    
    Implementations should inherit from this class and implement the abstract methods.
    """
    
    @abstractmethod
    def _validate_params(self):
        """
        Validates the connection parameters.
        
        Raises:
            ValueError: If required parameters are missing
        """
        pass
    
    @abstractmethod
    def setup_for_execution(self, context: dg.InitResourceContext):
        """
        Sets up the resource for execution.
        
        Args:
            context: The Dagster initialization context
        """
        pass
    
    def _resolve_full_context(self, run_context: dict) -> dict:
        """
        Resolves the full context for template rendering.
        
        Args:
            run_context: The run context dictionary
            
        Returns:
            dict: The resolved context
        """
        # TODO: Fill with more context
        return run_context
    
    @abstractmethod
    def _resolve_query_or_query_file(self, query: Optional[str], query_file: Optional[str], context: dict, fail_if_multiquery: bool = False) -> List[Any]:
        """
        Resolves a query from either a direct string or a file, and processes it through the template engine.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            context: Context for template rendering
            fail_if_multiquery: Whether to fail if multiple queries are detected
            
        Returns:
            List: List of query objects/strings
            
        Raises:
            ValueError: If neither query nor query_file is provided, or if multiple queries are detected
                      when fail_if_multiquery is True
        """
        pass
    
    @abstractmethod
    def run_query(self, query: Optional[str] = None, query_file: Optional[str] = None, params: Optional[dict] = None) -> bool:
        """
        Executes one or more SQL queries.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            params: Parameters to be used in the query
            
        Returns:
            bool: True if execution was successful
        """
        pass
    
    @abstractmethod
    def get_query_results(self, query: Optional[str] = None, query_file: Optional[str] = None, params: Optional[dict] = None) -> List[Tuple]:
        """
        Executes a query and returns the results.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            params: Parameters to be used in the query
            
        Returns:
            List[Tuple]: List of result rows
        """
        pass
    
    @abstractmethod
    def get_query_results_as_df(self, query: Optional[str] = None, query_file: Optional[str] = None, params: Optional[dict] = None) -> pd.DataFrame:
        """
        Executes a query and returns the results as a pandas DataFrame.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            params: Parameters to be used in the query
            
        Returns:
            DataFrame: Query results as a pandas DataFrame
        """
        pass
    
    @abstractmethod
    def check_if_table_exists(self, table_name: str, **kwargs) -> bool:
        """
        Checks if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            **kwargs: Additional arguments specific to the database implementation
            
        Returns:
            bool: True if the table exists, False otherwise
        """
        pass
    
    @abstractmethod
    def upload_df_to_table(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace", **kwargs):
        """
        Uploads a pandas DataFrame to a database table.
        
        Args:
            df: DataFrame to upload
            table_name: Name of the target table
            if_exists: How to behave if the table exists ('replace', 'append', 'fail')
            **kwargs: Additional arguments specific to the database implementation
        """
        pass
    
    @abstractmethod
    def upload_iterable_to_table(self, iterable: Iterable, table_name: str, **kwargs):
        """
        Uploads an iterable of dictionaries or Pydantic models to a database table.
        
        Args:
            iterable: Collection of items to upload
            table_name: Name of the target table
            **kwargs: Additional arguments specific to the database implementation
            
        Raises:
            ValueError: If items are not dictionaries or Pydantic models
        """
        pass
    
    @abstractmethod
    def upload_single_row_to_table(self, row: dict, table_name: str, **kwargs):
        """
        Uploads a single row to a database table.
        
        Args:
            row: Dictionary containing the row data
            table_name: Name of the target table
            **kwargs: Additional arguments specific to the database implementation
        """
        pass
