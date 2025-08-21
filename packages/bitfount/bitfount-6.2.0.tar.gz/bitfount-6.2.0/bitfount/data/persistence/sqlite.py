"""A data persistance implementation backed by an SQLite database."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
import logging
import os.path
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
from pandas.io.sql import (  # type: ignore[attr-defined] # Reason: the module _does_ have this class defined, it's just not meant for public accessibility # noqa: E501
    SQLDatabase as PandasSQLDatabase,
    SQLTable as PandasSQLTable,
)
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    inspect,
    select,
    text,
)
from sqlalchemy.event import listen
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import (
    DeclarativeMeta,
    Mapped,
    declarative_mixin,
    declared_attr,
    mapped_column,
    registry,
    relationship,
    sessionmaker,
)

from bitfount import config
from bitfount.data.exceptions import DataCacheError
from bitfount.data.persistence.base import BulkResult, DataPersister

# As the logs from cache interaction may be large, a specific flag is provided to
# control whether debug logging is enabled within this module specifically.
#
# Note that setting this flag will also cause the SQL to be output in the logs.
_logger = logging.getLogger(__name__)
if not config.settings.logging.data_cache_debug:
    _logger.setLevel(logging.INFO)

_CACHE_INFO_TABLE = "cache_info"
_CACHED_DATA_TABLE = "cached_data"


##########################
# SQLAlchemy ORM Classes #
##########################
@declarative_mixin
class CacheInfoTableBase:
    """Cache information entry ORM.

    Represents the table in the database that corresponds to cache validity
    information. In particular, stores the primary key of the cache, `file`,
    which is the canonical path of the file in question, and the time the cache
    was last updated for that file.

    This is a mix-in designed to be used with the EntityName pattern:
    https://github.com/sqlalchemy/sqlalchemy/wiki/EntityName
    """

    __tablename__ = _CACHE_INFO_TABLE

    file: Mapped[str] = mapped_column(Text, primary_key=True)
    cache_updated_at: Mapped[datetime] = mapped_column(DateTime)

    @declared_attr
    def data(cls) -> Mapped[DataTableBase]:
        """Attribute for DataTable relationship."""
        return relationship(
            "DataTable",
            back_populates="cache_info",
            cascade="all, delete",
            passive_deletes=True,
        )


@declarative_mixin
class DataTableBase:
    """Cached data entry ORM.

    The specific structure of this table will depend on the data being stored in
    it (hence why deferred reflection is used); the table is initialised at the
    first `set()` call and its schema determined at that point.

    Some things are consistent though; the data must have:
        - an integer primary key column (`data_cache_id`)
        - a column of text called `_source_canonical_path` (which stores a canonical
          filepath) and has a foreign key constraint on the cache info table.

    This is a mix-in designed to be used with the EntityName pattern:
    https://github.com/sqlalchemy/sqlalchemy/wiki/EntityName
    """

    __tablename__ = _CACHED_DATA_TABLE

    data_cache_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    @declared_attr
    def _source_canonical_path(cls) -> Mapped[str]:
        return mapped_column(
            Text, ForeignKey("cache_info.file", ondelete="CASCADE"), index=True
        )

    @declared_attr
    def cache_info(cls) -> Mapped[CacheInfoTableBase]:
        """Attribute for CacheInfoTable relationship."""
        return relationship("CacheInfoTable", back_populates="data")


STATIC_FILE_NAME_COLUMN: str = "_source_canonical_path"

###############################
# END: SQLAlchemy ORM Classes #
###############################


def _set_sqlite_foreign_key_pragma(
    dbapi_connection: Any, connection_record: Any
) -> None:
    """Ensures foreign keys are used on DB connection.

    Adapted from: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#foreign-key-support
    """  # noqa: E501
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class SQLiteDataPersister(DataPersister):
    """A data caching implementation that uses an SQLite database."""

    def __init__(self, sqlite_path: Path, *args: Any, **kwargs: Any) -> None:
        super().__init__(STATIC_FILE_NAME_COLUMN, *args, **kwargs)
        self._sqlite_path = sqlite_path

        self._engine = create_engine(
            f"sqlite:///{str(sqlite_path.resolve())}",
            echo=config.settings.logging.data_cache_sql_debug,
            future=True,
        )
        # Set up event listener so that _every_ connection will respect
        # foreign key constraints
        listen(self._engine, "connect", _set_sqlite_foreign_key_pragma)

        self._Session = sessionmaker(bind=self._engine)

        # We want each instance of the persister to have their own ORM classes as
        # each ORM class can only be bound to one table/database at a time, and
        # we may have multiple persister instances at a time.
        self._mapper_registry = registry()
        self._CacheInfoTable: type[CacheInfoTableBase]
        self._DataTable: type[DataTableBase]

        # Establish if the database has been fully initialised already (i.e. has
        # a _CACHED_DATA_TABLE table), or if we need to wait for the first entry
        # to be able to create the tables.
        #
        # This is needed because we don't know the structure of the data ahead of
        # time, so cannot specify the shape of the _CACHED_DATA_TABLE table until
        # we receive the first instance of data we want to store there.
        #
        # Subsequent uses of the same, initialised, database allow us to just reflect
        # the table structure onto the DataTableBase ORM class.
        self._db_prepped: bool
        if self._has_table(_CACHED_DATA_TABLE):
            self._create_orm_from_db()
            self._db_prepped = True
        else:
            self._db_prepped = False

    @property
    def db_prepped(self) -> bool:
        """Whether the database has been fully initialised."""
        if self._db_prepped:
            return True

        has_table = self._has_table(_CACHED_DATA_TABLE)
        if has_table:
            self._create_orm_from_db()
            self._db_prepped = True

        return has_table

    def _get(self, file: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Get the persisted data for a given file.

        Returns None if no data has been persisted, if the data is out of date,
        or if the database has not been initialized yet (i.e. no data has been stored).
        """
        if not self.db_prepped:
            _logger.debug(
                f"Database {self._sqlite_path} has not been initialised yet;"
                f" it will be initialised on the first call to `set()`."
            )
            return None

        file = Path(file).resolve()

        # If there's no entry for this file, or the entry is out of date (i.e. the
        # file has been modified since the last cache update), then we return None.
        #
        # Logging of the specific reason will occur in _check_cache_for_files().
        cache_hits, _ = self._check_cache_for_files([file])

        if len(cache_hits) > 0:
            _logger.debug(f"Cache hit for {file}; retrieving data from cache.")
            with self._Session() as session:
                data_select_stmt = select(self._DataTable).filter_by(
                    _source_canonical_path=cache_hits[0]
                )
                data = pd.read_sql(data_select_stmt, session.connection())

            # Remove the ID and _source_canonical_path as these are only relevant in
            # the database
            data.drop(
                ["data_cache_id", self._file_name_column],
                axis="columns",
                inplace=True,
            )
            return data
        else:
            return None

    def _bulk_get(self, files: Sequence[Union[str, Path]]) -> BulkResult:
        """Get the persisted data for the target files.

        Returns a dataframe containing the results.

        This implements no limits so please partition the file list before calling this.
        """
        files_as_paths = [
            (Path(file).resolve() if isinstance(file, str) else file) for file in files
        ]

        if not self.db_prepped:
            _logger.debug(
                f"Database {self._sqlite_path} has not been initialised yet;"
                f" it will be initialised on the first call to `set()`."
            )
            return BulkResult(
                file_name_column=self._file_name_column,
                cached=None,
                misses=files_as_paths,
            )

        # If there's no entry for this file, or the entry is out of date (i.e. the
        # file has been modified since the last cache update), then we return None.
        #
        # Logging of the specific reason will occur in _cache_valid_for_file().
        cache_hits, cache_misses = self._check_cache_for_files(files_as_paths)
        if len(cache_hits) == 0:
            return BulkResult(
                file_name_column=self._file_name_column,
                cached=None,
                misses=cache_misses,
            )
        else:
            _logger.debug(f"Cache hit for {cache_hits}; retrieving data from cache.")

        with self._Session() as session:
            data_select_stmt = select(self._DataTable).filter(
                self._DataTable._source_canonical_path.in_(cache_hits)
            )
            data = pd.read_sql(data_select_stmt, session.connection())

        # Remove the ID as this is only relevant in the database
        data.drop(["data_cache_id"], axis="columns", inplace=True)
        return BulkResult(
            file_name_column=self._file_name_column, cached=data, misses=cache_misses
        )

    def _set(self, file: Union[str, Path], data: pd.DataFrame) -> None:
        """Set the persisted data for a given file.

        If this is the first data being persisted in this database, the dataframe
        is used to determine the schema of the database table to store data in.
        """
        file = Path(file).resolve()

        data = self._ensure_source_canonical_path_column(data, file)

        if not self.db_prepped:
            try:
                if self._lock:
                    self._lock.acquire()
                _logger.info(
                    f"No existing `{_CACHED_DATA_TABLE}` table was present in"
                    f" {self._sqlite_path}; creating from supplied data"
                )
                self._prep_db_from_frame(data)
            finally:
                if self._lock:
                    self._lock.release()

        # Perform the insert, catching exceptions indicating that we have missing
        # columns and updating this as needed, or that there's already something
        # associated with this file.
        #
        # There should be max 3 attempts (currently) for insertion; we may see it
        # fail due to primary key, fail due to missing columns, after that we would
        # expect it to work
        max_attempts: int = 3
        current_attempt: int = 1
        insert_success: bool = False
        while not insert_success and current_attempt <= max_attempts:
            try:
                self._insert_into_db(file, data)
                insert_success = True
            except OperationalError as e:
                # This may indicate missing columns
                if f"table {_CACHED_DATA_TABLE} has no column" in str(e):
                    self._add_columns_to_db(data)
                    # As new columns have been added, need to update the ORM classes
                    self._create_orm_from_db()
                else:
                    raise
            except IntegrityError as e:
                # This may indicate a failure due to an existing entry for `file`
                if f"UNIQUE constraint failed: {_CACHE_INFO_TABLE}.file" in str(e):
                    _logger.debug(
                        f"Found existing cache entry for {file};"
                        f" removing before setting new entry"
                    )
                    self.unset(file)
                else:
                    raise
            current_attempt += 1

        if not insert_success:
            raise DataCacheError(f"Failed to set data cache entry for file {file}")

    def unset(self, file: Union[str, Path]) -> None:
        """Deletes the persisted data for the given file."""
        file = Path(file).resolve()
        return self._delete(file)

    def _has_table(self, table_name: str) -> bool:
        """Check if a given table exists in the database."""
        return inspect(self._engine).has_table(table_name)

    def _construct_table_from_frame(self, data: pd.DataFrame) -> Table:
        """Create an SQLAlchemy table from the given dataframe."""
        # We use Pandas SQL-related classes to generate the table as this handles
        # all the type conversions, etc., for us.
        pandas_genned_table: Table = PandasSQLTable(
            name=_CACHED_DATA_TABLE,
            pandas_sql_engine=PandasSQLDatabase(self._engine),
            frame=data,
            index=False,
        ).table
        return pandas_genned_table

    def _prep_db_from_frame(self, data: pd.DataFrame) -> None:
        """Prepare the database using information from the provided dataframe.

        In particular, the dataframe is used to establish what the schema of the
        data caching table needs to be.
        """
        if self.db_prepped:
            _logger.debug(
                f"Database {self._sqlite_path} has already been prepared; skipping."
            )
            return

        # We make use of the underlying classes in pandas that are used to implement
        # DataFrame.to_sql() as these handle all the type conversions and other
        # criteria for us.
        #
        # We can then extract the SQLAlchemy table description created and use this
        # directly.
        data_table: Table = self._construct_table_from_frame(data)

        # The generated table is missing a foreign key constraint on the cache_info
        # table
        data_table.append_constraint(
            ForeignKeyConstraint(
                (self._file_name_column,),
                ("cache_info.file",),
                ondelete="CASCADE",
            )
        )

        # The generated table is missing an appropriate primary key (as we use
        # index=False); generate our own.
        data_table.append_column(
            Column("data_cache_id", Integer, primary_key=True, autoincrement=True)
        )

        # We need to create a new MetaData instance as the default _Base.metadata
        # contains the "wrong" table info for the data table.
        metadata = MetaData()
        data_table.to_metadata(metadata)
        CacheInfoTableTemp: type[CacheInfoTableBase] = self._mapper_registry.mapped(
            type("CacheInfoTable", (CacheInfoTableBase,), {})
        )
        CacheInfoTableTemp.__table__.to_metadata(metadata)  # type: ignore[attr-defined] # Reason: the post-mapping class will have this attribute # noqa: E501

        metadata.create_all(self._engine)

        # Now we have created the tables as desired, we can reflect/instantiate
        # the ORM table descriptions knowing that the definitions in the database
        # are correct.
        self._create_orm_from_db()
        self._db_prepped = True

    def _add_columns_to_db(self, data: pd.DataFrame) -> None:
        """Add new columns from `data` to the database."""
        # SQL Alchemy doesn't directly support ALTER TABLE commands via its API
        # so we have to manually do so.
        new_table: Table = self._construct_table_from_frame(data)
        old_table: Table = self._DataTable.__table__  # type: ignore[attr-defined] # Reason: the post-mapping class will have this attribute # noqa: E501

        new_columns: set[str] = set(new_table.columns.keys()) - set(
            old_table.columns.keys()
        )

        with self._Session() as session, session.begin():
            for new_column_name in new_columns:
                # We have to use _copy() on the column as each column is bound to
                # a specific Table instance
                new_column: Column = new_table.columns[new_column_name]._copy()
                _logger.info(
                    f'New column found ("{new_column.name}"'
                    f" with type {new_column.type})."
                    f" Adding to dataset database cache."
                )

                # Ensure that table name and column name are escaped.
                # SQLAlchemy normally handles this behind the scenes, but because
                # we are more manually constructing the statement than usual, we
                # need to be certain.
                # Note that quote() already produces _quoted_ strings, if needed.
                preparer = self._engine.dialect.identifier_preparer

                stmt_col_name = preparer.quote(new_column.name)
                # If nothing was escaped, only difference might be quoting characters
                if stmt_col_name.strip('"') != new_column.name:
                    _logger.warning(
                        f'Unable to use column name "{new_column.name}"'
                        f" in ALTER TABLE statement;"
                        f" has been escaped to {stmt_col_name}"
                    )

                stmt_table_name = preparer.quote(_CACHED_DATA_TABLE)
                # If nothing was escaped, only difference might be quoting characters
                if stmt_table_name.strip('"') != _CACHED_DATA_TABLE:
                    _logger.warning(
                        f'Unable to use table name "{_CACHED_DATA_TABLE}"'
                        f" in ALTER TABLE statement;"
                        f" has been escaped to {stmt_table_name}"
                    )

                session.execute(
                    text(
                        f"ALTER TABLE {stmt_table_name}"
                        f" ADD COLUMN {stmt_col_name}"
                        f" {new_column.type.compile(self._engine.dialect)}"
                    )
                )

    def _create_orm_from_db(self) -> None:
        """Creates/reloads the ORM classes from the database."""
        # First, remove any existing mappings/metadata that link the table names
        # to classes
        self._mapper_registry.dispose()
        self._mapper_registry.metadata.clear()

        # Create a new declarative base, as this gets us a fresh MetaData instance
        # to work with
        Base: type[DeclarativeMeta] = self._mapper_registry.generate_base()

        # Create the ORM class for CacheInfoTable
        # We dynamically create a class that subclasses both the mixin and the
        # declarative base
        self._CacheInfoTable = type("CacheInfoTable", (CacheInfoTableBase, Base), {})

        # Create the ORM class for DataTable
        # We dynamically create a class that subclasses both the mixin and the
        # declarative base, _and_ that is told to reflect the structure from the
        # database. This gets us all the non-specified, dataframe-related, columns
        # that have been stored in the database.
        self._DataTable = type(
            "DataTable",
            (DataTableBase, Base),
            {"__table_args__": {"autoload_with": self._engine}},
        )

        Base.metadata.create_all(bind=self._engine)

    def _check_cache_for_files(self, files: list[Path]) -> tuple[list[str], list[Path]]:
        """Return a tuple with the cache hits and misses.

        Hits are the resolved files for which the cache is valid,
        and can be used to lookup the data table directly.

        Misses are the supplied paths that didn't get a hit.

        For a cache entry to be valid it must (a) exist, and (b) be more recent
        than the time the file was last modified.
        """
        if not self.db_prepped:
            _logger.debug(
                f"Database {self._sqlite_path} has not been initialised yet;"
                f" it will be initialised on the first call to `set()`."
            )
            return ([], files)

        resolved_files = dict([(str(file.resolve()), file) for file in files])

        # Retrieve the cache info from the DB. We will get None if there is no entry.
        cache_info: list[CacheInfoTableBase]
        with self._Session() as session:
            cache_info = (
                session.query(self._CacheInfoTable)
                .filter(self._CacheInfoTable.file.in_(resolved_files.keys()))
                .all()
            )

        # No cache entry found
        if not cache_info:
            _logger.debug(f"No cache entry found for files {files}")
            return ([], files)

        # Otherwise, we check if the cache entry is valid based on file/cache
        # modification dates
        cache_hits: list[str] = []
        for cache_entry in cache_info:
            if (
                cache_entry.file is not None
                and cache_entry.cache_updated_at is not None
            ):
                file_as_path = resolved_files[cache_entry.file]
                cache_hit = False
                try:
                    fs_last_modified: datetime = self._get_last_modified(file_as_path)
                    if cache_entry.cache_updated_at >= fs_last_modified:
                        # Cache is as recent or more recent
                        cache_hit = True
                    else:
                        _logger.debug(
                            "Cache entry found, but invalid: cache entry for"
                            f" {file_as_path} was last cached at"
                            f" {cache_entry.cache_updated_at}, but file was updated at"
                            f" {fs_last_modified}. Deleting cache entry."
                        )
                except FileNotFoundError:
                    _logger.debug(
                        f"Cache entry found for {file_as_path}"
                        " but file not found in the filesystem."
                        " Deleting cache entry."
                    )

                if cache_hit:
                    cache_hits.append(cache_entry.file)
                else:
                    self._delete(file_as_path)

        cache_misses = [
            resolved_files[key] for key in resolved_files if key not in cache_hits
        ]
        return (cache_hits, cache_misses)

    def _insert_into_db(self, file: Path, data: pd.DataFrame) -> None:
        """Perform the database insert."""
        with self._Session() as session, session.begin():
            session.add(
                self._CacheInfoTable(  # type: ignore[call-arg] # Reason: these are the attributes for this type, mypy is just not picking them up # noqa: E501
                    file=(str(file)), cache_updated_at=self._get_cache_update_time()
                )
            )

            # need to flush() to ensure that cache_info entry is written before
            # to_sql() is called (as otherwise will complain about foreign key
            # violation)
            session.flush()

            data.to_sql(
                _CACHED_DATA_TABLE,
                session.connection(),
                if_exists="append",
                index=False,  # we use our own index
            )

    def _delete(self, file: Path) -> None:
        """Delete an entry in the cache."""
        file_str = str(file.resolve())

        with self._Session() as session, session.begin():
            # Get the cache info for the given file. This will be None if no entry
            # is found.
            file_cache_info: Optional[CacheInfoTableBase] = session.get(
                self._CacheInfoTable, file_str
            )

            if file_cache_info is None:
                _logger.warning(
                    f"Cache deletion requested but no entry was found for {file_str}"
                )
            else:
                session.delete(file_cache_info)

    @staticmethod
    def _get_last_modified(file: Path) -> datetime:
        """Get the last modified time of a file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        return datetime.fromtimestamp(os.path.getmtime(file))

    @staticmethod
    def _get_cache_update_time() -> datetime:
        """Returns the datetime to use for cache update records.

        By default this is just `datetime.now()`.
        """
        return datetime.now()

    @staticmethod
    def _ensure_source_canonical_path_column(
        data: pd.DataFrame, file: Path
    ) -> pd.DataFrame:
        """Ensures dataframe has `_source_canonical_path` column, adding it if not."""
        if STATIC_FILE_NAME_COLUMN not in data.columns:
            file_str = str(file.resolve())
            # Use `assign()` rather than data[] assignment to avoid mutating input
            # frame
            data = data.assign(_source_canonical_path=file_str)
        return data

    def get_all_cached_files(self) -> list[str]:
        """Get all file paths currently stored in the cache.

        Returns:
            A list of canonical file paths (as strings) that have entries in the cache.
            Returns an empty list if the database hasn't been initialized yet.
        """
        if not self.db_prepped:
            _logger.debug(
                f"Database {self._sqlite_path} has not been initialised yet;"
                f" it will be initialised on the first call to `set()`."
            )
            return []

        with self._Session() as session:
            # Query all file paths from the cache_info table
            files = session.query(self._CacheInfoTable.file).all()

        # Return a flattened list of file paths
        return [file[0] for file in files]
