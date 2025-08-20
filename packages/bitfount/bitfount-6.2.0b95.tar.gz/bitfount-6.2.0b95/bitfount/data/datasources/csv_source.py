"""Module containing CSVSource class.

CSVSource class handles loading of CSV data.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Iterator, Optional, Union, cast, overload

import pandas as pd
from pydantic import AnyUrl
from typing_extensions import override

from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.exceptions import DataSourceError
from bitfount.data.types import DataPathModifiers, SingleOrMulti
from bitfount.utils import delegates

logger = logging.getLogger(__name__)


@delegates()
class CSVSource(BaseSource):
    """Data source for loading csv files.

    Args:
        path: The path or URL to the csv file.
        read_csv_kwargs: Additional arguments to be passed as a
            dictionary to `pandas.read_csv`. Defaults to None.
    """

    def __init__(
        self,
        path: Union[os.PathLike, AnyUrl, str],
        read_csv_kwargs: Optional[dict[str, Any]] = None,
        modifiers: Optional[dict[str, DataPathModifiers]] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._modifiers = modifiers
        if not str(path).endswith(".csv"):
            raise TypeError("Please provide a Path or URL to a CSV file.")
        self.path = str(path)
        if not read_csv_kwargs:
            read_csv_kwargs = {}
        self.read_csv_kwargs = read_csv_kwargs

    @override
    def get_data(
        self,
        data_keys: SingleOrMulti[str] | SingleOrMulti[int],
        *,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> Optional[pd.DataFrame]:
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
        """Loads and returns selected data from a CSV.

        Rows whose index matches the data keys are returned.

        Example:
        ::
            Consider the following dataframe:

                name         dob        s
            0   John  1990-02-14    hello
            1  James  1980-01-01    world
            2  Geoff  1963-10-31  it's me

            With data_keys=[0, 2], we would expect this to return:

                name         dob        s
            0   John  1990-02-14    hello
            2  Geoff  1963-10-31  it's me

        Args:
            data_keys: String or integer based indices for which rows of the CSV
                should be returned. If string-based integers (e.g. ["1", "2", "3"],
                will attempt to use them as integers first. Otherwise, the index
                column must be passed into this class as part of the read_csv_kwargs.
            use_cache: See parent method.
            **kwargs: See parent method.

        Returns:
            A DataFrame-type object which contains the data.

        Raises:
            DataSourceError: If the CSV file cannot be opened.
        """
        dfs = list(self._yield_data(data_keys, use_cache=use_cache, **kwargs))
        # Avoid trying to concat empty list, as raises error
        if dfs:
            return pd.concat(dfs, axis="index")
        else:
            # Return an empty dataframe instead
            return pd.DataFrame()

    @override
    def yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str] | SingleOrMulti[int]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        for data in self._yield_data(
            data_keys, use_cache=use_cache, partition_size=partition_size, **kwargs
        ):
            for hook in self._hooks:
                try:
                    hook.on_datasource_yield_data(data)
                except NotImplementedError:
                    logger.warning(
                        f"{hook.hook_name} does not implement "
                        "`on_datasource_yield_data`."
                    )
                except Exception as e:
                    logger.error(f"Error in hook {hook.hook_name}: {e}")

            if not data.empty:
                yield data

    def _yield_data(
        self,
        data_keys: Optional[SingleOrMulti[str] | SingleOrMulti[int]] = None,
        *,
        use_cache: bool = True,
        partition_size: Optional[int] = None,
        **kwargs: Any,
    ) -> Iterator[pd.DataFrame]:
        """Generator for providing data chunkwise from a CSV.

        Will dynamically filter rows based on index corresponding to the data_keys.

        Example:
        ::
            Consider the following dataframe:

                name         dob        s
            0   John  1990-02-14    hello
            1  James  1980-01-01    world
            2  Geoff  1963-10-31  it's me

            With data_keys=[0, 2], partition_size=1, we would expect this to yield:

                name         dob        s
            0   John  1990-02-14    hello

            then

                name         dob        s
            2  Geoff  1963-10-31  it's me

        Args:
            data_keys: String or integer based indices for which rows of the CSV
                should be returned. If string-based integers (e.g. ["1", "2", "3"],
                will attempt to use them as integers first. Otherwise, the index
                column must be passed into this class as part of the read_csv_kwargs.
            use_cache: See parent method.
            partition_size: See parent method.
            **kwargs: See parent method.
        """
        if data_keys is not None:
            data_keys = self._convert_to_multi(data_keys)

        partition_size_: int
        if partition_size:
            partition_size_ = partition_size
        else:
            partition_size_ = self.partition_size

        try:
            csv_iter = pd.read_csv(
                self.path, chunksize=partition_size_, **self.read_csv_kwargs
            )
        except FileNotFoundError:
            logger.error(f"File {self.path} does not exist.")
            yield pd.DataFrame()
            return
        except Exception as e:
            raise DataSourceError(
                f"Unable to open CSV file {self.path}. Got error {e}."
            ) from e

        df: pd.DataFrame
        for df in csv_iter:
            # Fast-continue if nothing
            if df.empty:
                continue

            # If data_keys provided to limit the output, filter the chunk on the index
            # against those data_keys.
            if data_keys is not None:
                # If we have an integer index on the dataframe (the default),
                # i.e. numbered rows, then we try to ensure that the data_keys are in
                # integer format even if supplied as strings.
                index_type = df.index.inferred_type
                if index_type == "integer":
                    # Idiomatic way of selecting only _valid_ keys, not caring about
                    # missing.
                    # See: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#reindexing # noqa: E501
                    df = df.loc[df.index.intersection([int(i) for i in data_keys])]
                # Otherwise, index via strings
                else:
                    # Idiomatic way of selecting only _valid_ keys, not caring about
                    # missing.
                    # See: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#reindexing # noqa: E501
                    df = df.loc[df.index.intersection([str(s) for s in data_keys])]

                # Fast-continue if nothing remaining after filtering
                if df.empty:
                    continue

            # TODO: [BIT-4590] This should be auto-applied at any data
            #       yielding/returning rather than having to explicitly do it in every
            #       appropriate call.
            df = self.apply_modifiers(df)
            df = self.apply_ignore_cols(df)

            if not df.empty:
                yield df

    ###################
    # Utility Methods #
    ###################
    @staticmethod
    @overload
    def _convert_to_multi(som: SingleOrMulti[str]) -> list[str]: ...

    @staticmethod
    @overload
    def _convert_to_multi(som: SingleOrMulti[int]) -> list[int]: ...

    @staticmethod
    def _convert_to_multi(
        som: SingleOrMulti[str] | SingleOrMulti[int],
    ) -> list[str] | list[int]:
        # If already list, return unchanged
        if isinstance(som, list):
            return som
        elif isinstance(som, str):
            return [som]
        elif isinstance(som, int):
            return [som]
        else:
            # revealed type is:
            #   Union[typing.Sequence[builtins.str], typing.Sequence[builtins.int]]
            # so can cast to assure of correct return type
            return cast(list[str] | list[int], list(som))
