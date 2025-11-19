import sys

__version__ = "3.9.0"

if sys.version_info[:2] != (3, 9):
    raise RuntimeError(
        f"This version of enumex is exclusive to Python 3.9.x, "
        f"and you are using {sys.version_info.major}.{sys.version_info.minor}"
    )

from .enumex import(
    EnumExMeta,
    EnumEx, IntEnumEx, FlagEx, IntFlagEx,
)


__all__ = [
        'EnumExMeta',
        'EnumEx', 'IntEnumEx', 'FlagEx', 'IntFlagEx',
        ]
