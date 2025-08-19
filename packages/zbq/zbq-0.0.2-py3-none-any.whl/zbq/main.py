from polars.exceptions import PolarsError
from google.cloud import bigquery
from zbq.base import BaseClientManager, ZbqAuthenticationError, ZbqOperationError
from typing import Literal, Union, List
import polars as pl
import re
import tempfile
import os
from typing import Dict, Any
from datetime import datetime, date


class BigQueryHandler(BaseClientManager):
    """Enhanced Google BigQuery handler with improved error handling and logging"""

    def __init__(
        self,
        project_id: str = "",
        default_timeout: int = 300,
        log_level: str = "INFO",
    ):
        super().__init__(project_id, log_level)
        self.default_timeout = default_timeout

    def _create_client(self):
        return bigquery.Client(project=self.project_id)

    def _build_job_config(
        self, parameters: Dict[str, Any] | None = None
    ) -> bigquery.QueryJobConfig:
        """
        Build BigQuery QueryJobConfig with properly typed parameters.
        
        This replaces the vulnerable string substitution approach with BigQuery's
        native parameterized queries, eliminating SQL injection vulnerabilities.

        Args:
            parameters: Dictionary mapping parameter names to values

        Returns:
            QueryJobConfig with typed query parameters

        Raises:
            ZbqOperationError: If parameter configuration fails
        """
        job_config = bigquery.QueryJobConfig()
        
        if not parameters:
            return job_config

        # Validate parameters dict
        if not isinstance(parameters, dict):
            raise ZbqOperationError("Parameters must be a dictionary")

        # Validate parameter names (only alphanumeric and underscore allowed)
        for param_name in parameters.keys():
            if not isinstance(param_name, str) or not re.match(r"^\w+$", param_name):
                raise ZbqOperationError(
                    f"Invalid parameter name: '{param_name}'. Parameter names must contain only letters, numbers, and underscores."
                )

        try:
            query_parameters = []
            
            for param_name, param_value in parameters.items():
                # Skip table identifiers and conditions - these need special handling
                if param_name in ['table', 'table_name', 'condition']:
                    # Log warning about deprecated/unsafe parameters
                    self.logger.warning(
                        f"Parameter '{param_name}' cannot be safely parameterized. "
                        f"Consider using explicit table names in your query."
                    )
                    continue
                    
                bq_param = self._create_bigquery_parameter(param_name, param_value)
                if bq_param:
                    query_parameters.append(bq_param)
                    
            job_config.query_parameters = query_parameters
            return job_config

        except Exception as e:
            raise ZbqOperationError(f"Parameter configuration failed: {str(e)}")
            
    def _create_bigquery_parameter(
        self, name: str, value: Any
    ) -> Union[bigquery.ScalarQueryParameter, bigquery.ArrayQueryParameter, None]:
        """
        Create appropriate BigQuery parameter based on value type.
        
        Args:
            name: Parameter name
            value: Parameter value
            
        Returns:
            BigQuery parameter object or None if unsupported type
        """
        if value is None:
            return bigquery.ScalarQueryParameter(name, "STRING", None)
        elif isinstance(value, bool):
            return bigquery.ScalarQueryParameter(name, "BOOL", value)
        elif isinstance(value, int):
            return bigquery.ScalarQueryParameter(name, "INT64", value)
        elif isinstance(value, float):
            return bigquery.ScalarQueryParameter(name, "FLOAT64", value)
        elif isinstance(value, str):
            return bigquery.ScalarQueryParameter(name, "STRING", value)
        elif isinstance(value, (datetime, date)):
            return bigquery.ScalarQueryParameter(name, "TIMESTAMP", value)
        elif isinstance(value, (list, tuple)):
            if not value:  # Empty list
                return bigquery.ArrayQueryParameter(name, "STRING", [])
                
            # Determine array type from first non-None element
            first_val = next((v for v in value if v is not None), None)
            if first_val is None:
                array_type = "STRING"
            elif isinstance(first_val, bool):
                array_type = "BOOL"
            elif isinstance(first_val, int):
                array_type = "INT64"
            elif isinstance(first_val, float):
                array_type = "FLOAT64"
            elif isinstance(first_val, str):
                array_type = "STRING"
            elif isinstance(first_val, (datetime, date)):
                array_type = "TIMESTAMP"
            else:
                # Convert unknown types to strings
                array_type = "STRING"
                value = [str(v) if v is not None else None for v in value]
                
            return bigquery.ArrayQueryParameter(name, array_type, value)
        else:
            # Convert unknown types to string
            return bigquery.ScalarQueryParameter(name, "STRING", str(value))
            
    def _process_table_identifiers(self, query: str, parameters: Dict[str, Any] | None = None) -> str:
        """
        Safely handle table identifier substitution (non-parameterizable).
        
        This is a separate, validated approach for table names which cannot be
        parameterized in BigQuery but need special handling.
        
        Args:
            query: SQL query string
            parameters: Dictionary that may contain table identifiers
            
        Returns:
            Query with table identifiers safely substituted
            
        Raises:
            ZbqOperationError: If table identifier validation fails
        """
        if not parameters:
            return query
            
        result_query = query
        table_params = ['table', 'table_name']
        
        for param_name in table_params:
            if param_name in parameters:
                table_value = parameters[param_name]
                if not isinstance(table_value, str):
                    raise ZbqOperationError(f"Table identifier '{param_name}' must be a string")
                    
                # Validate table identifier format
                if not self._validate_table_identifier(table_value):
                    raise ZbqOperationError(
                        f"Invalid table identifier: '{table_value}'. "
                        f"Must be in format 'project.dataset.table' or 'dataset.table'"
                    )
                    
                # Add backticks if needed
                if '.' in table_value and not table_value.startswith('`'):
                    safe_table = f"`{table_value}`"
                else:
                    safe_table = table_value
                    
                # Replace in query
                result_query = result_query.replace(f"@{param_name}", safe_table)
                
        return result_query
        
    def _validate_table_identifier(self, identifier: str) -> bool:
        """
        Validate that a table identifier is safe and properly formatted.
        
        Args:
            identifier: Table identifier string
            
        Returns:
            True if valid, False otherwise
        """
        # Remove backticks for validation
        clean_id = identifier.strip('`')
        
        # Basic pattern: project.dataset.table or dataset.table
        pattern = r'^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)?$'
        
        if not re.match(pattern, clean_id):
            return False
            
        # Check for dangerous characters or SQL keywords
        dangerous_chars = [';', '--', '/*', '*/', "'", '"', '\\', '\n', '\r']
        for char in dangerous_chars:
            if char in identifier:
                return False
                
        return True

    def _validate(self):
        """Internal helper: raise if ADC or project_id not set"""
        if not self._check_adc():
            raise RuntimeError(
                "Missing ADC. Run: gcloud auth application-default login"
            )
        if not self.project_id:
            raise RuntimeError("Project ID not set.")

    def read(
        self,
        query: str | None = None,
        timeout: int | None = None,
        parameters: Dict[str, Any] | None = None,
        dry_run: bool = False,
    ):
        """
        Execute a SQL query and return results as a Polars DataFrame.

        Args:
            query (str): SQL query string. Can include @param_name placeholders.
            timeout (int, optional): Query timeout in seconds. Uses default_timeout if not specified.
            parameters (Dict[str, Any], optional): Parameters for @param_name substitution in query.
            dry_run (bool, optional): If True, prints the final query after parameter substitution without executing it.

        Returns:
            pl.DataFrame: Query results as a Polars DataFrame, or None if dry_run is True.

        Raises:
            ValueError: If query is empty.
            ZbqOperationError: If parameter substitution fails.
            TimeoutError: If query times out.
        """

        if query:
            try:
                return self._query(query, timeout, parameters, dry_run)
            except TimeoutError as e:
                print(f"Read operation timed out: {e}")
                raise
            except Exception as e:
                print(f"Read operation failed: {e}")
                raise
        else:
            raise ValueError("Query is empty.")

    def insert(
        self,
        query: str,
        timeout: int | None = None,
        parameters: Dict[str, Any] | None = None,
        dry_run: bool = False,
    ):
        return self.read(query, timeout, parameters, dry_run)

    def update(
        self,
        query: str,
        timeout: int | None = None,
        parameters: Dict[str, Any] | None = None,
        dry_run: bool = False,
    ):
        return self.read(query, timeout, parameters, dry_run)

    def delete(
        self,
        query: str,
        timeout: int | None = None,
        parameters: Dict[str, Any] | None = None,
        dry_run: bool = False,
    ):
        return self.read(query, timeout, parameters, dry_run)

    def write(
        self,
        df: pl.DataFrame,
        full_table_path: str,
        write_type: str = "append",
        warning: bool = True,
        create_if_needed: bool = True,
        timeout: int | None = None,
    ):
        self._check_requirements(df, full_table_path)
        return self._write(
            df, full_table_path, write_type, warning, create_if_needed, timeout
        )

    def _check_requirements(self, df, full_table_path):
        if df.is_empty() or not full_table_path:
            missing = []
            if df.is_empty():
                missing.append("df")
            if not full_table_path:
                missing.append("full_table_path")
            raise ValueError(f"Missing required argument(s): {', '.join(missing)}")

    def _query(
        self,
        query: str,
        timeout: int | None = None,
        parameters: Dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> pl.DataFrame | pl.Series | None:
        timeout = timeout or self.default_timeout

        # Build job config with parameters
        job_config = self._build_job_config(parameters)
        
        # Handle table identifiers separately (cannot be parameterized)
        processed_query = self._process_table_identifiers(query, parameters)

        # If dry_run is enabled, print the final query and return None
        if dry_run:
            print("DRY RUN - Query that would be executed:")
            print("-" * 50)
            print(f"Query: {processed_query}")
            if job_config.query_parameters:
                print("Parameters:")
                for param in job_config.query_parameters:
                    # Get parameter type name safely
                    param_type = getattr(param.type_, 'name', str(param.type_))
                    print(f"  @{param.name} ({param_type}): {param.value}")
            print("-" * 50)
            return None

        try:
            # Use fresh client for each query to eliminate shared state issues
            with self._fresh_client() as client:
                query_job = client.query(processed_query, job_config=job_config)

                if re.search(r"\b(insert|update|delete)\b", query, re.IGNORECASE):
                    try:
                        query_job.result(timeout=timeout)
                        return pl.DataFrame(
                            {"status": ["OK"], "job_id": [query_job.job_id]}
                        )
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            raise TimeoutError(
                                f"Query timed out after {timeout} seconds"
                            )
                        raise

                try:
                    rows = query_job.result(timeout=timeout).to_arrow(
                        progress_bar_type=None
                    )
                    df = pl.from_arrow(rows)
                except Exception as e:
                    if "timeout" in str(e).lower():
                        raise TimeoutError(f"Query timed out after {timeout} seconds")
                    raise

        except PolarsError as e:
            print(f"PanicException: {e}")
            print("Retrying with Pandas DF")
            try:
                with self._fresh_client() as client:
                    query_job = client.query(processed_query, job_config=job_config)
                    pandas_df = query_job.result(timeout=timeout).to_dataframe(
                        progress_bar_type=None
                    )
                    df = pl.from_pandas(pandas_df)
            except Exception as e:
                if "timeout" in str(e).lower():
                    raise TimeoutError(f"Query timed out after {timeout} seconds")
                raise

        return df

    def _write(
        self,
        df: pl.DataFrame,
        full_table_path: str,
        write_type: str = "append",
        warning: bool = True,
        create_if_needed: bool = True,
        timeout: int | None = None,
    ):
        timeout = timeout or self.default_timeout
        destination = full_table_path
        temp_file = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        try:
            df.write_parquet(temp_file_path)

            if write_type == "truncate" and warning:
                try:
                    user_warning = input(
                        "You are about to overwrite a table. Continue? (y/n): "
                    )
                    if user_warning.lower() != "y":
                        return "CANCELLED"
                except (EOFError, KeyboardInterrupt):
                    print("\nOperation cancelled by user")
                    return "CANCELLED"

            write_disp = (
                bigquery.WriteDisposition.WRITE_TRUNCATE
                if write_type == "truncate"
                else bigquery.WriteDisposition.WRITE_APPEND
            )

            create_disp = (
                bigquery.CreateDisposition.CREATE_IF_NEEDED
                if create_if_needed
                else bigquery.CreateDisposition.CREATE_NEVER
            )

            # Use fresh client for write operation to eliminate shared state issues
            with self._fresh_client() as client:
                with open(temp_file_path, "rb") as source_file:
                    job = client.load_table_from_file(
                        source_file,
                        destination=destination,
                        project=self.project_id,
                        job_config=bigquery.LoadJobConfig(
                            source_format=bigquery.SourceFormat.PARQUET,
                            write_disposition=write_disp,
                            create_disposition=create_disp,
                        ),
                    )
                    # Add timeout to prevent hanging on job.result()
                    try:
                        result = job.result(timeout=timeout)
                        return result.state
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            raise TimeoutError(
                                f"Write operation timed out after {timeout} seconds"
                            )
                        raise

        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass  # Ignore cleanup errors
