import numpy as np
import pandas as pd
import dagster as dg

from dataclasses import field
from pydantic import BaseModel
from typing import Optional, Iterable, List, Tuple, Any
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.expression import TextClause, text

from dxtrx.utils.jinja import Jinja2TemplateEngine
from dxtrx.utils.sql import format_sql_multistatement, ORJSONType
from dxtrx.dagster.resources.sql import SQLBaseResource

FILELIKE_DB_PROTOCOLS = ["sqlite", "duckdb"]
COMMON_DB_PROTOCOLS = ["postgresql"]

class SqlAchemyResource(SQLBaseResource):
    """
    A configurable SQLAlchemy resource for database operations in Dagster.

    This resource provides a unified interface for connecting to different types of databases
    and performing common database operations like running queries and uploading data.

    Attributes:
        protocol: Database protocol (postgresql, sqlite, duckdb)
        url: Complete database URL (alternative to individual connection parameters)
        
        user: Database username
        password: Database password
        host: Database host address
        port: Database port
        database: Database name
        
        file_path: Path to database file (for SQLite/DuckDB)
        
        extra_url_params: Additional URL parameters
        extra_sqla_params: Additional SQLAlchemy parameters
        
        autoflush: Whether to autoflush SQLAlchemy sessions
    """
    protocol: Optional[str] = "postgresql"
    url: Optional[str] = None
    
    user: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    database: Optional[str] = None
    
    file_path: Optional[str] = None

    extra_url_params: Optional[str] = None
    extra_sqla_params: Optional[dict] = field(default_factory=dict)

    autoflush: Optional[bool] = True
            
    def _validate_params(self):
        """
        Validates the connection parameters.
        """
        if self.protocol in FILELIKE_DB_PROTOCOLS:
            self._validate_filelike_db_params()
        elif self.protocol in COMMON_DB_PROTOCOLS:
            self._validate_common_db_params()
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")
            

    def _validate_filelike_db_params(self):
        """
        Validates separated connection parameters for file-based databases (SQLite/DuckDB).
        
        Raises:
            ValueError: If required parameters are missing or if both URL and individual parameters are provided
        """
        if self.protocol not in ["sqlite", "duckdb"]:
            raise ValueError(f"Unsupported protocol for checking filelike db params: {self.protocol}. This method should only be used for file-based databases.")
        
        if not self.file_path:
            raise ValueError("Must provide 'file_path' when using 'sqlite' or 'duckdb' protocol")
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")
        
    def _validate_common_db_params(self):
        """
        Validates the connection parameters for common databases (PostgreSQL).
        
        Raises:
            ValueError: If required parameters are missing or if both URL and individual parameters are provided
        """
        if self.protocol not in ["postgresql"]:
            raise ValueError(f"Unsupported protocol for checking common db params: {self.protocol}. This method should only be used for common databases.")
        
        if not self.user or not self.password or not self.host or not self.port or not self.database:
            raise ValueError("Must provide both 'user', 'password', 'host', 'port', 'database'")
        

    def _build_url_according_to_protocol(self):
        """
        Constructs the database URL based on the specified protocol.
        
        Returns:
            str: The constructed database URL
            
        Raises:
            ValueError: If an unsupported protocol is specified
        """
        if self.protocol == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.protocol in FILELIKE_DB_PROTOCOLS:
            return f"{self.protocol}:///{self.file_path}" # TODO: Check if this respects relative/absolute paths
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def get_engine_url(self) -> str:
        """
        Gets the database engine URL after validating parameters.
        
        Returns:
            str: The database URL to be used for creating the engine
        """
        if not self.url:
            self._logger.info("No database URL provided, building URL according to protocol")
            self._validate_params()
            url = self._build_url_according_to_protocol()
        else:
            url = self.url
            self._logger.info(f"Using provided database URL: {url}") # TODO: Obfuscate the URL

        return url

    def setup_for_execution(self, context: dg.InitResourceContext):
        """
        Sets up the resource for execution by creating the SQLAlchemy engine and logger.
        
        Args:
            context: The Dagster initialization context
        """
        self._logger = dg.get_dagster_logger("sqlalchemy")
        
        self._engine = create_engine(self.get_engine_url(), **self.extra_sqla_params)
        self._template_engine = Jinja2TemplateEngine()

    def get_session(self) -> Session:
        """
        Creates and returns a new SQLAlchemy session.
        
        Returns:
            Session: A new SQLAlchemy session
        """
        SessionLocal = sessionmaker(autoflush=self.autoflush, bind=self._engine)
        return SessionLocal()
    
    def get_engine(self) -> Engine:
        """
        Returns the SQLAlchemy engine.
        
        Returns:
            Engine: The SQLAlchemy engine instance
        """
        return self._engine
    
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
    
    def _resolve_query_or_query_file(self, query: Optional[str], query_file: Optional[str], context: dict, fail_if_multiquery: bool = False) -> List[TextClause]:
        """
        Resolves a query from either a direct string or a file, and processes it through the template engine.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            context: Context for template rendering
            fail_if_multiquery: Whether to fail if multiple queries are detected
            
        Returns:
            list: List of SQLAlchemy text objects representing the queries
            
        Raises:
            ValueError: If neither query nor query_file is provided, or if multiple queries are detected
                      when fail_if_multiquery is True
        """
        if query:
            template_string = query
        elif query_file:
            with open(query_file, "rt") as f:
                template_string = f.read()
        else:
            raise ValueError("Must provide either 'query' or 'query_file'")
        
        rendered_template_string = self._template_engine.render_string(template_string, self._resolve_full_context(context))
        queries = format_sql_multistatement(rendered_template_string)

        if len(queries) == 0:
            raise ValueError("No actual queries found in the provided template string")

        if fail_if_multiquery and len(queries) > 1:
            raise ValueError("This operation is not supported for multistatement queries")
        
        return [text(q) for q in queries]

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
        queries = self._resolve_query_or_query_file(query, query_file, params, fail_if_multiquery=False)
        self._logger.info(f"Running queries: {[str(q) for q in queries]}")       

        # TODO: Allow them to run in the same session
        for query in queries:
            session = self.get_session()
            self._logger.info(f"Running query: {query} with params: {params}")

            result = session.execute(query, params)
            session.commit()
            session.close()

        # TODO: Return more details
        return True
    
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
        queries = self._resolve_query_or_query_file(query, query_file, params, fail_if_multiquery=True)
        self._logger.info(f"Getting results from query: {queries[0]}")

        session = self.get_session()
        result = session.execute(queries[0], params)
        rows = result.fetchall()
        session.close()

        return rows
    
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
        return pd.DataFrame(self.get_query_results(query=query, query_file=query_file, params=params))
    
    def check_if_table_exists(self, table_name: str, schema: str = "public") -> bool:
        """
        Checks if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            schema: Database schema name
            
        Returns:
            bool: True if the table exists, False otherwise
            
        Raises:
            ValueError: If an unsupported protocol is used
        """
        if self.protocol == "postgresql":
            query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table_name}');"
        elif self.protocol == "sqlite":
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")
        
        result = self.get_query_results(query=query)[0]

        return bool(result[0])
    
    def upload_df_to_table(self, 
                           df: pd.DataFrame, 
                           table_name: str, 
                           if_exists: str = "replace", 
                           schema: str = "public",
                           json_columns: Optional[list[str]] = [],
                           override_dtypes: Optional[dict] = {}):
        """
        Uploads a pandas DataFrame to a database table.
        
        Args:
            df: DataFrame to upload
            table_name: Name of the target table
            if_exists: How to behave if the table exists ('replace', 'append', 'fail')
            schema: Database schema name
            json_columns: List of column names that should be treated as JSON
            override_dtypes: Dictionary mapping column names to custom data types
        """
        self._logger.debug(f"Uploading df to table '{schema}.{table_name}' with params: if_exists={if_exists}, json_columns={json_columns}")

        final_df = df.copy()

        # Configure JSON column types
        dtypes = {
            key: ORJSONType
            for key in json_columns
        }

        # Apply custom data types
        for key, dtype in override_dtypes.items():
            if key in final_df.columns:
                final_df[key] = final_df[key].astype(dtype)

        final_df.to_sql(table_name, self._engine, if_exists=if_exists, index=False, schema=schema, dtype=dtypes)

    def upload_iterable_to_table(self, iterable: Iterable, table_name: str, schema: str = "public", json_columns: Optional[list[str]] = [], override_dtypes: Optional[dict] = {}):
        """
        Uploads an iterable of dictionaries or Pydantic models to a database table.
        
        Args:
            iterable: Collection of items to upload
            table_name: Name of the target table
            schema: Database schema name
            json_columns: List of column names that should be treated as JSON
            override_dtypes: Dictionary mapping column names to custom data types
            
        Raises:
            ValueError: If items are not dictionaries or Pydantic models
        """
        items = []
        for item in iterable:
            if isinstance(item, dict):
                items.append(item)
            elif isinstance(item, BaseModel):
                items.append(item.model_dump())
            else:
                raise ValueError(f"Item is not a dict nor BaseModel: {item}")

        df = pd.DataFrame(items, columns=items[0].keys()).replace({None: np.nan})

        self.upload_df_to_table(df, table_name, schema=schema, json_columns=json_columns, override_dtypes=override_dtypes)

    def upload_single_row_to_table(self, row: dict, table_name: str, schema: str = "public", json_columns: Optional[list[str]] = [], override_dtypes: Optional[dict] = {}):
        """
        Uploads a single row to a database table.
        
        Args:
            row: Dictionary containing the row data
            table_name: Name of the target table
            schema: Database schema name
            json_columns: List of column names that should be treated as JSON
            override_dtypes: Dictionary mapping column names to custom data types
        """
        self.upload_df_to_table(pd.DataFrame([row]), table_name, schema=schema, json_columns=json_columns, override_dtypes=override_dtypes)