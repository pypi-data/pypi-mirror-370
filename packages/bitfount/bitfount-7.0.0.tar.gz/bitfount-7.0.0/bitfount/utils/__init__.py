"""General helpful utilities to be found here."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Generator, Iterable, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
import importlib
import importlib.abc
import importlib.util
import inspect
from itertools import chain
import linecache
import logging
from pathlib import Path
import random
import sys
from types import GenericAlias, ModuleType
from typing import Any, Hashable, Literal, NoReturn, Optional, TypeVar, Union, cast

import docstring_parser
from docstring_parser import DocstringMeta
import numpy as np
from sklearn.preprocessing import OneHotEncoder

__all__: list[str] = [
    "is_notebook",
    "one_hot_encode_list",
    "seed_all",
    "ExampleSegmentationData",
]

from bitfount import config

_logger = logging.getLogger(__name__)

DEFAULT_SEED: int = 42
DOCSTRING_STYLE = docstring_parser.DocstringStyle.GOOGLE


class StringLoader(importlib.abc.Loader):
    """A custom loader that loads Python code from a string."""

    # Based on https://docs.python.org/3.1/library/importlib.html#module-importlib.abc

    def __init__(self, code: str):
        """Initialize the loader with the given code.

        Args:
            code (str): The Python code to load.
        """
        self.code = code

    def get_code(self, fullname: str) -> str:
        """Get the code for the given module.

        Args:
            fullname (str): The full name of the module.

        Returns:
            str: The Python code for the module.
        """
        return self.code

    def exec_module(self, module: ModuleType) -> None:
        """Execute the module's code in the module's namespace.

        Args:
            module (ModuleType): The module object to execute the code in.
        """
        # TODO: [BIT-3562] Can we avoid exec?
        exec(self.code, module.__dict__)  # nosec exec of arbitrary code


def is_notebook() -> bool:
    """Checks if code is being executed in a notebook or not."""
    try:
        # get_ipython() is always available in a notebook, no need to import
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined] # Reason: captured by NameError # noqa: E501
        return bool(shell == "ZMQInteractiveShell")  # True if ran from Jupyter notebook
    except NameError:
        return False  # Standard Python interpreter


def _inspect_get_file(obj: Any) -> str:
    """This is a wrapper around `inspect.getfile` that works with IPython.

    This is required because `inspect.getfile` does not work with classes defined in a
    notebook due to them not having a `__file__` attribute. Functions in a notebook are
    unaffected.

    Raises:
        TypeError: If the object source code cannot be retrieved.
    """
    # Only classes need a workaround, if the object is not a class we can just fall back
    # to `inspect.getfile`.
    if not inspect.isclass(obj):
        return inspect.getfile(obj)

    # Lookup by parent module as in `inspect.getfile`. This is the flow for classes that
    # are not defined in a notebook.
    if hasattr(obj, "__module__"):
        object_ = sys.modules.get(obj.__module__)
        if object_ is not None and hasattr(object_, "__file__"):
            return str(object_.__file__)

    # If parent module is __main__, lookup by methods. This is the flow for classes that
    # are defined in a notebook.
    for _, member in inspect.getmembers(obj):
        if (
            inspect.isfunction(member)
            and obj.__qualname__ + "." + member.__name__ == member.__qualname__
        ):
            return inspect.getfile(member)

    # If all else fails, raise an error.
    raise TypeError(f"Source for {obj.__name__} not found.")


def _get_ipython_extract_symbols() -> Callable[[Any, Any], tuple[list, list]]:
    """Returns the `extract_symbols` function from IPython.

    This should only be imported from an environment which has IPython installed.
    """
    from IPython.core.magics.code import extract_symbols

    return extract_symbols


def _get_object_source_code(obj: Any) -> str:
    """Returns the source code for an object as a string.

    If the object is defined in a file, the function simply returns the result from
    `inspect.getsource`. If the object is defined in a notebook, a different approach
    must be taken to extract the source code.
    """
    if is_notebook():
        extract_symbols = _get_ipython_extract_symbols()

        # Extract the source code from the cell the object is defined in as a string.
        cell_code = "".join(linecache.getlines(_inspect_get_file(obj)))
        # Extracts the first symbol (by name) that is defined in the cell that the
        # object is defined in. This should be the object itself.
        class_code: str = extract_symbols(cell_code, obj.__name__)[0][0]
        return class_code

    return inspect.getsource(obj)


def seed_all(seed_value: Optional[int] = None) -> None:
    """Sets random seed for `numpy`, `python.random` and any other relevant library.

    If `pytorch` is used as the backend, this is just a wrapper around the
    `seed_everything` function from `pytorch-lightning`.

    :::info

    `PYTHONHASHSEED` is not set as an environment variable because this has no effect
    once the process has been started. If you wish to set this, you should set it
    yourself in your own environment before running python.

    :::

    Args:
        seed_value: The seed value to use. If None, uses the default seed (42).
    """
    seed_value = DEFAULT_SEED if seed_value is None else seed_value

    # Try to seed other libraries that may be present
    # Torch
    try:
        import pytorch_lightning as pl

        _logger.debug(f"Setting seed of torch, random and numpy to {seed_value}")
        # This call takes care of setting the seed for all libraries including
        # random and numpy as well as pytorch. `workers=True` ensures that the workers
        # for the dataloaders are also seeded.
        pl.seed_everything(seed_value, workers=True)
    except ModuleNotFoundError:
        _logger.debug(f"Setting seed of random and numpy to {seed_value}")
        random.seed(seed_value)
        np.random.seed(seed_value)


def _add_this_to_list(
    this: Union[Any, Iterable[Any]], the_list: list[Any]
) -> list[Any]:
    """Adds this to the list and returns the list.

    `this` is checked not be `None` or to already exist in `the_list` before it is
    appended. If `this` is an iterable, `the_list` is extended to add the individual
    elements in `this` with the same constraints as just mentioned.

    Args:
        this: The object to add to the list. Can be an iterable.
        the_list: The list to which `this` gets appended to or extended by.

    Returns:
        The list but with any new elements added to the end to ensure the original order
        of the list is preserved.
    """
    if not isinstance(this, Iterable) or isinstance(this, str):
        this = [this]

    for i in this:
        if i is not None and i not in the_list:
            the_list.append(i)

    return the_list


def _array_version(this: Union[Any, Iterable[Any]]) -> list[Any]:
    """Returns this as a list.

    Checks if 'this' is an iterable, in which case it returns it as a list (unless
    it's a string), otherwise it wraps it as a single element list.
    """
    if isinstance(this, Iterable) and not isinstance(this, str):
        return list(this)
    return [this]


def one_hot_encode_list(
    targets: Union[
        np.ndarray, Iterable[np.ndarray], Iterable[int], Iterable[Iterable[int]]
    ],
) -> np.ndarray:
    """Converts a list of targets into a list of one-hot targets."""
    arr_targets: np.ndarray = np.asarray(targets)

    # Can only encode 1D or 2D targets
    if not (1 <= arr_targets.ndim <= 2):
        raise ValueError(
            f"Incorrect number of dimensions for one-hot encoding; "
            f"expected 1 or 2, got {arr_targets.ndim}"
        )

    # OneHotEncoder needs a 2D numpy array so if this is 1D, needs reshape
    if arr_targets.ndim == 1:
        arr_targets = arr_targets.reshape(-1, 1)

    # Ensure output is ndarray of correct types
    encoder = OneHotEncoder(categories="auto", sparse_output=False, dtype=np.uint8)
    # sparse_output=False guarantees output of ndarray
    return cast(np.ndarray, encoder.fit_transform(arr_targets))


def _get_module_from_source(model_source: Union[Path, str]) -> ModuleType:
    """Creates a module from a file or string and returns the module.

    :::caution

    This explicitly does NOT add it to sys.modules, so it's not available
    for import elsewhere. If you want the module in sys.modules, use
    _import_module_from_file instead.

    :::

    Args:
        model_source: The path to the module file or a string
        containing the module code.

    Returns:
        The module.

    Raises:
        ImportError: If the module cannot be imported.
    """
    if isinstance(model_source, Path):
        path = model_source.expanduser().absolute()
        module_name = path.stem
        # Load the module from the file WITHOUT SAVING IT TO sys.modules
        # See: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly  # noqa: E501
        spec = importlib.util.spec_from_file_location(module_name, path)
    elif isinstance(model_source, str):
        # Load module from string
        module_name = f"_generated_module_{id(model_source)}"  # Generate unique name
        loader = StringLoader(model_source)
        spec = importlib.util.spec_from_loader(
            module_name, loader=loader, origin=model_source
        )
    else:
        raise ValueError(f"Unsupported model source type: {type(model_source)}")

    try:
        # `spec` has type `ModuleSpec | None`. If it is None, an error is raised which
        # caught by the `try...except` block
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type] # Reason: See comment # noqa: E501
        sys.modules[module_name] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr] # Reason: See comment # noqa: E501
    except Exception as ex:
        msg = f"Unable to load code from {model_source}"
        _logger.debug(msg, exc_info=True)
        raise ImportError(msg) from ex

    return module


def _import_module_from_file(
    path_to_module: Path, parent_module: Optional[str] = None
) -> tuple[ModuleType, str]:
    """Imports a module from a file path and returns the module.

    Ensures module is added to sys.modules.

    Args:
        path_to_module: The path to the module file.
        parent_module: The parent module this module should be imported under.

    Returns:
        The module and the base module name (i.e. the module name without any parent
        package elements such as `path` for `os.path`).

    Raises:
        ImportError: If the module cannot be imported.
    """
    path = path_to_module.expanduser().absolute()
    module_name = path.stem

    # Modify module name to reference parent if included
    if parent_module:
        fqual_module_name = f"{parent_module}.{module_name}"
    else:
        fqual_module_name = module_name

    if (existing_module := sys.modules.get(fqual_module_name)) is None:
        _logger.debug(f"Dynamically importing {path_to_module} as {fqual_module_name}")

        # Load the module from the file and import it
        # See: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly  # noqa: E501
        spec = importlib.util.spec_from_file_location(fqual_module_name, path)
        try:
            # `spec` has type `ModuleSpec | None`. If it is None, an error is raised
            # which is caught by the `try...except` block
            module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type] # Reason: See comment # noqa: E501
            sys.modules[fqual_module_name] = module
            spec.loader.exec_module(module)  # type: ignore[union-attr] # Reason: See comment # noqa: E501
        except Exception as ex:
            # If we added the module to sys.modules, remove it as the import failed
            sys.modules.pop(fqual_module_name, None)  # "None" default prevents KeyError

            msg = f"Unable to load code from {path_to_module}"
            _logger.debug(msg, exc_info=True)
            raise ImportError(msg) from ex

        return module, module_name
    else:
        if (
            hasattr(existing_module, "__file__")
            and existing_module.__file__ is not None
            and Path(existing_module.__file__) != path
        ):
            _logger.error(
                "A module with the same name but a different source already exists,"
                " cannot register"
            )
            raise ImportError(
                f"A module with this name already exists: {existing_module}"
            )
        else:
            _logger.debug(
                f"{str(path)} is already loaded as {existing_module.__name__},"
                f" will not reload"
            )
            return existing_module, module_name


def _get_non_abstract_classes_from_module(
    model_source: Union[Path, str],
) -> dict[str, type]:
    """Returns non-abstract classes from a module path.

    Returns a dictionary of non-abstract class names and classes present within a
    module file which is given as a Path object.
    """
    if not isinstance(model_source, (Path, str)):
        raise ValueError(f"Unsupported model source type: {type(model_source)}")

    module = _get_module_from_source(model_source=model_source)

    classes = {
        name: class_
        for name, class_ in vars(module).items()
        if inspect.isclass(class_)
        # types.GenericAlias instances (e.g. list[str]) are reported as classes by
        # inspect.isclass() but are not compatible with issubclass() against an
        # abstract class, so we need to exclude.
        # See: https://github.com/python/cpython/issues/101162
        # TODO: [Python 3.11] This issue is fixed in Python 3.11 so can remove
        and not isinstance(class_, GenericAlias)
        and not inspect.isabstract(class_)
    }

    return classes


# TypeVars for merge_list_of_dicts
KT = TypeVar("KT")  # Key type.
VT = TypeVar("VT")  # Value type.


def _merge_list_of_dicts(
    lod: Iterable[Mapping[KT, Union[VT, Iterable[VT]]]],
) -> dict[KT, list[VT]]:
    """Converts a list of dicts into a dict of lists.

    Each element in the dicts should be a single element or a list of elements.

    :::info

    Any iterable elements will be flattened into the final list, any single
    elements will be appended.

    :::

    The keys in each dict should be identical.

    Args:
        lod: A list of dicts to merge.

    Returns:
        A dictionary of lists where each value is the merged values from the
        input list of dicts.
    """
    # First check that all the keys are identical
    if not _check_dicts_in_list_have_same_keys(lod):
        raise ValueError(
            "Not all dicts in the list have the same keys. Unable to merge."
        )

    # Merge into singular lists rather than a list of dicts
    merged: defaultdict[KT, list[VT]] = defaultdict(list)

    for i in lod:
        for k, v in i.items():
            # We ignore the mypy errors on the `extend` and `append` calls because
            # we don't know the type of v. Instead rely on the `try...except` block
            # for type safety
            try:
                # We explicitly don't want to merge/flatten a list of strings into a
                # single long string, so fail out and ensure we are using the append().
                if isinstance(v, str):
                    raise TypeError("Should not merge/flatten strings together.")

                # Attempt to extend first (for outputs and targets).
                # This will _flatten_ any iterable of iterables into a single list.
                # This is of particular importance for things like numpy arrays,
                # as it will convert a list of X arrays of shape YxZ into a list
                # of XxY arrays of shape (Z,).
                merged[k].extend(v)  # type: ignore[arg-type]  # Reason: will TypeError if not Iterable[VT]  # noqa: E501
            except TypeError:
                # Otherwise if not iterable, append
                v = cast(VT, v)
                merged[k].append(v)

    return merged


def _check_dicts_in_list_have_same_keys(lod: Iterable[Mapping[KT, Any]]) -> bool:
    """Check that all dicts in a list of dicts have the exact same keys.

    Args:
        lod: The list of dicts to check the keys of.

    Returns:
        True iff all dicts in the list have the same keys, False otherwise.
    """
    baseline_keys: set[KT] = set()
    for i, d in enumerate(lod):
        # If this is the first dict, use it to set the baseline keys
        if i == 0:
            baseline_keys = set(d.keys())
        # Otherwise, compare them
        else:
            if set(d.keys()) != baseline_keys:
                return False

    # If we get to this point, all of the dicts must have had the same keys
    return True


@dataclass
class _MegaBytes:
    """Thin wrapper for bytes->MB conversion."""

    whole: int
    fractional: float


def _get_mb_from_bytes(num_bytes: int) -> _MegaBytes:
    """Converts a number of bytes into the number of megabytes.

    Returns a tuple of the number of whole megabytes and the number of megabytes
    as a float.
    """
    mb: float = num_bytes / (1024 * 1024)
    return _MegaBytes(int(mb), mb)


_LOG_LEVELS_STR = Literal[
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
]

_LOG_LEVELS_NUM = Literal[
    50,  # logging.CRITICAL
    40,  # logging.ERROR
    30,  # logging.WARNING
    20,  # logging.INFO
    10,  # logging.DEBUG
]
_LOG_LEVELS = Union[_LOG_LEVELS_STR, _LOG_LEVELS_NUM]


def _find_logger_filenames(
    logger: logging.Logger, level: _LOG_LEVELS
) -> Optional[list[str]]:
    """Finds all files that are being logged to for a given logger and level."""
    # Convert to int-log-level if needed
    if isinstance(level, str):
        level = logging.getLevelName(level)
    level = cast(_LOG_LEVELS_NUM, level)

    # If logger is not enabled for target level, will never output
    if not logger.isEnabledFor(level):
        return None

    # Otherwise, iterate up through the logger hierarchy and note any FileHandler
    # files that will be output to for the target level.
    log_files: list[str] = []
    curr_logger: Optional[logging.Logger] = logger
    while curr_logger:
        handlers = curr_logger.handlers
        log_files.extend(
            h.baseFilename
            for h in handlers
            if isinstance(h, logging.FileHandler) and h.level <= level
        )
        curr_logger = curr_logger.parent  # will be None if root logger

    # Return either the list of file paths or None if no files
    # were found.
    if log_files:
        return log_files
    else:
        return None


_no_tb_limit_sentinel = object()


@contextmanager
def _full_traceback() -> Generator[None, None, None]:
    """Temporarily sets tracebacklimit to original limit."""
    # If sys.tracebacklimit has been set, we need to store its current value
    orig_limit: Union[int, object]
    try:
        orig_limit = sys.tracebacklimit
    except AttributeError:
        orig_limit = _no_tb_limit_sentinel

    try:
        # Reset traceback limit to default (done by deleting the attribute)
        if orig_limit is not _no_tb_limit_sentinel:
            del sys.tracebacklimit

        yield
    finally:
        # Set back to original value again if needed
        if orig_limit is not _no_tb_limit_sentinel:
            sys.tracebacklimit = cast(int, orig_limit)


_fatal_logger = logging.getLogger("bitfount.fatal")


def _handle_fatal_error(
    ex: Exception,
    logger: logging.Logger = _fatal_logger,
    log_msg: Optional[str] = None,
) -> NoReturn:
    """Determines how to handle fatal errors depending on configuration.

    How the error is handled will depend on the configuration:
        - Normal, API-based use:
            - Exception is raised and system errors out.
            - Full stack trace logged at CRITICAL.

        - Logs limited, API-based use:
            - Exception is raised and system errors out.
            - Limited stack trace/error logged at CRITICAL.
            - Full stack trace logged at DEBUG.

        - Normal, CLI-based use:
            - Exception is captured and sys.exit() is called.
            - Full stack trace logged at CRITICAL.

        - Logs limited, CLI-based use:
            - Exception is captured and sys.exit() is called.
            - Limited stack trace/error logged at CRITICAL.
            - Full stack trace logged at DEBUG.

    Logs limited functionality can be configured by setting the BITFOUNT_LIMIT_LOGS
    environment variable to True.
    CLI mode functionality can be configured by setting the BITFOUNT_CLI_MODE
    environment variable to True. This is automatically done if the Bitfount library
    is called from any of the CLI scripts provided.

    Args:
        ex: The exception to handle.
        logger: The logger to use for logging out details. If not provided a
            "bitfount.fatal" logger is used.
        log_msg: The log message to use. If not provided the str() representation
            of the exception is used.
    """
    # Create log_msg from exception if one not explicitly provided
    if not log_msg:
        log_msg = str(ex)

    # Determine how full stack trace will be logged
    if config.settings.logging.limit_logs:
        # Will want to say "see debug log for more details"
        additional_log_msg = ""
        if debug_log_files := _find_logger_filenames(logger, "DEBUG"):
            if not log_msg.endswith("."):
                additional_log_msg += "."
            debug_log_files_str = ", ".join(debug_log_files)
            additional_log_msg += f" Full details logged to {debug_log_files_str}."
        logger.critical(log_msg + additional_log_msg)
        with _full_traceback():
            logger.debug(log_msg, exc_info=ex)
    else:
        with _full_traceback():
            logger.critical(log_msg, exc_info=ex)

    if config._BITFOUNT_CLI_MODE:
        # Exit instead of raising exception
        sys.exit(ex)  # type: ignore[arg-type] # Reason: This is allowed
    else:
        # Exceptions get raised
        # Need to use `raise X` form here as we're not directly in an `except` clause
        raise ex


# Example segmentation image dataset class
class ExampleSegmentationData:
    """A synthetic segmentation dataset example.

    This class is used mainly in Tutorial 10 and testing.
    """

    def masks_to_colorimg(self, masks: np.ndarray) -> np.ndarray:
        """Adds RGB coloring to masks.

        Args:
            masks: The masks to which we want to add coloring.

        Returns:
              The masks with RGB coloring applied to them.
        """
        colors = np.asarray(
            [(201, 58, 64), (242, 207, 1)]
        )  # , (0, 152, 75)])#, (101, 172, 228),(56, 34, 132), (160, 194, 56)])

        colorimg = np.ones((masks.shape[1], masks.shape[2], 3), dtype=np.float32) * 255
        channels, height, width = masks.shape
        for y in range(height):
            for x in range(width):
                selected_colors = colors[masks[:, y, x] > 0.5]

                if len(selected_colors) > 0:
                    colorimg[y, x, :] = np.mean(selected_colors, axis=0)

        return colorimg.astype(np.uint8)

    def generate_data(
        self, height: int, width: int, count: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate random data given height, weight and count.

        Args:
            height: The height of the images to generate.
            width: The width of the images to generate.
            count: The number of images to generate.
        """
        x, y = zip(
            *[self._generate_img_and_mask(height, width) for i in range(0, count)]
        )

        X = np.asarray(x) * 255
        X = X.repeat(3, axis=1).transpose([0, 2, 3, 1]).astype(np.uint8)
        Y = np.asarray(y)
        return X, Y

    def _generate_img_and_mask(
        self, height: int, width: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """Creates image and mask given height and width."""
        shape = (height, width)
        # Assign random location to triangle and circle
        triangle_location = self._get_random_location(*shape)
        circle_location2 = self._get_random_location(*shape, zoom=1.5)

        # Create input image
        arr = np.zeros(shape, dtype=bool)
        arr = self._add_triangle(arr, *triangle_location)
        arr = self._add_circle(arr, *circle_location2, fill=True)
        arr = np.reshape(arr, (1, height, width)).astype(np.float32)

        # Create target masks
        masks = np.asarray(
            [
                self._add_circle(
                    np.zeros(shape, dtype=bool), *circle_location2, fill=True
                ),
                self._add_triangle(np.zeros(shape, dtype=bool), *triangle_location),
            ]
        ).astype(np.float32)
        return arr, masks

    def _get_random_location(
        self, height: int, width: int, zoom: float = 1.0
    ) -> tuple[int, int, int]:
        """Gets a random location for placing shapes."""
        x = int(
            width * random.uniform(0.1, 0.9)  # nosec B311 # "random" usage # reason: see below
        )
        y = int(
            height * random.uniform(0.1, 0.9)  # nosec B311 # "random" usage # reason: see below
        )
        size = int(
            min(width, height)
            * random.uniform(0.06, 0.12)  # nosec B311 # "random" usage # reason: see below
            * zoom
        )
        # We only use random for generating images for a demo segmentation
        # dataset used in testing an as an example in tutorial 11
        return (x, y, size)

    def _add_triangle(self, arr: np.ndarray, x: int, y: int, size: int) -> np.ndarray:
        """Adds a triangle to the input arrays."""
        s = int(size / 2)
        triangle = np.tril(np.ones((size, size), dtype=bool))
        arr[x - s : x - s + triangle.shape[0], y - s : y - s + triangle.shape[1]] = (
            triangle
        )
        return arr

    def _add_circle(
        self, arr: np.ndarray, x: int, y: int, size: int, fill: bool = False
    ) -> np.ndarray:
        """Adds a circle to the input arrays."""
        xx, yy = np.mgrid[: arr.shape[0], : arr.shape[1]]
        circle = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
        new_arr = np.logical_or(
            arr,
            np.logical_and(circle < size, circle >= size * 0.7 if not fill else True),
        )
        return new_arr


# type var for class
_C = TypeVar("_C", bound=type)


def delegates(
    keep: bool = False, exclude_doc_meta: Optional[list[Any]] = None
) -> Callable[[_C], _C]:
    """Decorator to replace `**kwargs` in signature.

    The `@delegates()` decorator should be added to all classes that inherit
    from a parent class. It will ensure that the signature of the class
    includes all the arguments from the parent class(es) as well as combine
    the docstring of all the parent classes to make sure all args, attributes
    and errors are reflected in the class it decorates.
    """

    def _decorate_class(klass: _C) -> _C:
        # Mypy complains that DocstringMeta is not iterable, when it is,
        # hence the "type: ignore"s.

        # get the signature of the decorated class
        from_klass = klass.__init__  # type: ignore[misc] # Reason: just "unsound" not impossible ('Accessing "__init__" on an instance is unsound, since instance.__init__ could be from an incompatible subclass') # noqa: E501
        init_sig = inspect.signature(from_klass)
        init_params = dict(init_sig.parameters)

        # get the docstring of the decorated class
        klass_doc = docstring_parser.parse(
            klass.__doc__ if klass.__doc__ else "", style=DOCSTRING_STYLE
        )

        # aux variables to keep track of everything
        # "combined" keeps track of all args, attributes and errors across all classes.
        combined: defaultdict[type[DocstringMeta], list[DocstringMeta]] = defaultdict(
            list
        )
        # "metas" keeps track of all args, attributes and errors for one class only.
        metas: defaultdict[type[DocstringMeta], list[DocstringMeta]] = defaultdict(list)
        # "arg_names" keeps track of all the arg (also attrs & errors)
        # names to ensure there are no duplicates.
        arg_names: list[str] = []

        # get all the metadata from the decorated class' docstring and...
        for meta in klass_doc.meta:
            meta_type = type(meta)
            if exclude_doc_meta is not None:
                if meta_type in exclude_doc_meta:
                    continue
            metas[meta_type].append(meta)
        # ...feed it into our aux variables
        for meta_type, meta_list in metas.items():
            combined[meta_type].extend(meta_list)
            arg_names += [arg.args[1] for arg in meta_list]

        if "kwargs" in init_params:
            init_kwargs = init_params.pop("kwargs")
        else:
            init_kwargs = None

        # We only need the ancestors from our own repo.
        ancestors = [
            ancestor
            for ancestor in klass.__mro__
            if ancestor.__module__.startswith("bitfount") and ancestor != klass
        ]
        # ancestors.sort(key=lambda x: len(x.__module__.split(".")))

        # now we loop through all the base classes of the
        # decorated class and extract the relevant items
        for ancestor in ancestors:
            # Load public methods from parent classes

            # pdoc checks whether the methods are in the class's dictionary,
            # so we need to add them to the relevant class to ensure they
            # show up in the docs.
            to_klass_dict = ancestor.__dict__
            # get the abstract methods
            if hasattr(ancestor, "__abstractmethods__"):
                abstract_methods = ancestor.__abstractmethods__
            else:
                abstract_methods = []

            # Get the public non-abstract attributes
            new_dict_items = {
                attr_name: attr
                for attr_name, attr in to_klass_dict.items()
                if not attr_name.startswith("_")
                and attr_name not in klass.__dict__
                and attr_name not in abstract_methods
            }

            for attr_name, attr in new_dict_items.items():
                # `If` checks below explained:
                # 1. We only need to document the methods from bitfount modules.
                # 2. Only get the public methods from parent classes.
                # 3. Check if the methods is not already in the class's dictionary.
                # 4. Only get callables (i.e. functions).
                # This will no affect in any way the error
                # handling for abstract methods not being implemented.
                if (
                    ancestor.__module__.startswith("bitfount")
                    and not attr_name.startswith("_")
                    and attr_name not in klass.__dict__
                    and callable(to_klass_dict[attr_name])
                ):
                    # `__dict__` is a mappingproxy which cannot be
                    # updated in the same way we would update a
                    # dictionary, so need the setattr instead.
                    setattr(klass, attr_name, attr)

            # get the docstring and the metadata
            item_doc = docstring_parser.parse(
                ancestor.__doc__ if ancestor.__doc__ else "", style=DOCSTRING_STYLE
            )

            # "metas" keeps track of all args, attributes and errors for one class only.
            metas = defaultdict(list)  # reset to empty
            for meta in item_doc.meta:
                meta_type = type(meta)
                if exclude_doc_meta is not None:
                    if meta_type in exclude_doc_meta:
                        continue
                metas[meta_type].append(meta)
            # keep track in aux variables
            for meta_type, meta_list in metas.items():
                to_add = [arg for arg in meta_list if arg.args[1] not in arg_names]
                arg_names += [arg.args[1] for arg in meta_list]
                combined[meta_type].extend(to_add)

            # now sort alphabetically the args, attrs
            # and errors in the docstring.
            # NOTE: have to sort in place in order to keep the defaultdict
            for k, v in combined.items():
                combined[k] = sorted(v, key=lambda d: d.args[1])

            # Now get the signature.
            to_klass = ancestor.__init__  # type: ignore[misc] # Reason: _can_ access __init__ directly # noqa: E501
            # extract the "self" param from the signature
            self_param = init_params.pop("self")
            # get the values without default first
            s1 = {
                param_name: param
                for param_name, param in inspect.signature(to_klass).parameters.items()
                if param.default == inspect.Parameter.empty
                and param_name not in init_params
                and param_name not in ["args", "kwargs"]
            }
            # "self" needs to go first, then unparametrised args
            # and then all the other args otherwise an error is raised.
            init_params = {"self": self_param, **s1, **init_params}
            # Then add the params which have default values.
            s2 = {
                param_name: param
                for param_name, param in inspect.signature(to_klass).parameters.items()
                if param.default != inspect.Parameter.empty
                and param_name not in init_params
            }

            init_params.update(s2)

        # Check if kwargs should be kept in the signature
        if keep and init_kwargs is not None:
            init_params["kwargs"] = init_kwargs

        # replace the decorated class's signature.
        from_klass.__signature__ = init_sig.replace(parameters=init_params.values())  # type: ignore[arg-type] # Reason: see below # noqa: E501
        # Mypy complains that Argument "parameters" to "replace" of
        # "Signature" has incompatible type "dict_values[str, Parameter]";
        # expected "Union[Sequence[Parameter], type[_void], None], even though
        # Signature.replace is untyped.

        # Now, replace the decorated class's docstring metadata.
        klass_doc.meta = list(chain(*combined.values()))
        klass.__doc__ = docstring_parser.compose(klass_doc, style=DOCSTRING_STYLE)

        return klass

    return _decorate_class


def model_id_from_elements(
    username: str,
    model_name: str,
    model_version: Optional[int] = None,
) -> str:
    """Construct a model ID from individual elements.

    Creates a model ID (e.g. "username/model_name:model_version") from the
    individual elements that make it up.
    """
    return f"{username}/{model_name}:{model_version or 'latest'}"


def str_is_int(s: str) -> bool:
    """Check if a string represents an integer."""
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


_K = TypeVar("_K")
_V = TypeVar("_V", bound=Hashable)


def invert_dict(d: dict[_K, _V]) -> dict[_V, list[_K]]:
    """Inverts a dict K->V to V->list[K].

    The list[K] is needed as there is no guarantee of uniqueness amongst the dict's
    values.
    """
    inverted = defaultdict(list)
    for k, v in d.items():
        inverted[v].append(k)
    return dict(inverted)


def dict_to_dict_cache_key(d: dict[_K, _V]) -> frozenset[tuple[_K, _V]]:
    """Converts a dictionary to a cache key.

    The cache key is a frozenset of tuples (k, v) for each k, v in the input dict.
    """
    return frozenset((k, v) for k, v in d.items())


def dict_cache_key_to_dict(cache_key: frozenset[tuple[_K, _V]]) -> dict[_K, _V]:
    """Converts a cache key back to a dictionary.

    The cache key is a frozenset of tuples (k, v) for each k, v in the input dict.
    """
    return dict(cache_key)
