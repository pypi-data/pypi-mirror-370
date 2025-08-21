"""Module containing SQLSource class.

SQLSource class handles loading of data from SQL databases.
"""

from __future__ import annotations

from importlib.resources import open_text
import json
import logging
from typing import Any, Iterator, Optional, cast, overload

import pandas as pd
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from typing_extensions import override

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.exceptions import DataSourceError, ElevatedPermissionsError
from bitfount.data.types import SingleOrMulti
from bitfount.types import _JSONDict
from bitfount.utils import delegates

logger = logging.getLogger(__name__)


class _ReadOnlyPermissionsValidator:
    """Validator for SQL connection read-only permissions."""

    @classmethod
    def validate(cls, conn: Connection, dialect_name: str) -> None:
        """Validate the connection has read-only permissions.

        Args:
            conn: The SQLAlchemy connection to validate.
            dialect_name: The SQLAlchemy dialect name of the connection.

        Raises:
            ElevatedPermissionsError: If the connection is detected to have write
                privileges (e.g. INSERT/UPDATE/DELETE) for supported SQL
                dialects.
        """
        if dialect_name == "postgresql":
            cls._validate_postgresql(conn)
        elif dialect_name in {"mysql", "mariadb"}:
            cls._validate_mysql(conn)
        elif dialect_name == "mssql":
            cls._validate_mssql(conn)
        elif dialect_name == "oracle":
            cls._validate_oracle(conn)
        else:
            logger.warning(
                f"Read-only permission check not implemented for SQL dialect "
                f"'{dialect_name}'. Skipping enforcement."
            )

    @staticmethod
    def _validate_postgresql(conn: Connection) -> None:
        """Validate the connection has read-only permissions for PostgreSQL."""
        # For PostgreSQL, check if the session is in read-only mode
        try:
            # Check if the current transaction is read-only
            result = conn.execute(text("SHOW transaction_read_only"))
            transaction_readonly = result.scalar()

            if transaction_readonly != "on":
                # Also check if the database itself is read-only
                result = conn.execute(text("SELECT pg_is_in_recovery()"))
                is_in_recovery = result.scalar()

                if not is_in_recovery:
                    # If neither transaction nor database is read-only,
                    # check if user has actual write permissions by
                    # trying to create a table
                    try:
                        conn.execute(
                            text("CREATE TEMPORARY TABLE test_readonly_check (id int)")
                        )
                        conn.execute(text("DROP TABLE test_readonly_check"))
                        # If we get here, user has write permissions
                        raise ElevatedPermissionsError(
                            "PostgreSQL connection has write permissions. "
                            "Please connect using a read-only role or set "
                            "default_transaction_read_only=on."
                        )
                    except SQLAlchemyError:
                        # User cannot create tables, this is good (read-only)
                        pass
        except SQLAlchemyError:
            # If we can't check transaction_read_only, fall back to the
            # write test
            try:
                conn.execute(
                    text("CREATE TEMPORARY TABLE test_readonly_check (id int)")
                )
                conn.execute(text("DROP TABLE test_readonly_check"))
                # If we get here, user has write permissions
                raise ElevatedPermissionsError(
                    "PostgreSQL connection has write permissions. "
                    "Please connect using a read-only role."
                )
            except SQLAlchemyError:
                # User cannot create tables, likely read-only - this is
                # acceptable
                pass

    @staticmethod
    def _validate_mysql(conn: Connection) -> None:
        """Validate the connection has read-only permissions for MySQL."""
        # For MySQL/MariaDB, check if the session or database is read-only
        try:
            # Check if the session is in read-only mode
            result = conn.execute(text("SELECT @@session.transaction_read_only"))
            session_readonly = result.scalar()

            if session_readonly != 1:
                # Also check if the database is read-only
                result = conn.execute(text("SELECT @@read_only"))
                db_readonly = result.scalar()

                if db_readonly != 1:
                    # If neither session nor database is read-only,
                    # try to create a temporary table to verify permissions
                    try:
                        conn.execute(
                            text("CREATE TEMPORARY TABLE test_readonly_check (id int)")
                        )
                        conn.execute(text("DROP TEMPORARY TABLE test_readonly_check"))
                        # If we get here, user has write permissions
                        raise ElevatedPermissionsError(
                            "MySQL/MariaDB connection has write permissions. "
                            "Please connect using a read-only user or set "
                            "transaction_read_only=1."
                        )
                    except SQLAlchemyError:
                        # User cannot create tables, likely read-only - this is
                        # acceptable
                        pass
        except SQLAlchemyError:
            # If we can't check the read-only settings, fall back to the
            # original test
            try:
                conn.execute(
                    text("CREATE TEMPORARY TABLE test_readonly_check (id int)")
                )
                conn.execute(text("DROP TEMPORARY TABLE test_readonly_check"))
                # If we get here, user has write permissions
                raise ElevatedPermissionsError(
                    "MySQL/MariaDB connection has write permissions. "
                    "Please connect using a read-only user."
                )
            except SQLAlchemyError:
                # User cannot create tables, likely read-only - this is
                # acceptable
                pass

    @staticmethod
    def _validate_mssql(conn: Connection) -> None:
        """Validate the connection has read-only permissions for SQL Server."""
        # SQL Server readonly checking: try multiple approaches
        readonly_verified = False

        # Approach 1: Check if database is in read-only state
        try:
            read_only_val = conn.execute(
                text("SELECT DATABASEPROPERTYEX(DB_NAME(), 'Updateability')")
            ).scalar()
            if str(read_only_val).upper() == "READ_ONLY":
                readonly_verified = True
                logger.info("SQL Server database is in READ_ONLY state")
            else:
                logger.debug(
                    "SQL Server database is not in READ_ONLY state, "
                    "checking user permissions"
                )
        except SQLAlchemyError as e:
            logger.debug(f"Could not check database updateability: {e}")

        # Approach 2: If database is not read-only, test user's actual
        # write permissions
        if not readonly_verified:
            try:
                # Try to create a table - this should fail for read-only users
                conn.execute(text("CREATE TABLE test_readonly_check_mssql (id INT)"))
                conn.execute(text("DROP TABLE test_readonly_check_mssql"))
                # If we get here, user has write permissions
                raise ElevatedPermissionsError(
                    "SQL Server connection has write permissions. "
                    "Please connect using a user with only SELECT "
                    "privileges or set the database to READ-only state."
                )
            except SQLAlchemyError:
                # User cannot create tables, this indicates read-only
                # permissions
                readonly_verified = True
                logger.info(
                    "SQL Server user verified as read-only (cannot create tables)"
                )

        if not readonly_verified:
            raise ElevatedPermissionsError(
                "Unable to verify SQL Server connection is read-only. "
                "Please ensure the user has only SELECT privileges or "
                "the database is in read-only state."
            )

    @staticmethod
    def _validate_oracle(conn: Connection) -> None:
        """Validate the connection has read-only permissions for Oracle."""
        # Oracle readonly checking: try multiple approaches
        readonly_verified = False

        # Approach 1: Try to check database open mode via V$DATABASE
        try:
            open_mode_val = conn.execute(
                text("SELECT open_mode FROM v$database")
            ).scalar()
            if open_mode_val is not None:
                open_mode_upper = str(open_mode_val).upper()
                logger.info(f"Oracle database open mode: {open_mode_upper}")
                if "READ ONLY" in open_mode_upper or "MOUNTED" in open_mode_upper:
                    readonly_verified = True
                else:
                    raise ElevatedPermissionsError(
                        "Oracle database is in READ WRITE mode. For security, "
                        "please connect using a read-only database or a user "
                        "with restricted privileges."
                    )
        except SQLAlchemyError as e:
            logger.debug(f"Could not check v$database (may lack privileges): {e}")
            # Approach 2: Test user's actual write permissions
            try:
                # Try to create a table - this should fail for read-only users
                conn.execute(
                    text("CREATE TABLE test_readonly_check_oracle (id NUMBER)")
                )
                conn.execute(text("DROP TABLE test_readonly_check_oracle"))
                # If we get here, user has write permissions
                raise ElevatedPermissionsError(
                    "Oracle connection has write permissions. "
                    "Please connect using a user with only SELECT privileges "
                    "or a read-only database."
                )
            except SQLAlchemyError:
                # User cannot create tables, this indicates read-only
                # permissions
                readonly_verified = True
                logger.info("Oracle user verified as read-only (cannot create tables)")

        if not readonly_verified:
            raise ElevatedPermissionsError(
                "Unable to verify Oracle connection is read-only. "
                "Please ensure the user has only SELECT privileges."
            )


@delegates()
class _SQLSource(BaseSource):
    """Base class for SQL data sources.

    This datasource allows you to connect to any SQL database supported by SQLAlchemy
    and stream results from queries. The query results are treated as a single
    "table" view, maintaining consistency with other datasources.

    Args:
        connection_string: SQLAlchemy connection string (e.g.,
            "postgresql://user:pass@localhost/db" or "sqlite:///path/to/db.sqlite")
        read_sql_kwargs: Additional arguments to be passed to `pandas.read_sql`.
            Defaults to None.
        **kwargs: Additional arguments passed to BaseSource.
    """

    def __init__(
        self,
        connection_string: str,
        read_sql_kwargs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.connection_string = connection_string

        if not read_sql_kwargs:
            read_sql_kwargs = {}
        self.read_sql_kwargs = read_sql_kwargs

        # Initialize query-related attributes
        self._query: Optional[str] = None
        self._query_params: Optional[dict[str, Any]] = None

        # Validate connection on initialization
        self._validate_connection()

    def _validate_connection(self) -> None:
        """Validate the database connection.

        Raises:
            DataSourceError: If the connection cannot be established.
            ElevatedPermissionsError: If the connection is detected to have write
                privileges (e.g. INSERT/UPDATE/DELETE) for supported SQL
                dialects.
        """
        try:
            engine = create_engine(self.connection_string)
            with engine.connect() as conn:
                # Test the connection with a simple query
                # Use dialect-specific test queries
                dialect_name = engine.dialect.name.lower()
                if dialect_name == "oracle":
                    conn.execute(text("SELECT 1 FROM DUAL"))
                else:
                    conn.execute(text("SELECT 1"))

                # Validate read-only permissions
                self._check_readonly_permissions(conn, dialect_name)

            # Set the engine if validation was successful
            self._engine = engine
        except SQLAlchemyError as e:
            raise DataSourceError(
                f"Failed to connect to database with connection string: {self.connection_string}. "  # noqa: E501
                f"Error: {e}"
            ) from e
        except ElevatedPermissionsError as e:
            logger.error(
                "Database connection has write permissions. "
                "Please connect using a read-only role or set "
                "default_transaction_read_only=on."
            )
            raise e

    def _check_readonly_permissions(self, conn: Connection, dialect_name: str) -> None:
        """Ensure the active connection has read-only permissions.

        Args:
            conn: An active SQLAlchemy connection.
            dialect_name: The SQLAlchemy dialect name of the connection.

        Raises:
            ElevatedPermissionsError: If the connection is detected to have write
                privileges (e.g. INSERT/UPDATE/DELETE) for supported SQL
                dialects.
            DataSourceError: If the read-only permissions validation fails for any
                reason.
        """
        try:
            _ReadOnlyPermissionsValidator.validate(conn, dialect_name)
        except ElevatedPermissionsError as e:
            # Re-raise the exception since we know the read-only
            # permissions are not valid
            raise e
        except Exception as e:
            # This is a fallback in case the read-only permissions
            # validation fails for any reason
            raise DataSourceError(
                f"Failed to validate read-only permissions for dialect "
                f"'{dialect_name}': {e}"
            ) from e

    def execute_query(
        self,
        query: str,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """Execute a SQL query and return the results as a DataFrame.

        Args:
            query: SQL query to execute.
            **kwargs: Additional arguments to be passed to `pandas.read_sql`.

        Returns:
            DataFrame containing the query results.
        """
        read_sql_kwargs = {**self.read_sql_kwargs, **kwargs}

        try:
            with self._engine.connect() as conn:
                df = pd.read_sql(query, conn, **read_sql_kwargs)
                return cast(pd.DataFrame, df)
        except Exception as e:
            raise DataSourceError(
                f"Failed to execute SQL query: {query}. Error: {e}"
            ) from e

    def set_query(self, query: str) -> None:
        """Set the query to be used for data retrieval."""
        self._query = query

    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy engine."""
        return self._engine

    @override
    def get_data(
        self,
        data_keys: SingleOrMulti[str] | SingleOrMulti[int],
        *,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> Optional[pd.DataFrame]:
        """Get data using the set query.

        Args:
            data_keys: String or integer based indices for which rows should be
                returned.
            use_cache: Whether to use cached data if available.
            **kwargs: Additional keyword arguments.

        Returns:
            DataFrame containing the selected rows or None if no data is returned.
        """
        data = self._get_data(data_keys, use_cache=use_cache, **kwargs)

        for hook in self._hooks:
            try:
                hook.on_datasource_get_data(data)
            except NotImplementedError:
                logger.debug(
                    f"{hook.hook_name} does not implement `on_datasource_get_data`."
                )
            except Exception as e:
                logger.error(f"Error in hook {hook.hook_name}: {e}")

        if not data.empty:
            return data
        else:
            return None

    def _get_data(
        self,
        data_keys: SingleOrMulti[str] | SingleOrMulti[int],
        *,
        use_cache: bool = True,
        **kwargs: bool,
    ) -> pd.DataFrame:
        """Loads and returns selected data from the SQL query.

        Rows whose index matches the data keys are returned.

        Args:
            data_keys: String or integer based indices for which rows should be
                returned.
            use_cache: Whether to use cached data if available.
            **kwargs: Additional keyword arguments.

        Returns:
            DataFrame containing the selected rows.
        """
        if self._query is None:
            raise DataSourceError("No query has been set. Call set_query() first.")

        df = self.execute_query(self._query, **kwargs)

        # Filter by data_keys if provided
        if data_keys is not None:
            data_keys = self._convert_to_multi(data_keys)

            # Handle different index types
            index_type = df.index.inferred_type
            if index_type == "integer":
                df = df.loc[df.index.intersection([int(i) for i in data_keys])]
            else:
                df = df.loc[df.index.intersection([str(s) for s in data_keys])]

        # Apply modifiers and ignore columns
        df = self.apply_modifiers(df)
        df = self.apply_ignore_cols(df)

        return df

    @override
    def yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str] | SingleOrMulti[int]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        """Generator for providing data chunkwise from the SQL query.

        Args:
            data_keys: String or integer based indices for which rows should be
                returned.
            use_cache: Whether to use cached data if available.
            partition_size: Size of each partition to yield.
            **kwargs: Additional keyword arguments.

        Yields:
            DataFrame chunks containing the selected data.
        """
        yield from self._yield_data(
            data_keys=data_keys,
            use_cache=use_cache,
            partition_size=partition_size,
            **kwargs,
        )

    def _yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str] | SingleOrMulti[int]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        """Generator for providing data chunkwise from the SQL query.

        Args:
            data_keys: String or integer based indices for which rows should be
                returned.
            use_cache: Whether to use cached data if available.
            partition_size: Size of each partition to yield.
            **kwargs: Additional keyword arguments.

        Yields:
            DataFrame chunks containing the selected data.
        """
        if self._query is None:
            raise DataSourceError("No query has been set. Call set_query() first.")

        if data_keys is not None:
            data_keys = self._convert_to_multi(data_keys)

        partition_size_: int
        if partition_size:
            partition_size_ = partition_size
        else:
            partition_size_ = self.partition_size

        try:
            with self._engine.connect() as conn:
                # Use pandas read_sql with chunksize for streaming
                df_iter = pd.read_sql(
                    self._query,
                    conn,
                    params=self._query_params,
                    chunksize=partition_size_,
                    **self.read_sql_kwargs,
                )
        except Exception as e:
            raise DataSourceError(
                f"Failed to execute SQL query: {self._query}. Error: {e}"
            ) from e

        df: pd.DataFrame
        for df in df_iter:
            # Fast-continue if nothing
            if df.empty:
                continue

            # Filter by data_keys if provided
            if data_keys is not None:
                index_type = df.index.inferred_type
                if index_type == "integer":
                    df = df.loc[df.index.intersection([int(i) for i in data_keys])]
                else:
                    df = df.loc[df.index.intersection([str(s) for s in data_keys])]

                # Fast-continue if nothing remaining after filtering
                if df.empty:
                    continue

            # Apply modifiers and ignore columns
            df = self.apply_modifiers(df)
            df = self.apply_ignore_cols(df)

            if not df.empty:
                yield df

    @staticmethod
    @overload
    def _convert_to_multi(
        som: SingleOrMulti[str],
    ) -> list[str]: ...

    @staticmethod
    @overload
    def _convert_to_multi(
        som: SingleOrMulti[int],
    ) -> list[int]: ...

    @staticmethod
    def _convert_to_multi(
        som: SingleOrMulti[str] | SingleOrMulti[int],
    ) -> list[str] | list[int]:
        """Convert single or multi value to list."""
        # If already a list, return unchanged
        if isinstance(som, list):
            return som
        # If it's a string, wrap in list
        elif isinstance(som, str):
            return [som]
        # If it's an int, wrap in list
        elif isinstance(som, int):
            return [som]
        # If it's some other sequence (tuple, etc.), convert to list
        else:
            # At this point, som must be a sequence of either str or int
            # We use cast to help mypy understand the type
            return cast(list[str] | list[int], list(som))

    def __len__(self) -> int:
        """Return the total number of rows in the query result."""
        if self._query is None:
            return 0

        try:
            with self._engine.connect() as conn:
                # Use COUNT(*) to get the total number of rows efficiently
                count_query = (
                    f"SELECT COUNT(*) as count FROM ({self._query}) as subquery"  # nosec: B608
                )
                result = pd.read_sql(count_query, conn, params=self._query_params)
                return int(result.iloc[0]["count"])
        except Exception as e:
            logger.warning(f"Could not determine length of SQL result: {e}")
            return 0


class OMOPSource(_SQLSource):
    """Data source for connecting to OMOP databases.

    The Observational Medical Outcomes Partnership (OMOP) datasource is specifically
    designed for OMOP Common Data Model databases. The chosen version determines the
    schema of the database displayed in the Bitfount Hub.

    Args:
        connection_string: SQLAlchemy connection string to the OMOP database.
        version: OMOP CDM version. Must be one of "v3.0", "v5.3", or "v5.4".
        read_sql_kwargs: Additional arguments to be passed to `pandas.read_sql`.
            Defaults to None.
        **kwargs: Additional arguments passed to BaseSource.
    """

    SUPPORTED_VERSIONS = ["v3.0", "v5.3", "v5.4"]
    has_predefined_schema: bool = True

    def __init__(
        self,
        connection_string: str,
        version: str,
        read_sql_kwargs: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        if version not in self.SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported OMOP version: {version}. "
                f"Supported versions: {self.SUPPORTED_VERSIONS}"
            )

        super().__init__(
            connection_string=connection_string,
            read_sql_kwargs=read_sql_kwargs,
            **kwargs,
        )
        self.version = version

    def get_schema(self) -> _JSONDict:
        """Get the pre-defined OMOP schema for this datasource's version.

        Returns:
            The OMOP schema as a JSON dictionary.

        Raises:
            DataSourceError: If the schema file cannot be opened or parsed.
            FileNotFoundError: If the schema file doesn't exist for this version.
            ValueError: If the version is not supported.
        """
        if self.version not in self.SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported OMOP version: {self.version}. "
                f"Supported versions: {self.SUPPORTED_VERSIONS}"
            )

        # Convert version to filename format (e.g., "v3.0" -> "30")
        version_number = self.version.replace("v", "").replace(".", "")
        schema_filename = f"omop_schema_{version_number}.json"

        try:
            # Use importlib.resources.open_text to access the schema file.
            # This is the best way to access a resource as part of an installed package
            with open_text(
                "bitfount.schemas.omop", schema_filename, encoding="utf-8"
            ) as schema_file:
                return cast(_JSONDict, json.load(schema_file))
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"OMOP schema file not found: {schema_filename}"
            ) from e
        except (ImportError, AttributeError) as e:
            raise DataSourceError(
                f"Could not access OMOP schema file {schema_filename}: {e}"
            ) from e
