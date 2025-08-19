import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Literal,
    TypeVar,
)

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if TYPE_CHECKING:
    import numpy as np
    import numpy as array_api
    from numpy import dtype, long, ulong
    from numpy.polynomial._polybase import ABCPolyBase
    from typing_extensions import Never

    StringDType: TypeAlias = dtype[Never]


__version__: Final[Literal["20250818.2.0"]] = "20250818.2.0"

__all__ = (
    "NUMPY_GE_1_22",
    "NUMPY_GE_1_23",
    "NUMPY_GE_1_25",
    "NUMPY_GE_2_0",
    "NUMPY_GE_2_1",
    "NUMPY_GE_2_2",
    "NUMPY_GE_2_3",
    "ABCPolyBase",
    "CanArray",
    "LiteralFalse",
    "LiteralTrue",
    "StringDType",
    "array_api",
    "long",
    "ulong",
    "_check_version",
    "__version__",
)


def __dir__() -> tuple[str, ...]:
    return __all__


__ALL_SET = frozenset(__all__)


def __getattr__(name: str, /) -> object:
    if name == "CanArray":
        from numpy import ndarray

        return ndarray

    if name == "StringDType":
        from numpy.dtypes import StringDType

        return StringDType

    if name == "array_api":
        import numpy as array_api

        return array_api

    if name == "long":
        from numpy import long

        return long

    if name == "ulong":
        from numpy import ulong

        return ulong

    if name == "ABCPolyBase":
        from numpy.polynomial._polybase import ABCPolyBase

        return ABCPolyBase

    if name in __ALL_SET and name in globals():
        return globals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


NUMPY_GE_1_22: Final[Literal[True]] = True
NUMPY_GE_1_23: Final[Literal[True]] = True
NUMPY_GE_1_25: Final[Literal[True]] = True
NUMPY_GE_2_0: Final[Literal[True]] = True
NUMPY_GE_2_1: Final[Literal[False]] = False
NUMPY_GE_2_2: Final[Literal[False]] = False
NUMPY_GE_2_3: Final[Literal[False]] = False


LiteralTrue: TypeAlias = Literal[True]
LiteralFalse: TypeAlias = Literal[False]


if TYPE_CHECKING:
    ShapeT = TypeVar("ShapeT", bound=tuple[int, ...])
    DTypeT = TypeVar("DTypeT", bound=np.dtype[Any])

    CanArray: TypeAlias = np.ndarray[ShapeT, DTypeT]


def _check_version() -> bool:
    """Check if the `numpy-typing-compat` version is compatible with `numpy`."""
    import numpy as np

    np_version = tuple(map(int, np.__version__.split(".", 2)[:2]))
    return (2, 0) <= np_version < (2, 1)
