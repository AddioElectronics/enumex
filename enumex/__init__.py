import sys

__version__ = "3.13.0"

if sys.version_info[:2] != (3, 13):
    raise RuntimeError(
        f"This version of enumex is exclusive to Python 3.13, "
        f"and you are using {sys.version_info.major}.{sys.version_info.minor}"
    )

from .enumex import(
    EnumExType, EnumExMeta,
    EnumEx, IntEnumEx, StrEnumEx, FlagEx, IntFlagEx, ReprEnumEx,
)


__all__ = [
        'EnumExType', 'EnumExMeta',
        'EnumEx', 'IntEnumEx', 'StrEnumEx', 'FlagEx', 'IntFlagEx', 'ReprEnumEx',
        ]
