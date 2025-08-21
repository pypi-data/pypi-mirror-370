"""Contains classes designed for easy caching/persistence.

These classes are designed to be used in cases where you would normally use a `dict`
but want to have the ability to persist between restarts/runs or do not/cannot store
the entire dict in memory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import atexit
from collections.abc import Container, Iterator, MutableMapping
from contextlib import AbstractContextManager
import hashlib
import json
import logging
import multiprocessing
import os.path
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from types import TracebackType
from typing import (
    Any,
    Callable,
    Final,
    Literal,
    Optional,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
)
import zlib

from cryptography.fernet import Fernet
import diskcache
from diskcache import UNKNOWN
from typing_extensions import Self, TypeAlias, override

from bitfount.config import settings
from bitfount.encryption.encryption import _DeterministicAESEncryption

_logger = logging.getLogger(__name__)

_JSON: TypeAlias = dict[str, Any] | list[Any] | str | int | float | bool | None
_T = TypeVar("_T")


CACHE_DIR: Final[Path] = settings.paths.cache_dir
_ADD_SENTINEL: Final[str] = "ENTRY_ADDED"

# See _handle_cache_name_length() for details for why this is needed.
#
# Value was chosen as allows expected cache to contain one of (cache_name,
# datasource_name) and one of (project_id, task_id) before hashing will be needed,
# assuming that cache_name or datasource_name are reasonable lengths.
MAX_CACHE_NAME_LEN: Final[int] = 60

# Use multiprocessing RLock to give both thread- and process-safe interactions
_CACHE_MAPPING_FILE_LOCK = multiprocessing.RLock()

FUNCTION_CACHE_TTL = 21_600  # 6 hours in seconds


class Cache(MutableMapping[str, _JSON], AbstractContextManager, ABC):
    """An on-disk cache/persistence class.

    This can be used as though a standard mutable mapping.
    """

    def __init__(self, cache_name: str) -> None:
        self.cache_name = cache_name

    def set(self, k: str, v: _JSON) -> None:
        """Set a value against key."""
        self[k] = v

    def add(self, k: str) -> None:
        """Add key to cache.

        Stores key with a sentinel value so that key can be checked for via `key in
        cache` but where the value does not matter.
        """
        return self.set(k, _ADD_SENTINEL)

    def delete(self, k: str, error: bool = False) -> None:
        """Delete key from cache.

        Raises:
            KeyError: if key is not present and `error` is True
        """
        try:
            del self[k]
        except KeyError:
            if error:
                raise

    @abstractmethod
    def close(self) -> None:
        """Close the cache."""
        ...

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        self.close()

    @abstractmethod
    def delete_cache(self) -> None:
        """Delete the cache."""
        ...


class _DiskcacheCache(Cache):
    """Cache implementation using diskcache as the backing."""

    def __init__(
        self,
        cache_name: str,
        json_compression_level: int = 6,
        use_tmp_dir: bool = False,
    ) -> None:
        if json_compression_level > 9:
            _logger.warning(
                f"Cache compression level, {json_compression_level},"
                f" is higher than the maximum, 9. Setting to 9."
            )
            json_compression_level = 9
        if json_compression_level < 0:
            _logger.warning(
                f"Cache compression level, {json_compression_level},"
                f" is lower than the minimum, 0. Setting to 0."
            )
            json_compression_level = 0

        super().__init__(cache_name=cache_name)

        self._tmp_dir: Optional[TemporaryDirectory] = None

        if use_tmp_dir:
            self._tmp_dir = TemporaryDirectory(prefix="bitfount_cache_")
            directory = Path(self._tmp_dir.name) / self.cache_name
        else:
            directory = CACHE_DIR / self.cache_name
        _logger.debug(f"Creating cache at {str(directory)}")
        self._db = diskcache.Cache(
            directory=str(directory),
            disk=diskcache.JSONDisk,
            disk_compress_level=json_compression_level,
            eviction_policy="none",
        )

    def __getitem__(self, key: str, /) -> _JSON:
        # mypy: underlying diskcache.Cache isn't typed
        return cast(_JSON, self._db[key])

    def __setitem__(self, key: str, value: _JSON, /) -> None:
        self._db[key] = value

    def __delitem__(self, key: str, /) -> None:
        del self._db[key]

    def __len__(self) -> int:
        return len(self._db)

    def __iter__(self) -> Iterator[str]:
        return iter(self._db)

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        self._db.close()

    def delete_cache(self) -> None:
        # Ensure closed first
        try:
            self.close()
        except Exception as e:
            _logger.warning(
                f"Error when trying to close cache directory: {self._db.directory}."
                f" Got: {e}"
            )

        try:
            # If we were using a temporary directory, make use of its own cleanup
            if self._tmp_dir is not None:
                self._tmp_dir.cleanup()
            else:
                shutil.rmtree(self._db.directory)
        except OSError as ose:  # Windows wonkiness
            _logger.error(
                f"Error when trying to delete cache directory: {self._db.directory}."
                f" Got: {ose}"
            )


def get_cache(
    *,
    cache_name: Optional[str] = None,
    datasource_name: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    use_tmp_dir: bool = False,
) -> Cache:
    """Create/retrieve cache given various name/specifier options.

    At least one specifier option must be provided.

    If a cache with the same specifiers exists, it will be opened and returned. If
    one does not exist it will be created.

    Specifiers should be provided when a cache that is associated with a given
    datasource/task/project is wanted. For instance, if a cache is wanted for a given
    datasource for a given project, both datasource_name and project_id should be
    provided. Such a cache would be shared across all task runs within that project
    when using that datasource.

    Args:
        cache_name: Human-provided name/additional specifier for cache.
        datasource_name: Name of datasource this cache is related to.
        project_id: UUID of the project this cache is related to.
        task_id: UUID of the task run this cache is related to.
        use_tmp_dir: Whether to use a temporary directory for the cache. If this is
            true then the cache is unlikely to be reusable across runs.

    Returns:
        Cache instance named for this combination of specifiers.

    Raises:
        ValueError: if no specifiers are provided.
    """
    if all(i is None for i in (cache_name, datasource_name, project_id, task_id)):
        raise ValueError(
            "At least one of"
            " cache_name,"
            " datasource_name,"
            " project_id"
            " or task_id,"
            " must be provided."
        )

    full_cache_name_components: list[str] = []
    if cache_name:
        full_cache_name_components.append(cache_name)
    if datasource_name:
        full_cache_name_components.append(f"ds_{datasource_name}")
    if project_id:
        full_cache_name_components.append(f"proj_{project_id}")
    if task_id:
        full_cache_name_components.append(f"task_{task_id}")

    full_cache_name = "_".join(full_cache_name_components)
    full_cache_name = _make_file_name_safe(full_cache_name)

    # Shrink cache name if overly long, add details to store
    full_cache_name = _handle_cache_name_length(full_cache_name)

    _logger.debug(
        f"Creating/locating cache {full_cache_name} for"
        f" {cache_name=},"
        f" {datasource_name=},"
        f" {project_id=},"
        f" and {task_id=}"
    )
    return _DiskcacheCache(full_cache_name, use_tmp_dir=use_tmp_dir)


def _make_file_name_safe(filename: str) -> str:
    keepcharacters = (" ", ".", "_", "-")
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


def _handle_cache_name_length(cache_name: str) -> str:
    """Reduce cache name if too long, store details elsewhere.

    Given the potential inclusion in the cache names of very long components (such as
    UUIDs), we may find that cache names will hit OS-specific path/file name limits.
    This function provides the ability to reduce those cache names to a shortened
    version whilst still maintaining information on what the cache actually
    corresponds to.
    """
    # DEV: Max length for file names/paths differ depending on OS.
    #      - Windows 10: 260 characters (path limit)
    #      - Windows 11: 32,767 characters (path limit)
    #      - macOS: 1024 characters (path limit)
    #      - macOS: 255 characters (file name limit)
    #
    #      Further details can be found using `os.pathconf("/", "PC_PATH_MAX")` and
    #      `os.pathconf("/", "PC_NAME_MAX")` for the max path length and max file
    #      name length respectively.

    # If name is short enough, simply return
    if len(cache_name) <= MAX_CACHE_NAME_LEN:
        return cache_name

    mapping_json_file = CACHE_DIR / "cache_name_mappings.json"
    _logger.debug(
        f'Cache name "{cache_name}" is too long;'
        f" reducing to hash"
        f" and the mapping details will be stored at {str(mapping_json_file)}"
    )

    # We use SHAKE256 here as it allows variable length digest output
    new_cache_name = hashlib.shake_256(cache_name.encode()).hexdigest(
        # hexdigest will produce a string of twice the length of the input digest length
        MAX_CACHE_NAME_LEN // 2
    )

    with _CACHE_MAPPING_FILE_LOCK:
        # Get existing mapping JSON store
        mapping_json: dict[str, str]
        if mapping_json_file.exists():
            with open(mapping_json_file, "r") as f:
                mapping_json = json.load(f)
        else:
            mapping_json = {}

        # Add new details
        mapping_json[new_cache_name] = cache_name

        # Export back to file
        with open(mapping_json_file, "w") as f:
            json.dump(mapping_json, f, sort_keys=True, indent=2)

    return new_cache_name


ModeRaw: TypeAlias = Literal[1]
ModeBinary: TypeAlias = Literal[2]

ExpireTime: TypeAlias = Optional[float]
Tag: TypeAlias = Optional[str]
Ignore: TypeAlias = Container[int | str]

_T_co = TypeVar("_T_co", covariant=True)
_P = ParamSpec("_P")


class Memoized(Protocol[_P, _T_co]):
    """A protocol for memoized functions.

    This protocol defines the interface for memoized functions, including
    methods for generating cache keys and calling the memoized function.
    """

    def __cache_key__(self, *args: _P.args, **kwargs: _P.kwargs) -> tuple[Any, ...]:
        """Generate a cache key for the given arguments.

        Args:
            *args: Positional arguments passed to the memoized function.
            **kwargs: Keyword arguments passed to the memoized function.

        Returns:
            A tuple that serves as a unique cache key for the given arguments.
        """
        ...

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _T_co:
        """Call the memoized function.

        If the result for the given arguments is cached, return the cached result.
        Otherwise, call the original function and cache the result before returning.

        Args:
            *args: Positional arguments to pass to the original function.
            **kwargs: Keyword arguments to pass to the original function.

        Returns:
            The result of the memoized function call.
        """
        ...


class FunctionCache(ABC):
    """A cache for applying to function calls à la functools.cache()."""

    @abstractmethod
    def memoize(
        self,
        expire: Optional[float] = FUNCTION_CACHE_TTL,
        ignore: Container[int | str] = (),
    ) -> Callable[[Callable[_P, _T]], Memoized[_P, _T]]:
        """Memoize a function, caching its results.

        This method returns a decorator that can be applied to functions to cache
        their results.

        Args:
            expire: The time-to-live for cached entries in seconds. If None, entries do
                not expire.
            ignore: A container of argument indices or names to ignore when creating
                the cache key. Note that you may need to pass both the index and the
                keyword name if the argument can be passed by both.

        Returns:
            A decorator function that, when applied to a function, returns a memoized
            version of that function.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries from the cache.

        This method removes all memoized results from the cache, effectively
        resetting it.
        """
        ...


class _EncryptedJSONDisk(diskcache.Disk):
    """An encrypted JSON disk implementation for diskcache.

    This class extends the diskcache.Disk class to provide encryption for both keys
    and values stored in the cache, and both keys and values can be any arbitrary
    object that is JSON-serializable.

    Keys are encrypted using a deterministic AES encryption algorithm to ensure that
    they correspond to the same encrypted string each time. This means the keys'
    encryption is slightly weaker than the values but allows comparison of
    ciphertexts to determine if they are for the same key (a necessity for caching).

    Values are encrypted using a Fernet symmetric encryption algorithm to provide
    maximum security. However, this is non-deterministic, and thus we cannot directly
    compare the ciphertext of two values to determine if they are for the same object.
    """

    # mypy_reason:
    #
    # The methods in the parent class (diskcache.Disk) are not typed, instead relying
    # on a third-party library (diskcache-stubs) for type hints. These stubs provide
    # a number of `@overload`s for each method which we would need to replicate in
    # the class.
    #
    # Given that this class is only used internally for a diskcache.Cache instance
    # (and that class doesn't care about the type hints), we instead only type hint
    # for the types we are expecting to use, rather than the full signature.

    def __init__(self, directory: str, compress_level: int = 6, **kwargs: Any) -> None:
        """Initialize the EncryptedJSONDisk.

        Args:
            directory: The directory where the cache will be stored.
            compress_level: The compression level for JSON data (default: 6).
            **kwargs: Additional keyword arguments passed to the parent class.
        """
        super().__init__(directory, **kwargs)
        self.compress_level = compress_level
        self._key_cryptor_key = _DeterministicAESEncryption.generate_key()
        self._key_cryptor_nonce = _DeterministicAESEncryption.generate_nonce()
        self._value_cryptor = Fernet(Fernet.generate_key())

    def put(self, key: Any) -> tuple[memoryview, bool]:  # type: ignore[override] # Reason: see comment in class
        """Convert `key` to the fields `key` and `raw` for the database.

        For this implementation this involves converting the key to a JSON string,
        compressing it, and deterministically encrypting it.

        Args:
            key: key to convert.

        Returns:
            (database key, raw boolean) pair.
        """

        json_bytes: bytes = json.dumps(key).encode("utf-8")
        data = zlib.compress(json_bytes, self.compress_level)
        encrypted_data = _DeterministicAESEncryption.encrypt(
            key=self._key_cryptor_key, plaintext=data, nonce=self._key_cryptor_nonce
        )
        return super().put(encrypted_data)

    def get(self, key: Any, raw: bool) -> Any:
        """Convert fields `key` and `raw` from database-stored key to python version.

        This is to support instances where the key is not a simple string/object but
        is something that needs decoding/transforming to be used in Python. For
        instance if the key was a dict that was converted to a JSON string we would
        want to convert it back into a dict.

        In this implementation this involves decrypting the data, uncompressing it,
        and converting it back into a Python object from the JSON string.

        Args:
            key: database key to convert
            raw: flag indicating raw database storage

        Returns:
            corresponding Python key
        """
        data: bytes = super().get(key, raw)
        decrypted_data = _DeterministicAESEncryption.decrypt(
            key=self._key_cryptor_key, ciphertext=data, nonce=self._key_cryptor_nonce
        )
        return json.loads(zlib.decompress(decrypted_data).decode("utf-8"))

    def store(  # type: ignore[override] # Reason: see comment in class
        self, value: Any, read: bool = False, key: Any = UNKNOWN
    ) -> (
        tuple[Literal[0], ModeRaw, None, memoryview] | tuple[int, ModeBinary, str, None]
    ):
        """Convert `value` to fields for storing in database.

        Fields in question are `size`, `mode`, `filename`, and `value` which indicate
        how/where the value is actually stored (in database or as a file).

        Args:
            value: value to convert
            read: True when value is file-like object. Must be False for this disk type.
            key: key for item (default UNKNOWN)

        Returns:
            (size, mode, filename, value) tuple for Cache table
        """
        if not read:
            json_bytes: bytes = json.dumps(value).encode("utf-8")
            value = zlib.compress(json_bytes, self.compress_level)
            encrypted_value = self._value_cryptor.encrypt(value)
            return super().store(encrypted_value, read, key=key)
        else:
            raise ValueError(f"{read=} is not supported for encrypted cache.")

    def fetch(  # type: ignore[override] # Reason: see comment in class
        self,
        mode: ModeRaw | ModeBinary,
        filename: str,
        value: Any,
        read: bool = False,
    ) -> Any:
        """Convert fields `mode`, `filename`, and `value` from database to actual value.

        Args:
            mode: value mode raw, binary, text, or pickle
            filename: filename of corresponding value
            value: database value
            read: when True, return an open file handle. Must be False for this disk
                type.

        Returns:
            corresponding Python value

        Raises:
            IOError if the value cannot be read
        """
        if not read:
            # mypy: cast as the only call types of fetch() we will be using will be
            # bytes (as that what we're storing)
            data: bytes = cast(bytes, super().fetch(mode, filename, value, read))
            decrypted_data = self._value_cryptor.decrypt(data)
            return json.loads(zlib.decompress(decrypted_data).decode("utf-8"))
        else:
            raise ValueError(f"{read=} is not supported for encrypted cache.")


class EncryptedDiskcacheFunctionCache(FunctionCache):
    """An encrypted function cache implementation using diskcache.

    This class provides a secure way to cache function results, with both
    keys and values encrypted on disk.
    """

    def __init__(
        self,
        json_compression_level: int = 6,
    ) -> None:
        """Initialize the EncryptedDiskcacheFunctionCache.

        Args:
            json_compression_level: The compression level for JSON data (default: 6).
        """
        if json_compression_level > 9:
            _logger.warning(
                f"Cache compression level, {json_compression_level},"
                f" is higher than the maximum, 9. Setting to 9."
            )
            json_compression_level = 9
        if json_compression_level < 0:
            _logger.warning(
                f"Cache compression level, {json_compression_level},"
                f" is lower than the minimum, 0. Setting to 0."
            )
            json_compression_level = 0

        super().__init__()

        self._db = diskcache.Cache(
            # Explicitly create this in a temporary directory
            directory=None,
            disk=_EncryptedJSONDisk,
            disk_compress_level=json_compression_level,
            eviction_policy="none",
        )
        _logger.debug(f"Encrypted function cache created at {self._db.directory}")

        # Register cache deleter
        atexit.register(_remove_cache_dir, self._db.directory)

    @override
    def memoize(
        self,
        expire: Optional[float] = FUNCTION_CACHE_TTL,
        ignore: Container[int | str] = (),
    ) -> Callable[[Callable[_P, _T]], Memoized[_P, _T]]:
        return self._db.memoize(expire=expire, ignore=ignore)

    @override
    def clear(self) -> None:
        self._db.clear()

    def __del__(self) -> None:
        """Clean up resources when the cache is deleted."""
        self._db.close()
        _remove_cache_dir(self._db.directory)


def _remove_cache_dir(cache_dir: str) -> None:
    """Remove the cache directory.

    This function is called when cleaning up the EncryptedDiskcacheFunctionCache.

    Args:
        cache_dir: The directory of the cache to be removed.
    """
    try:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
    except Exception as e:
        # If this method is called via EncryptedDiskcacheFunctionCache's __del__
        # method at interpreter shutdown, it might be that _logger has already been
        # closed/deleted so have fallback to print to stderr.
        #
        # See: https://docs.python.org/3/reference/datamodel.html#object.__del__
        err_msg = (
            f"Encountered issue when trying to remove encrypted cache"
            f" at {cache_dir}: {e}"
        )
        try:
            _logger.warning(err_msg)
        except Exception:
            import sys

            print(f"WARNING: {err_msg}", file=sys.stderr)
