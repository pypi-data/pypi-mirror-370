"""SQL query algorithm."""

from __future__ import annotations

from typing import Any, ClassVar, Optional, cast

from marshmallow import fields
import pandas as pd
import pandasql

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.sql_source import _SQLSource
from bitfount.data.datasources.utils import load_data_in_memory
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.exceptions import DuplicateColumnError
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    ResultsOnlyModellerAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import _ModellessAlgorithmMixIn
from bitfount.federated.privacy.differential import DPPodConfig
from bitfount.federated.types import _DataLessAlgorithm
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import delegates

logger = _get_federated_logger(__name__)


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the SqlQuery algorithm."""

    def __init__(
        self, *, query: str, table: Optional[str] = None, **kwargs: Any
    ) -> None:
        self.datasource: BaseSource
        self.query = query
        self.table = table
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)
        if self.table is None and pod_identifier is not None:
            self.table = pod_identifier.split("/")[1]

    def run(self, **kwargs: Any) -> pd.DataFrame:
        """Executes the query on the data source and returns a dataframe."""
        logger.info("Executing query...")
        if isinstance(self.datasource, _SQLSource):
            # We leverage the remote SQL engine to execute the query
            logger.debug("Executing query remotely...")
            output = self.execute_query_remotely()
        else:
            logger.debug("Executing query in memory...")
            output = self.execute_query_in_memory()

        logger.info("Query executed successfully.")
        return output

    def execute_query_remotely(self) -> pd.DataFrame:
        """Executes the query on the data source and returns a dataframe.

        This is a helper function that is used to execute the query on the database
        itself and returns a dataframe.

        Returns:
            A dataframe containing the results of the query.

        Raises:
            ValueError: If the table is not specified or the query is not valid.
        """
        if self.table is not None:
            logger.warning(
                "Ignoring table name as it is not supported for remote execution."
            )
        self.datasource = cast(_SQLSource, self.datasource)
        return self.datasource.execute_query(self.query)

    def execute_query_in_memory(self) -> pd.DataFrame:
        """Executes the query on the data source and returns a dataframe.

        This is a helper function that is used to execute the query on the data in
        memory and returns a dataframe.

        Returns:
            A dataframe containing the results of the query.

        Raises:
            ValueError: If the table is not specified or the query is not valid.
            DuplicateColumnError: If the query returns duplicate column names.
        """
        if self.table is None:
            raise ValueError(
                "No table specified on which to execute the query on. "
                "Please specify the table on which to execute the query "
                "in the algorithm definition."
            )

        # For SQL queries on a dataframe/single table.
        df = load_data_in_memory(self.datasource, table_name=self.table)
        if (f"from `{self.table}`" not in self.query) and (
            f"FROM `{self.table}`" not in self.query
        ):
            err_msg = """The default table for single table datasource is the pod
                identifier without the username, in between backticks(``).
                Please ensure your SQL query operates on that table. The
                table name should be put inside backticks(``) in the
                query statement, to make sure it is correctly parsed."""
            logger.error(err_msg)
            raise ValueError(err_msg)
        # We need to remove hyphens as pandasql errors out if
        # they are included in the table name and query.
        query = self.query.split("`")
        query[query.index(self.table)] = query[query.index(self.table)].replace("-", "")
        table_name = self.table.replace("-", "")
        try:
            # Now for the actual query.
            output: pd.DataFrame = pandasql.sqldf("".join(query), {table_name: df})
        except pandasql.PandaSQLException as ex:
            raise ValueError(
                f"Error executing SQL query: [{self.query}], got error [{ex}]"
            ) from ex

        if any(output.columns.duplicated()):
            raise DuplicateColumnError(
                f"The following column names are duplicated in the output "
                f"dataframe: {output.columns[output.columns.duplicated()]}. "
                f"Please rename them in the query, and try again."
            )
        return output


@delegates()
class SqlQuery(
    BaseNonModelAlgorithmFactory[ResultsOnlyModellerAlgorithm, _WorkerSide],
    _ModellessAlgorithmMixIn,
    _DataLessAlgorithm,
):
    r"""Simple algorithm for running a SQL query on a table.

    :::info

    The default table for single-table datasources is the pod identifier without the
    username, in between backticks(\`\`). Please ensure your SQL query operates on
    that table. The table name should be put inside backticks(\`\`) in the query
    statement, to make sure it is correctly parsed e.g. ``SELECT MAX(G) AS MAX_OF_G
    FROM `df` ``. This is the standard quoting mechanism used by MySQL (and also
    included in SQLite).

    :::

    :::info

    If you are using a multi-table datasource, ensure that your SQL query syntax matches
    the syntax required by the Pod database backend.

    :::

    Args:
        datastructure: The data structure to use for the algorithm.
        query: The SQL query to execute.
        table: The target table name. For single table pod datasources,
            this will default to the pod name.

    Attributes:
        query: The SQL query to execute.
        table: The target table name. For single table pod datasources,
            this will default to the pod name.

    """

    _inference_algorithm: bool = False

    def __init__(
        self,
        *,
        datastructure: DataStructure,
        query: str,
        table: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.query = query
        self.table = table

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "query": fields.Str(required=True),
        "table": fields.Str(allow_none=True),
    }

    def modeller(self, **kwargs: Any) -> ResultsOnlyModellerAlgorithm:
        """Returns the modeller side of the SqlQuery algorithm."""
        return ResultsOnlyModellerAlgorithm(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the SqlQuery algorithm."""
        return _WorkerSide(query=self.query, table=self.table, **kwargs)
