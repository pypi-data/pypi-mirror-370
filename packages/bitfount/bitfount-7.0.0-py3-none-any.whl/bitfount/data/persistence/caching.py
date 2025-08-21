"""Contains classes designed for easy caching/persistence.

:::warning

This import location is deprecated and will be removed in a future version.

Please use the `bitfount.persistence.caching` module instead.

:::

These classes are designed to be used in cases where you would normally use a `dict`
but want to have the ability to persist between restarts/runs or do not/cannot store
the entire dict in memory.
"""

from bitfount.persistence.caching import *  # noqa: F401, F403
