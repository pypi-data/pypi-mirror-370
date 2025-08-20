"""Constants, types, objects and functions used within this sub-package."""

from __future__ import annotations

from collections.abc import Callable

from attrs import frozen

from .. import VERSION, ArrayDouble  # noqa: TID252

__version__ = VERSION


@frozen
class GuidelinesBoundaryCallable:
    """A function to generate Guidelines boundary points, along with area and knot."""

    boundary_function: Callable[[ArrayDouble], ArrayDouble]
    area: float
    s_naught: float = 0
