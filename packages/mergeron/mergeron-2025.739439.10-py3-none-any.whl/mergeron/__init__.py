"""Variables, types, objects and functions used throughout the package."""

from __future__ import annotations

import enum
from collections.abc import Mapping
from multiprocessing import cpu_count
from pathlib import Path
from typing import Any, Literal

import attrs
import numpy as np
from numpy.typing import NDArray
from ruamel import yaml

_PKG_NAME: str = Path(__file__).parent.name

VERSION = "2025.739439.10"

__version__ = VERSION

WORK_DIR = globals().get("WORK_DIR", Path.home() / _PKG_NAME)
"""
If defined, the global variable WORK_DIR is used as a data store.

If the user does not define WORK_DIR, a subdirectory in
the user's home directory, named for this package, is
created/reused.
"""
if not WORK_DIR.is_dir():
    WORK_DIR.mkdir(parents=False)

DEFAULT_REC_RATIO = 0.85

EMPTY_ARRAYDOUBLE = np.array([], float)
EMPTY_ARRAYINT = np.array([], int)

NTHREADS = 2 * cpu_count()

PKG_ATTRS_MAP: dict[str, type] = {}

np.set_printoptions(precision=28, floatmode="fixed", legacy=False)

type HMGPubYear = Literal[1992, 2010, 2023]

type ArrayBoolean = NDArray[np.bool_]
type ArrayFloat = NDArray[np.floating]
type ArrayINT = NDArray[np.integer]

type ArrayDouble = NDArray[np.float64]
type ArrayBIGINT = NDArray[np.int64]


def allclose(
    _a: ArrayFloat | ArrayINT | float | int,
    _b: ArrayFloat | ArrayINT | float | int,
    /,
    *,
    rtol: float = 1e-14,
    atol: float = 1e-15,
    equal_nan: bool = True,
) -> bool:
    """Redefine native numpy function with updated default tolerances."""
    return np.allclose(_a, _b, atol=atol, rtol=rtol, equal_nan=equal_nan)


def assert_allclose(  # noqa: PLR0913
    _a: ArrayFloat | ArrayINT | float | int,
    _b: ArrayFloat | ArrayINT | float | int,
    /,
    *,
    rtol: float = 1e-14,
    atol: float = 1e-15,
    equal_nan: bool = True,
    err_msg: str = "",
    verbose: bool = False,
    strict: bool = True,
) -> None:
    """Redefine native numpy function with updated default tolerances, type-enforcing."""
    return np.testing.assert_allclose(
        _a,
        _b,
        atol=1e-15,
        rtol=1e-14,
        equal_nan=equal_nan,
        err_msg=err_msg,
        verbose=verbose,
        strict=True,
    )


this_yaml = yaml.YAML(typ="rt")
this_yaml.indent(mapping=2, sequence=4, offset=2)

# Add yaml representer, constructor for NoneType
(_, _) = (
    this_yaml.representer.add_representer(
        type(None), lambda _r, _d: _r.represent_scalar("!None", "none")
    ),
    this_yaml.constructor.add_constructor("!None", lambda _c, _n, /: None),
)


# Add yaml representer, constructor for ndarray
(_, _) = (
    this_yaml.representer.add_representer(
        np.ndarray,
        lambda _r, _d: _r.represent_sequence("!ndarray", (_d.tolist(), _d.dtype.str)),
    ),
    this_yaml.constructor.add_constructor(
        "!ndarray", lambda _c, _n, /: np.array(*_c.construct_sequence(_n, deep=True))
    ),
)


def yaml_rt_mapper(
    _c: yaml.constructor.RoundTripConstructor, _n: yaml.MappingNode
) -> Mapping[str, Any]:
    """Construct mapping from a mapping node with the RoundTripConstructor."""
    data_: Mapping[str, Any] = yaml.constructor.CommentedMap()
    _c.construct_mapping(_n, maptyp=data_, deep=True)
    return data_


def yamelize_attrs(_typ: type, /, *, attr_map: dict[str, type] = PKG_ATTRS_MAP) -> None:
    """Add yaml representer, constructor for attrs-defined class.

    Attributes with property, `init=False` are not serialized/deserialized
    to YAML by the functions defined here. These attributes can, of course,
    be dumped to stand-alone (YAML) representation, and deserialized from there.
    """
    if not attrs.has(_typ):
        raise ValueError(f"Object {_typ} is not attrs-defined")

    attr_map |= {_typ.__name__: _typ}

    _ = this_yaml.representer.add_representer(
        _typ,
        lambda _r, _d: _r.represent_mapping(
            f"!{_d.__class__.__name__}",
            {_a.name: getattr(_d, _a.name) for _a in _d.__attrs_attrs__ if _a.init},
        ),
    )
    _ = this_yaml.constructor.add_constructor(
        f"!{_typ.__name__}",
        lambda _c, _n: attr_map[_n.tag.lstrip("!")](**yaml_rt_mapper(_c, _n)),
    )


@this_yaml.register_class
class Enameled(enum.Enum):
    """Add YAML representer, constructor for enum.Enum."""

    @classmethod
    def to_yaml(
        cls, _r: yaml.representer.RoundTripRepresenter, _d: enum.Enum
    ) -> yaml.ScalarNode:
        """Serialize enumerations by .name, not .value."""
        return _r.represent_scalar(
            f"!{super().__getattribute__(cls, '__name__')}", f"{_d.name}"
        )

    @classmethod
    def from_yaml(
        cls, _c: yaml.constructor.RoundTripConstructor, _n: yaml.ScalarNode
    ) -> enum.EnumType:
        """Deserialize enumeration."""
        retval: enum.EnumType = super().__getattribute__(cls, _n.value)
        return retval


@this_yaml.register_class
@enum.unique
class RECForm(str, Enameled):
    R"""For derivation of recapture ratio from market shares.

    With :math:`\mathscr{N}` a set of firms, each supplying a
    single differentiated product, and :math:`\mathscr{M} \subset \mathscr{N}`
    a putative relevant product market, with
    :math:`d_{ij}` denoting diversion ratio from good :math:`i` to good :math:`j`,
    :math:`s_i` denoting market shares, and
    :math:`\overline{r}` the default market recapture ratio,
    market recapture ratios for the respective products may be specified
    as having one of the following forms:
    """

    FIXED = "proportional"
    R"""Given, :math:`\overline{r}`,

    .. math::

        REC_i = \overline{r} {\ } \forall {\ } i \in \mathscr{M}

    """

    INOUT = "inside-out"
    R"""
    Given, :math:`\overline{r}, s_i {\ } \forall {\ } i \in \mathscr{M}`, with
    :math:`s_{min} = \min(s_1, s_2)`,

    .. math::

        REC_i = \frac{\overline{r} (1 - s_i)}{1 - (1 - \overline{r}) s_{min} - \overline{r} s_i}
        {\ } \forall {\ } i \in \mathscr{M}

    """

    OUTIN = "outside-in"
    R"""
    Given, :math:`d_{ij} {\ } \forall {\ } i, j \in \mathscr{M}, i \neq j`,

    .. math::

        REC_i = {\sum_{j \in \mathscr{M}}^{j \neq i} d_{ij}}
        {\ } \forall {\ } i \in \mathscr{M}

    """


@this_yaml.register_class
@enum.unique
class UPPAggrSelector(str, Enameled):
    """Aggregator for GUPPI and diversion ratio estimates."""

    AVG = "average"
    CPA = "cross-product-share weighted average"
    CPD = "cross-product-share weighted distance"
    CPG = "cross-product-share weighted geometric mean"
    DIS = "symmetrically-weighted distance"
    GMN = "geometric mean"
    MAX = "max"
    MIN = "min"
    OSA = "own-share weighted average"
    OSD = "own-share weighted distance"
    OSG = "own-share weighted geometric mean"
