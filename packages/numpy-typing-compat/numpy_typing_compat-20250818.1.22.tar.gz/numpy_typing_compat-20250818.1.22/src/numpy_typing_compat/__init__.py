import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Literal,
    Tuple,
    TypeVar,
)

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if TYPE_CHECKING:
    import numpy as np
    from typing_extensions import Never

    from numpy.polynomial._polybase import ABCPolyBase
    from numpy import int_ as long
    from numpy import uint as ulong

    array_api: TypeAlias = Never
    StringDType: TypeAlias = Never


__version__: Final[Literal["20250818.1.22"]] = "20250818.1.22"

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


def __dir__() -> Tuple[str, ...]:
    return __all__


__ALL_SET = frozenset(__all__)


def __getattr__(name: str, /) -> object:
    if name == "CanArray":
        from numpy import ndarray

        return ndarray

    if name == "long":
        from numpy import int_ as long

        return long

    if name == "ulong":
        from numpy import uint as ulong

        return ulong

    if name == "ABCPolyBase":
        from numpy.polynomial._polybase import ABCPolyBase

        return ABCPolyBase

    if name in __ALL_SET and name in globals():
        return globals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


NUMPY_GE_1_22: Final[Literal[True]] = True
NUMPY_GE_1_23: Final[Literal[False]] = False
NUMPY_GE_1_25: Final[Literal[False]] = False
NUMPY_GE_2_0: Final[Literal[False]] = False
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
    return (1, 22) <= np_version < (1, 23)
