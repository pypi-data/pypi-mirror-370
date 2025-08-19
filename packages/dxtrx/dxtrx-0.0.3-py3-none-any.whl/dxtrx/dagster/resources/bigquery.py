import numpy as np
import pandas as pd
import pandas_gbq  # Using pandas-gbq for BigQuery I/O operations (https://pypi.org/project/pandas-gbq/)
import dagster as dg

from dataclasses import field
from pydantic import BaseModel
from typing import Optional, Iterable, List, Tuple
from google.cloud import bigquery
from google.oauth2 import service_account

from dxtrx.utils.jinja import Jinja2TemplateEngine
from dxtrx.utils.sql import format_sql_multistatement
from dxtrx.dagster.resources.sql import SQLBaseResource
from dxtrx.utils.pandas import safe_astype
from dxtrx.utils import json

WRITE_DISPOSITION_MAP = {
    "replace": bigquery.WriteDisposition.WRITE_TRUNCATE,
    "append": bigquery.WriteDisposition.WRITE_APPEND,
    "fail": bigquery.WriteDisposition.WRITE_EMPTY
}

def get_table_schema(df: pd.DataFrame, json_columns: Optional[List[str]] = None) -> List[bigquery.SchemaField]:
    schema = []
    for col in df.columns:
        dtype = df[col].dtype
        if json_columns and col in json_columns:
            field_type = "STRING" # For now, all JSON columns are treated as strings
        elif dtype.kind in {"i"}: 
            field_type = "INTEGER"
        elif dtype.kind in {"f"}:
            field_type = "FLOAT"
        elif dtype.kind in {"b"}:
            field_type = "BOOLEAN"
        elif dtype.kind in {"M"}:
            field_type = "TIMESTAMP"
        else:
            field_type = "STRING"
        schema.append(bigquery.SchemaField(col, field_type, mode="NULLABLE"))
    return schema

class BigQueryResource(SQLBaseResource):
    """
    A configurable BigQuery resource for Google BigQuery operations in Dagster.

    This resource provides a unified interface for connecting to Google BigQuery
    and performing common database operations like running queries and uploading data.

    Attributes:
        project_id: Google Cloud project ID (optional, will use default from credentials if not provided)
        dataset_id: Default BigQuery dataset ID (optional)
        location: BigQuery dataset location (e.g., "US", "EU")
        credentials_path: Path to Google Cloud service account credentials JSON file
        credentials_info: Dictionary containing service account credentials information
        query_timeout: Query timeout in seconds
        extra_client_options: Additional BigQuery client options
    """
    project_id: Optional[str] = None
    dataset_id: Optional[str] = None
    location: Optional[str] = "europe-north1"
    
    credentials_path: Optional[str] = None
    credentials_info: Optional[dict] = None
    
    query_timeout: Optional[int] = 300
    extra_client_options: Optional[dict] = field(default_factory=dict)
            
    def _validate_params(self):
        """
        Validates the connection parameters.
        
        Uses default settings from authenticated account if not explicitly provided.
        """
        # All parameters are optional and will use defaults from the authenticated account
            
    def setup_for_execution(self, context: dg.InitResourceContext):
        """
        Sets up the resource for execution by creating the BigQuery client and logger.
        
        Args:
            context: The Dagster initialization context
        """
        self._logger = dg.get_dagster_logger("bigquery")
        self._validate_params()
        
        client_options = {}
        if self.extra_client_options:
            client_options.update(self.extra_client_options)
            
        client_kwargs = {}
        
        # Add client_options only if not empty
        if client_options:
            client_kwargs["client_options"] = client_options
            
        # Add location as direct parameter to Client constructor
        if self.location:
            client_kwargs["location"] = self.location
            
        # Add project_id to client kwargs if provided
        if self.project_id:
            client_kwargs["project"] = self.project_id
            
        if self.credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            client_kwargs["credentials"] = credentials
            self._client = bigquery.Client(**client_kwargs)
        elif self.credentials_info:
            credentials = service_account.Credentials.from_service_account_info(
                self.credentials_info,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            client_kwargs["credentials"] = credentials
            self._client = bigquery.Client(**client_kwargs)
        else:
            # Use default credentials and project
            self._client = bigquery.Client(**client_kwargs)
            
        # Store the actual project_id being used in a private attribute instead of modifying self.project_id
        self._effective_project_id = self.project_id or self._client.project
            
        self._template_engine = Jinja2TemplateEngine()
    
    def get_client(self) -> bigquery.Client:
        """
        Returns the BigQuery client.
        
        Returns:
            Client: The BigQuery client instance
        """
        return self._client
    
    def _ensure_dataset_exists(self, dataset: str) -> None:
        """
        Ensures that a dataset exists, creating it if it doesn't.
        
        Args:
            dataset: ID of the dataset to ensure exists
        """
        if not dataset:
            raise ValueError("Dataset ID must be provided")
            
        try:
            # For dataset reference, use the effective project ID
            dataset_ref = f"{self._effective_project_id}.{dataset}"
            self._client.get_dataset(dataset_ref)
        except Exception as e:
            self._logger.info(f"Dataset {dataset} does not exist, creating it: {str(e)}")
            dataset_obj = bigquery.Dataset(f"{self._effective_project_id}.{dataset}")
            dataset_obj.location = self.location
            self._client.create_dataset(dataset_obj, exists_ok=True)
    
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
    
    def _resolve_query_or_query_file(self, query: Optional[str], query_file: Optional[str], context: dict, fail_if_multiquery: bool = False, write_dialect: str = "bigquery") -> List[str]:
        """
        Resolves a query from either a direct string or a file, and processes it through the template engine.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            context: Context for template rendering
            fail_if_multiquery: Whether to fail if multiple queries are detected
            write_dialect: Dialect to use for SQL formatting
            
        Returns:
            list: List of query strings
            
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
        queries = format_sql_multistatement(rendered_template_string, read_dialect=write_dialect, write_dialect=write_dialect)

        if len(queries) == 0:
            raise ValueError("No actual queries found in the provided template string")

        if fail_if_multiquery and len(queries) > 1:
            raise ValueError("This operation is not supported for multistatement queries")
        
        return queries

    def run_query(self, query: Optional[str] = None, query_file: Optional[str] = None, params: Optional[dict] = None, write_dialect: str = "bigquery") -> bool:
        """
        Executes one or more SQL queries.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            params: Parameters to be used in the query
            write_dialect: Dialect to use for SQL formatting
            
        Returns:
            bool: True if execution was successful
        """
        queries = self._resolve_query_or_query_file(query, query_file, params, fail_if_multiquery=False, write_dialect=write_dialect)
        self._logger.info(f"Running queries: {queries}")       

        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(key, "STRING", value)
                for key, value in params.items()
            ]

        for query in queries:
            self._logger.info(f"Running query: {query} with params: {params}")
            query_job = self._client.query(query, job_config=job_config)
            query_job.result(timeout=self.query_timeout)  # Wait for query to complete

        return True
    
    def get_query_results(self, query: Optional[str] = None, query_file: Optional[str] = None, params: Optional[dict] = None, write_dialect: str = "bigquery") -> List[Tuple]:
        """
        Executes a query and returns the results.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            params: Parameters to be used in the query
            write_dialect: Dialect to use for SQL formatting
            
        Returns:
            List[Tuple]: List of result rows as tuples
        """
        queries = self._resolve_query_or_query_file(query, query_file, params, fail_if_multiquery=True, write_dialect=write_dialect)
        self._logger.info(f"Getting results from query: {queries[0]}")

        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = [
                bigquery.ScalarQueryParameter(key, "STRING", value)
                for key, value in params.items()
            ]

        query_job = self._client.query(queries[0], job_config=job_config)
        results = query_job.result(timeout=self.query_timeout)
        
        return [tuple(row.values()) for row in results]
    
    def get_query_results_as_df(self, query: Optional[str] = None, query_file: Optional[str] = None, params: Optional[dict] = None, write_dialect: str = "bigquery") -> pd.DataFrame:
        """
        Executes a query and returns the results as a pandas DataFrame.
        
        Args:
            query: The SQL query string
            query_file: Path to a file containing the SQL query
            params: Parameters to be used in the query
            write_dialect: Dialect to use for SQL formatting
            
        Returns:
            DataFrame: Query results as a pandas DataFrame
        """
        queries = self._resolve_query_or_query_file(query, query_file, params, fail_if_multiquery=True, write_dialect="bigquery")
        self._logger.info(f"Getting DataFrame from query: {queries[0]}")

        # Use pandas-gbq to execute query and get results as DataFrame
        read_gbq_kwargs = {
            "query_or_table": queries[0]
        }
        
        if self.location:
            read_gbq_kwargs["location"] = self.location
        
        # Only pass credentials if explicitly defined
        if self.credentials_path or self.credentials_info:
            read_gbq_kwargs["credentials"] = self._client._credentials
        
        # Use effective project ID
        read_gbq_kwargs["project_id"] = self._effective_project_id
            
        return pandas_gbq.read_gbq(**read_gbq_kwargs)
    
    def check_if_table_exists(self, table_name: str, schema: Optional[str] = None) -> bool:
        """
        Checks if a table exists in the specified dataset.
        
        Args:
            table_name: Name of the table to check
            schema: ID of the dataset containing the table (uses default if not specified)
            
        Returns:
            bool: True if the table exists, False otherwise
            
        Raises:
            ValueError: If schema cannot be determined and table_name doesn't include dataset
        """
        # Try to parse the dataset from table_name if it's in format "dataset.table"
        if "." in table_name and not schema:
            parts = table_name.split(".")
            if len(parts) == 2:
                dataset = parts[0]
                table_name = parts[1]
            else:
                dataset = schema or self.dataset_id
        else:
            dataset = schema or self.dataset_id
            
        if not dataset:
            raise ValueError("Must provide 'schema' either in the resource config, method call, or as part of table_name (dataset.table)")
        
        # Create dataset if it doesn't exist
        self._ensure_dataset_exists(dataset)
        
        # Use the effective project ID
        project = self._effective_project_id
        table_ref = f"{project}.{dataset}.{table_name}"
        try:
            self._client.get_table(table_ref)
            return True
        except Exception:
            return False
    
    def upload_df_to_table(self, 
                            df: pd.DataFrame, 
                            table_name: str, 
                            schema: Optional[str] = None,
                            if_exists: str = "replace",
                            clustering_fields: Optional[List[str]] = None,
                            time_partitioning: Optional[bigquery.TimePartitioning] = None,
                            json_columns: Optional[List[str]] = None,
                            override_dtypes: Optional[dict] = {},
                            **kwargs):
        # Determine dataset
        if "." in table_name and not schema:
            parts = table_name.split(".")
            if len(parts) == 2:
                dataset = parts[0]
                table_name = parts[1]
            else:
                dataset = schema or self.dataset_id
        else:
            dataset = schema or self.dataset_id

        if not dataset:
            raise ValueError("Must provide a schema/dataset")

        if "project_id" in kwargs:
            project_id = kwargs["project_id"]
        else:
            project_id = self._effective_project_id

        table_id = f"{project_id}.{dataset}.{table_name}"
        self._logger.debug(f"Uploading df to table '{table_id}'")

        df_to_upload = df.copy()

        # Apply overrides
        for key, dtype in override_dtypes.items():
            if key in df_to_upload.columns:
                df_to_upload[key] = safe_astype(df_to_upload[key], dtype)

        if json_columns:
            for key in json_columns:
                if key in df_to_upload.columns:
                    df_to_upload[key] = df_to_upload[key].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x).astype(str)

        # Generate BigQuery schema
        table_schema = get_table_schema(df_to_upload, json_columns)

        # Create dataset if it doesn't exist
        self._ensure_dataset_exists(dataset)

        # Configure the job
        job_config = bigquery.LoadJobConfig(
            schema=table_schema,
            write_disposition=WRITE_DISPOSITION_MAP[if_exists]
        )

        if clustering_fields:
            job_config.clustering_fields = clustering_fields

        if time_partitioning:
            job_config.time_partitioning = time_partitioning

        # Upload the data
        job = self._client.load_table_from_dataframe(
            dataframe=df_to_upload,
            destination=table_id,
            job_config=job_config
        )

        job.result()  # Wait for completion
        self._logger.info(f"Table uploaded: {table_id}")

    def upload_iterable_to_table(self, 
                                iterable: Iterable, 
                                table_name: str, 
                                schema: Optional[str] = None,
                                if_exists: str = "replace",
                                json_columns: Optional[List[str]] = None,
                                override_dtypes: Optional[dict] = {},
                                **kwargs):
        """
        Uploads an iterable of dictionaries or Pydantic models to a BigQuery table.
        
        Args:
            iterable: Collection of items to upload
            table_name: Name of the target table
            schema: ID of the dataset to use (uses default if not specified)
            if_exists: How to behave if the table exists ('replace', 'append', 'fail')
            json_columns: List of column names to be treated as JSON strings
            override_dtypes: Dictionary mapping column names to custom data types
            **kwargs: Additional parameters passed to upload_df_to_table
            
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
        self.upload_df_to_table(
            df, 
            table_name, 
            schema=schema, 
            if_exists=if_exists, 
            json_columns=json_columns,
            override_dtypes=override_dtypes,
            **kwargs
        )

    def upload_single_row_to_table(self, 
                                  row: dict, 
                                  table_name: str, 
                                  schema: Optional[str] = None,
                                  if_exists: str = "replace",
                                  json_columns: Optional[List[str]] = None,
                                  override_dtypes: Optional[dict] = {},
                                  **kwargs):
        """
        Uploads a single row to a BigQuery table.
        
        Args:
            row: Dictionary containing the row data
            table_name: Name of the target table
            schema: ID of the dataset to use (uses default if not specified)
            if_exists: How to behave if the table exists ('replace', 'append', 'fail')
            json_columns: List of column names to be treated as JSON strings
            override_dtypes: Dictionary mapping column names to custom data types
            **kwargs: Additional parameters passed to upload_df_to_table
        """
        self.upload_df_to_table(
            pd.DataFrame([row]), 
            table_name, 
            schema=schema, 
            if_exists=if_exists, 
            json_columns=json_columns,
            override_dtypes=override_dtypes,
            **kwargs
        ) 