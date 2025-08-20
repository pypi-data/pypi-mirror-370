"""Constants, types, objects and functions used within this sub-package."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Any

import mpmath  # type: ignore
import numpy as np
from attrs import cmp_using, field, frozen
from numpy.random import PCG64DXSM

from .. import (  # noqa: TID252
    VERSION,
    ArrayBIGINT,
    ArrayDouble,
    this_yaml,
    yamelize_attrs,
    yaml_rt_mapper,
)

__version__ = VERSION

DEFAULT_BITGENERATOR = PCG64DXSM

type MPFloat = mpmath.ctx_mp_python.mpf
type MPMatrix = mpmath.matrices.matrices._matrix


@frozen
class GuidelinesBoundary:
    """Represents Guidelines boundary analytically."""

    coordinates: ArrayDouble
    """Market-share pairs as Cartesian coordinates of points on the boundary."""

    area: float
    """Area under the boundary."""


@frozen
class INVTableData:
    """Represents individual table of FTC merger investigations data."""

    industry_group: str
    additional_evidence: str
    data_array: ArrayBIGINT = field(eq=cmp_using(eq=np.array_equal))


type INVData = MappingProxyType[
    str, MappingProxyType[str, MappingProxyType[str, INVTableData]]
]
type INVData_in = dict[str, dict[str, dict[str, INVTableData]]]

yamelize_attrs(INVTableData)

(_, _) = (
    this_yaml.representer.add_representer(
        Decimal, lambda _r, _d: _r.represent_scalar("!Decimal", f"{_d}")
    ),
    this_yaml.constructor.add_constructor(
        "!Decimal", lambda _c, _n, /: Decimal(_c.construct_scalar(_n))
    ),
)


(_, _) = (
    this_yaml.representer.add_representer(
        mpmath.mpf, lambda _r, _d: _r.represent_scalar("!MPFloat", f"{_d}")
    ),
    this_yaml.constructor.add_constructor(
        "!MPFloat", lambda _c, _n, /: mpmath.mpf(_c.construct_scalar(_n))
    ),
)

(_, _) = (
    this_yaml.representer.add_representer(
        mpmath.matrix, lambda _r, _d: _r.represent_sequence("!MPMatrix", _d.tolist())
    ),
    this_yaml.constructor.add_constructor(
        "!MPMatrix",
        lambda _c, _n, /: mpmath.matrix(_c.construct_sequence(_n, deep=True)),
    ),
)

_, _ = (
    this_yaml.representer.add_representer(
        MappingProxyType,
        lambda _r, _d: _r.represent_mapping("!mappingproxy", dict(_d.items())),
    ),
    this_yaml.constructor.add_constructor(
        "!mappingproxy", lambda _c, _n: MappingProxyType(dict(**yaml_rt_mapper(_c, _n)))
    ),
)


def _dict_from_mapping(_p: Mapping[Any, Any], /) -> dict[Any, Any]:
    retval: dict[Any, Any] = {}
    for _k, _v in _p.items():
        retval |= {_k: _dict_from_mapping(_v)} if isinstance(_v, Mapping) else {_k: _v}
    return retval


def _mappingproxy_from_mapping(_p: Mapping[Any, Any], /) -> MappingProxyType[Any, Any]:
    retval: dict[Any, Any] = {}
    for _k, _v in _p.items():
        retval |= (
            {_k: _mappingproxy_from_mapping(_v)}
            if isinstance(_v, Mapping)
            else {_k: _v}
        )
    return MappingProxyType(retval)
