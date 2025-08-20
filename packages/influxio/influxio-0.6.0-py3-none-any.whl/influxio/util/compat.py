import sys
import typing

if typing.TYPE_CHECKING:
    from importlib.metadata import EntryPoints


def entry_points(**params) -> "EntryPoints":
    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points
    return entry_points(**params)
