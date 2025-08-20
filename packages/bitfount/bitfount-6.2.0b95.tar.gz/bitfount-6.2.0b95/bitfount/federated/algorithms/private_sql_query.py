"""Private SQL query algorithm."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import TYPE_CHECKING, Any, ClassVar, Final, Optional, TypedDict, Union, cast

from marshmallow import fields
import pandas as pd
from typing_extensions import NotRequired

from bitfount.config import DP_AVAILABLE
from bitfount.data.datasources.base_source import (
    BaseSource,
    FileSystemIterableSource,
)
from bitfount.data.datasources.utils import load_data_in_memory
from bitfount.data.datasplitters import DatasetSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import SemanticType, _SemanticTypeValue
from bitfount.federated.algorithms.base import (
    BaseNonModelAlgorithmFactory,
    BaseWorkerAlgorithm,
    ResultsOnlyModellerAlgorithm,
)
from bitfount.federated.exceptions import PrivateSqlError
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.mixins import _ModellessAlgorithmMixIn
from bitfount.federated.privacy.differential import (
    DPModellerConfig,
    DPPodConfig,
    _DifferentiallyPrivate,
)
from bitfount.types import T_FIELDS_DICT
from bitfount.utils import delegates

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger(__name__)

if DP_AVAILABLE:
    import snsql
    from snsql import Privacy


class ColumnRanges(TypedDict):
    """Column ranges for the PrivateSqlQuery algorithm."""

    lower: NotRequired[Optional[int]]
    upper: NotRequired[Optional[int]]
    type: NotRequired[Optional[str]]  # Added at runtime


# Either a mapping of column names to their ranges, or a mapping of table names to
# a mapping of column names to their ranges for multi-table datasets.
ColumnRangesType = Union[dict[str, ColumnRanges], dict[str, dict[str, ColumnRanges]]]


class _WorkerSide(BaseWorkerAlgorithm):
    """Worker side of the PrivateSqlQuery algorithm."""

    _SMART_NOISE_TYPE: Final[Mapping[str, tuple[str, Optional[int]]]] = {
        "int": ("int", 1_000),
        "int32": ("int", 1_000),
        "int64": ("int", 1_000),
        "float": ("float", 1),
        "float32": ("float", 1),
        "float64": ("float", 1),
        "string": ("string", None),
    }

    def __init__(
        self,
        *,
        query: str,
        epsilon: float,
        delta: float,
        column_ranges: ColumnRangesType,
        hub: BitfountHub,
        db_schema: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.datasource: BaseSource
        self.pod_identifier: Optional[str] = None
        self.pod_dp: Optional[DPPodConfig] = None
        self.query = query
        self.epsilon = epsilon
        self.delta = delta
        self.column_ranges = column_ranges
        self.hub = hub
        self.table = table
        self.db_schema = db_schema
        super().__init__(**kwargs)

    def initialise(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
        pod_dp: Optional[DPPodConfig] = None,
        pod_identifier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Sets Datasource."""
        self.initialise_data(datasource=datasource, data_splitter=data_splitter)
        if pod_identifier:
            self.pod_identifier = pod_identifier
        if pod_dp:
            self.pod_dp = pod_dp

        if self.table is None and self.pod_identifier is not None:
            self.table = self.pod_identifier.split("/")[1]

    def initialise_data(
        self,
        datasource: BaseSource,
        data_splitter: Optional[DatasetSplitter] = None,
    ) -> None:
        """Initialise the data for the worker side of the algorithm."""
        self.datasource = datasource
        self.data_splitter = data_splitter

    def map_types(self, schema: BitfountSchema) -> None:
        """Map from Pandas DataTypes to SmartNoise types.

        For the features that were user-specified in the single-table dataset,
        map from the Pandas DataTypes to the equivalent SmartNoise types.
        """
        self.column_ranges = cast(dict[str, ColumnRanges], self.column_ranges)
        for column in self.column_ranges:
            mapped_type = None
            default_max = None
            # Determine what type we have in the schema for the column
            for stype in SemanticType:
                for feature in schema.get_feature_names(stype):
                    if feature == column:
                        stype_features = schema.features[
                            cast(_SemanticTypeValue, stype.value)
                        ]
                        feature_details = stype_features[feature]
                        mapped_type = feature_details.dtype_name
                        break

            if mapped_type is None:
                logger.warning(
                    f"No field named '{column}' present in the schema."
                    " Will proceed assuming it is a string."
                )
                mapped_type = "str"

            # Map the type we have to an equivalent for SmartNoise SQL
            sn_mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                mapped_type.lower(), (None, None)
            )
            if not sn_mapped_type:
                logger.warning(
                    f"type {mapped_type} for column '{column}' is not supported."
                    " Defaulting to string type."
                )
                sn_mapped_type = "string"

            self.column_ranges[column]["type"] = sn_mapped_type
            # if there is no specified lower/upper for int/float set defaults
            if not self.column_ranges[column].get("lower") and default_max is not None:
                logger.warning(
                    "Using default lower and upper bound of "
                    f"(0, {default_max}) for field [{column}]"
                )
                self.column_ranges[column]["lower"] = 0
                self.column_ranges[column]["upper"] = default_max

    def map_types_multi(self, schema: BitfountSchema) -> list[str]:
        """Map from Pandas DataTypes to SmartNoise types.

        For the features that were user-specified in the multi-table dataset,
        map from the Pandas DataTypes to the equivalent SmartNoise types.
        """
        features_added = []
        self.column_ranges = cast(
            dict[str, dict[str, ColumnRanges]], self.column_ranges
        )
        for table_name, columns in self.column_ranges.items():
            for column in columns:
                mapped_type: Optional[str] = None
                if table_name == schema.name:
                    # Determine what type we have in the schema for the column
                    for stype in SemanticType:
                        for feature in schema.get_feature_names(stype):
                            if feature == column:
                                stype_features = schema.features[
                                    cast(_SemanticTypeValue, stype.value)
                                ]
                                feature_details = stype_features[feature]
                                mapped_type = feature_details.dtype_name
                                break
                else:
                    logger.warning(
                        f"No table named '{table_name}' present in the schema. "
                        "SQL query will probably fail if a query attempts "
                        "to use this table."
                    )

                if mapped_type is None:
                    logger.warning(
                        f"No field named '{column}' present in the schema"
                        "will proceed assuming it is a string."
                    )
                    mapped_type = "str"

                # Map the type we have to an equivalent for SmartNoise SQL
                sn_mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                    mapped_type.lower(), (None, None)
                )
                if not sn_mapped_type:
                    logger.warning(
                        f"type {mapped_type} for column '{column}' is not supported"
                        "defaulting to string type."
                    )
                    sn_mapped_type = "string"

                self.column_ranges[table_name][column]["type"] = sn_mapped_type
                features_added.append(column)
                # if there is no specified lower/upper for int/float set defaults
                if (
                    not self.column_ranges[table_name][column].get("lower")
                    and default_max is not None
                ):
                    logger.warning(
                        "Using default lower and upper bound of "
                        f"(0, {default_max}) for field [{column}]"
                    )
                    self.column_ranges[table_name][column]["lower"] = 0
                    self.column_ranges[table_name][column]["upper"] = default_max

        return features_added

    def extend_types(self, schema: BitfountSchema, already_added: list[str]) -> None:
        """Add SmartNoise types for remaining features from Pandas DataTypes.

        In this case, for the features are not all specified in the modeller-supplied
        metadata, map to the appropriate type.
        """
        self.column_ranges = cast(
            dict[str, dict[str, ColumnRanges]], self.column_ranges
        )
        for stype in SemanticType:
            for feature in schema.get_feature_names(stype):
                f_cat = str(stype.value)
                if feature not in already_added:
                    mapped_type = schema.features[
                        f_cat  # type: ignore[literal-required] # Reason: below
                    ][feature.replace('"', "")].dtype.name
                    # Reason: enum value is valid
                    # Only need to deal with numeric types, others already string
                    mapped_type, default_max = self._SMART_NOISE_TYPE.get(
                        mapped_type.lower(), (None, None)
                    )

                    if schema.name not in self.column_ranges:
                        self.column_ranges[schema.name] = {}
                    self.column_ranges[schema.name][feature] = {"type": mapped_type}
                    # If there is no specified lower/upper for int/float, default
                    if default_max is not None:
                        logger.warning(
                            "Using default lower and upper bound of "
                            f"(0,{default_max}) for field [{feature}]"
                        )
                        self.column_ranges[schema.name][feature].update({"lower": 0})
                        self.column_ranges[schema.name][feature].update(
                            {"upper": default_max}
                        )

    def run(self, **kwargs: Any) -> pd.DataFrame:
        """Executes the SQL query on the `BaseSource`."""
        logger.info("Executing query...")
        if self.table is None:
            raise ValueError(
                "No table specified on which to execute the query on. "
                "Please specify the table on which to execute the query "
                "in the algorithm definition."
            )
        if self.pod_identifier is None:
            raise ValueError("No pod identifier - cannot get schema to infer types.")
        # Get the schema from the hub, needed for getting the column data types.
        schema = self.hub.get_pod_schema(self.pod_identifier)
        # Check that modeller-side dp parameters are within the pod config range.
        dp = _DifferentiallyPrivate({"epsilon": self.epsilon, "delta": self.delta})
        # We initialise dp explicitly above, so dp._dp_config will be of
        # type DPModellerConfig, making it safe to cast.
        dp._dp_config = cast(DPModellerConfig, dp._dp_config)
        if self.pod_dp:
            dp.apply_pod_dp(self.pod_dp)
        else:
            # If there is no pod_pd, we assign to it the epsilon and delta values
            # from the Modeller, as they have been previously checked by the AM.
            self.pod_dp = DPPodConfig(epsilon=self.epsilon, delta=self.delta)

        # Extract the metadata from the column ranges.
        meta: dict[str, dict[str, dict[str, dict[str, Union[ColumnRanges, bool, int]]]]]
        if isinstance(self.datasource, FileSystemIterableSource):
            # TODO: [BIT-3486] Address this exclusion by adding path that works
            #       with iteration
            raise TypeError(
                f"PrivateSQLQuery does not support iterable datasources that"
                f" are not databases; got {type(self.datasource)}"
            )
        else:
            # Single-table/in-memory path - load the data into memory
            df = load_data_in_memory(self.datasource)

            if (f"from `{self.table}`" not in self.query) and (
                f"FROM `{self.table}`" not in self.query
            ):
                err_msg = """The default table for single table datasource is the pod
                    identifier without the username, in between backticks(``),
                    repeated twice, separated by a dot.
                    (e.g. `census-income-demo`.`census-income-demo`)
                    Please ensure your SQL query operates on that table. The
                    table name should be put inside backticks(``) in the
                    query statement, to make sure it is correctly parsed."""
                logger.error(err_msg)
                raise ValueError(err_msg)

            # We need to remove hyphens as pandasql errors out if
            # they are included in the table name and query.
            aux_query = self.query.split("`")
            table_name = self.table.replace("-", "")
            aux_query[:] = [
                item if item != self.table else table_name for item in aux_query
            ]

            # Update the query with the table name with hyphens removed
            query = "".join(aux_query)

            # Change the table name in the schema for the purpose of this query
            if schema.name == self.table:
                schema.name = table_name

            # Map the dtypes to types understood by SmartNoise SQL
            self.map_types(schema)
            # Set up the metadata dictionary required for SmartNoise SQL
            meta = {
                "": {
                    table_name: {
                        table_name: {"row_privacy": True, "rows": int(len(df.index))}
                    }
                }
            }
            # We update the metadata with a copy so we don't modify
            # the original column ranges.
            meta[""][table_name][table_name].update(
                cast(dict[str, ColumnRanges], self.column_ranges.copy())
            )

        # Set default values for the used_epsilon and used_delta
        used_epsilon = float("inf")
        used_delta = float("inf")

        # Initialise epsilon and delta divisors as 1
        delta_div = 1.0
        epsilon_div = 1.0
        # Parameters used for rounding up the divisors
        delta_n = 10
        epsilon_n = 10

        try:
            while used_epsilon > self.pod_dp.epsilon or used_delta > self.pod_dp.delta:
                # Configure privacy
                # Note that the parameters are per-column maximums
                privacy = Privacy(
                    epsilon=dp._dp_config.epsilon / epsilon_div,
                    delta=dp._dp_config.delta / delta_div,
                )

                # Pre-flight the sql query, and compute the privacy cost
                reader = snsql.from_df(df, privacy=privacy, metadata=meta)
                used_epsilon, used_delta = reader.get_privacy_cost(query)

                if used_epsilon > self.pod_dp.epsilon:
                    # Update epsilon_div to be the result of dividing the used_epsilon
                    # by the maximum allowed value by the pod, rounded up to eps_n
                    # decimals
                    epsilon_div = (
                        math.ceil(used_epsilon / self.pod_dp.epsilon * 10**epsilon_n)
                        / 10**epsilon_n
                    )
                    epsilon_n -= 1

                if used_delta > self.pod_dp.delta and delta_n > 1:
                    # Update delta_div to be the result of dividing the used_delta
                    # by the maximum allowed value by the pod, rounded up to delta_n
                    # decimals
                    delta_div = (
                        math.ceil(used_delta / self.pod_dp.delta * 10**delta_n)
                        / 10**delta_n
                    )
                    delta_n -= 1
                elif used_delta > self.pod_dp.delta and delta_n <= 1:
                    # On the last loop, do a bigger division for the delta.
                    delta_div = (
                        math.ceil(used_delta / self.pod_dp.delta * 10**delta_n)
                        / 10**delta_n
                    ) * 10
                    delta_n -= 1
                # If any of delta_n or epsilon_n are 0, then we have reached
                # the end of our loop, and we raise an error to the user.
                if delta_n < 0:
                    raise PrivateSqlError(
                        "Cannot execute current query given the provided privacy "
                        f"parameter delta={self.delta}). Try again using a "
                        f"smaller value of delta."
                    )
                if epsilon_n < 0:
                    raise PrivateSqlError(
                        "Cannot execute current query given the provided privacy "
                        f"parameter epsilon={self.epsilon}. Try again using a "
                        f"smaller epsilon value."
                    )
            # Log the total values of the privacy budget used.
            logger.federated_info(
                "Total privacy cost for query will be "
                f"(epsilon={used_epsilon}, delta={used_delta})"
            )
            # Log the values of the privacy budget used per column.
            logger.federated_info(
                f"Executing SQL query with epsilon {privacy.epsilon} "
                f"and delta {privacy.delta} applied on each queried column."
            )
            # Execute the Private SQL query
            output = reader.execute(query)

        except Exception as ex:
            raise PrivateSqlError(
                f"Error executing PrivateSQL query: [{self.query}], got error [{ex}]"
            ) from ex

        # Output is a list of lists (or similar) with the first one representing
        # column headers, all the rest representing rows
        return pd.DataFrame(output[1:], columns=output[0])


@delegates()
class PrivateSqlQuery(
    BaseNonModelAlgorithmFactory[ResultsOnlyModellerAlgorithm, _WorkerSide],
    _ModellessAlgorithmMixIn,
):
    """Simple algorithm for running a SQL query on a table, with privacy.

    :::note

    The values provided for the privacy budget (i.e. epsilon and delta)
    will be applied individually to all columns included in the SQL query provided.
    If the total values of the epsilon and delta exceed the maximum allowed by the pod,
    the provided values will be reduced to the maximum values required to remain
    within the allowed privacy budget.

    :::

    Args:
        datastructure: The data structure to use for the algorithm.
        query: The SQL query to execute.
        epsilon: The maximum epsilon to use for the privacy budget.
        delta: The target delta to use for the privacy budget.
        column_ranges: A dictionary of column names and their ranges.
        table: The target table name. For single table pod datasources,
            this will default to the pod name.
        db_schema: The name of the schema for a database connection. If
            not provided, it will be set to the default schema name
            for the database.

    Attributes:
        query: The SQL query to execute.
        epsilon: The maximum epsilon to use for the privacy budget.
        delta: The target delta to use for the privacy budget.
        column_ranges: A dictionary of column names and their ranges.
        table: The target table name. For single table pod datasources,
            this will default to the pod name.
        db_schema: The name of the schema for a database connection. If
            not provided, it will be set to the default schema name
            for the database.

    Raises:
        PrivateSqlError: If there is an error executing the private SQL query (e.g. DP
            misconfiguration or bad query specified).
        ValueError: If a pod identifier is not supplied, or if a join is attempted.
        DatabaseSchemaNotFoundError: If a non-existent db_schema name is provided.
    """

    fields_dict: ClassVar[T_FIELDS_DICT] = {
        "query": fields.Str(),
        "epsilon": fields.Float(allow_nan=True),
        "delta": fields.Float(allow_nan=True),
        "column_ranges": fields.Dict(),
        "table": fields.Str(allow_none=True),
        "db_schema": fields.Str(allow_none=True),
    }
    _inference_algorithm: bool = False

    def __init__(
        self,
        *,
        datastructure: DataStructure,
        query: str,
        epsilon: float,
        delta: float,
        column_ranges: ColumnRangesType,
        table: Optional[str] = None,
        db_schema: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(datastructure=datastructure, **kwargs)
        self.query = query
        self.epsilon = epsilon
        self.delta = delta
        self.column_ranges = column_ranges
        self.table = table
        self.db_schema = db_schema

    def modeller(self, **kwargs: Any) -> ResultsOnlyModellerAlgorithm:
        """Returns the modeller side of the PrivateSqlQuery algorithm.

        Args:
            **kwargs: Additional keyword arguments to pass to the modeller side.
        """
        return ResultsOnlyModellerAlgorithm(**kwargs)

    def worker(self, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the PrivateSqlQuery algorithm.

        Args:
            **kwargs: Additional keyword arguments to pass to the worker side. `hub`
                must be one of these keyword arguments which provides a `BitfountHub`
                instance.
        """
        return _WorkerSide(
            query=self.query,
            epsilon=self.epsilon,
            delta=self.delta,
            column_ranges=self.column_ranges,
            table=self.table,
            db_schema=self.db_schema,
            **kwargs,
        )
