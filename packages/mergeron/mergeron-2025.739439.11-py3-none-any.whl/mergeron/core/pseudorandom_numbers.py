"""
Functions for generating synthetic data under specified distributions.

Uses multiple CPUs when available, with PCG64DXSM as the PRNG. [#]_

References
----------

.. [#] See,
    https://numpy.org/doc/stable/reference/random/generated/numpy.random.PCG64DXSM.html

"""

from __future__ import annotations

import concurrent.futures
from collections.abc import Sequence
from typing import Literal

import numpy as np
from attrs import Attribute, Converter, define, field
from numpy.random import Generator, SeedSequence

from .. import (  # noqa: TID252
    NTHREADS,
    VERSION,
    ArrayDouble,
    ArrayFloat,
    this_yaml,
    yaml_rt_mapper,
)
from . import DEFAULT_BITGENERATOR

__version__ = VERSION

DEFAULT_DIST_PARMS: ArrayFloat = np.array([0.0, 1.0], float)
DEFAULT_BETA_DIST_PARMS: ArrayFloat = np.array([1.0, 1.0], float)


def prng(_s: SeedSequence | None = None, /) -> np.random.Generator:
    """Return a psure-random number generator.

    Parameters
    ----------
    _s
        SeedSequence, for generating repeatable, non-overlapping random numbers.

    Returns
    -------
        A numpy random generator.

    """
    return Generator(
        DEFAULT_BITGENERATOR(SeedSequence(pool_size=8) if _s is None else _s)
    )


# Add yaml representer, constructor for SeedSequence
(_, _) = (
    this_yaml.representer.add_representer(
        SeedSequence, lambda _r, _d: _r.represent_mapping("!SeedSequence", _d.state)
    ),
    this_yaml.constructor.add_constructor(
        "!SeedSequence", lambda _c, _n, /: SeedSequence(**yaml_rt_mapper(_c, _n))
    ),
)


def gen_seed_seq_list_default(
    _len: int = 3, /, *, generated_entropy: Sequence[int] | None = None
) -> tuple[SeedSequence, ...]:
    R"""
    Return specified number of SeedSequences, for generating random variates.

    Initializes a specified number of SeedSequences based on a set of
    10 generated "seeds" in a hard-coded list. If the required number of
    random variates is larger than 10, the user must first generate
    a sufficient number of seeds to draw upon for initializing SeedSequences.
    The generated entropy can be reused in subsequent calls to this function.

    Parameters
    ----------
    _len
        Number of SeedSequences to initialize

    generated_entropy
        A list of integers with length not less than _s, to be used as seeds
        for initializing SeedSequences. A list of 10 appropriately generated
        integers is used as default.

    Returns
    -------
        A list of numpy SeedSequence objects, which can be used to seed prng() or to spawn
        seed sequences that can be used as seeds to generate non-overlapping streams in parallel. [#]_

    Raises
    ------
    ValueError
        When, :math:`\_sseq\_list\_len > max(10, len(generated\_entropy))`.

    References
    ----------
    .. [#] *See*, https://numpy.org/doc/stable/reference/random/parallel.html

    """
    generated_entropy = generated_entropy or [
        92156365243929466422624541055805800714117298857186959727264899187749727119124,
        45508962760932900824607908382088764294813063250106926349700153055300051503944,
        11358852481965974965852447884047438302274082458147659701772223782670581495409,
        98335771128074178116267837103565107347248838466705856121954317889296202882090,
        99169860978478959086120522268530894898455162069966492625932871292847103049882,
        87208206842095975410011581094164970201731602958127872604742955058753939512957,
        3615645999448046437740316672917313005913548649308233620056831197005377987468,
        108909094416963715978441140822183411647298834317413586830609215654532919223699,
        88096344099146385192471976829122012867254940684757663128881853302534662995332,
        63206306147411023146090085885772240748399174641427012462446714431253444120718,
    ]

    if _len > (_lge := len(generated_entropy)):
        e_str_segs = (
            "This function can presently create SeedSequences for generating up to ",
            f"{_lge:,d} independent random variates. If you really need to generate ",
            f"more than {_lge:,d} seeded independent random variates, please pass a ",
            "sufficiently large list of seeds as generated_entropy. See,",
            "{}/{}.".format(
                "https://numpy.org/doc/stable/reference/random",
                "bit_generators/generated/numpy.random.SeedSequence.html",
            ),
        )
        raise ValueError("".join(e_str_segs))

    return tuple(SeedSequence(_s, pool_size=8) for _s in generated_entropy[:_len])


def _dist_parms_conv(_v: ArrayFloat | None, _i: MultithreadedRNG) -> ArrayFloat:
    if _v is None or not len(_v):
        return {
            "Beta": DEFAULT_BETA_DIST_PARMS,
            "Dirichlet": np.ones(_i.values.shape[-1], float),
            "Normal": DEFAULT_DIST_PARMS,
            "Uniform": DEFAULT_DIST_PARMS,
        }.get(_i.dist_type, DEFAULT_DIST_PARMS)
    elif isinstance(_v, Sequence | np.ndarray):
        return np.asarray(_v, float)
    else:
        raise ValueError(
            f"Input, {_v!r} has invalid type. Must be None, Sequence of floats, or Numpy ndarray."
        )


@define
class MultithreadedRNG:
    """Fill given array on demand with pseudo-random numbers as specified.

    Random number generation is multithreaded, using twice
    the number of threads as available CPU cores by default.
    If a seed sequence is provided, it is used in a thread-safe way
    to generate repeatable i.i.d. draws. All arguments are validated
    before commencing multithreaded random number generation.
    """

    values: ArrayDouble = field(kw_only=False)
    """Output array to which generated data are over-written

    Array-length defines the number of i.i.d. (vector) draws.
    """

    @values.validator
    def _vsv(
        _i: MultithreadedRNG, _a: Attribute[ArrayDouble], _v: ArrayDouble, /
    ) -> None:
        if not len(_v):
            raise ValueError("Output array must at least be one dimension")

    dist_type: Literal[
        "Beta", "Dirichlet", "Gaussian", "Normal", "Random", "Uniform"
    ] = field(default="Uniform")
    """Distribution for the generated random numbers.

    Default is "Uniform".
     """

    @dist_type.validator
    def _dtv(_i: MultithreadedRNG, _a: Attribute[str], _v: str, /) -> None:
        if _v not in (
            _rdts := ("Beta", "Dirichlet", "Gaussian", "Normal", "Random", "Uniform")
        ):
            raise ValueError(f"Specified distribution must be one of {_rdts}")

    dist_parms: ArrayFloat = field(
        converter=Converter(_dist_parms_conv, takes_self=True)  # type: ignore
    )
    """Parameters, if any, for tailoring random number generation
    """

    @dist_parms.default
    def _dpd(_i: MultithreadedRNG) -> ArrayFloat:
        return _dist_parms_conv(None, _i)

    @dist_parms.validator
    def _dpv(
        _i: MultithreadedRNG, _a: Attribute[ArrayFloat], _v: ArrayFloat, /
    ) -> None:
        if (_i.dist_type != "Dirichlet" and (_lrdp := len(_v)) != (_trdp := 2)) or (
            _i.dist_type == "Dirichlet"
            and (_lrdp := len(_v)) != (_trdp := _i.values.shape[-1])
        ):
            raise ValueError(f"Expected {_trdp} parameters, got, {_lrdp}")

        elif _i.dist_type in {"Beta", "Dirichlet"} and (_v <= 0.0).any():
            raise ValueError("Shape and location parameters must be strictly positive")

    seed_sequence: SeedSequence | None = field(default=None)
    """Seed sequence for generating random numbers."""

    nthreads: int = field(default=NTHREADS)
    """Number of threads to spawn for random number generation."""

    def fill(self) -> None:
        """Fill the provided output array with random number draws as specified."""
        if not len(self.dist_parms) or np.array_equal(
            self.dist_parms, DEFAULT_DIST_PARMS
        ):
            if self.dist_type == "Uniform":
                dist_type = "Random"
            elif self.dist_type == "Normal":
                dist_type = "Gaussian"
        else:
            dist_type = self.dist_type

        step_size = (len(self.values) / self.nthreads).__ceil__()

        seed_ = (
            SeedSequence(pool_size=8)
            if self.seed_sequence is None
            else self.seed_sequence
        )

        random_generators = tuple(prng(_t) for _t in seed_.spawn(self.nthreads))

        def _fill(
            _rng: np.random.Generator,
            _dist_type: str,
            _dist_parms: ArrayFloat,
            out_: ArrayDouble,
            _first: int,
            _last: int,
            /,
        ) -> None:
            _sz: tuple[int, ...] = out_[_first:_last].shape
            match _dist_type:
                case "Beta":
                    shape_a, shape_b = _dist_parms
                    out_[_first:_last] = _rng.beta(shape_a, shape_b, size=_sz)
                case "Dirichlet":
                    out_[_first:_last] = _rng.dirichlet(_dist_parms, size=_sz[:-1])
                case "Gaussian":
                    _rng.standard_normal(out=out_[_first:_last])
                case "Normal":
                    _mu, _sigma = _dist_parms
                    out_[_first:_last] = _rng.normal(_mu, _sigma, size=_sz)
                case "Random":
                    _rng.random(out=out_[_first:_last])
                case "Uniform":
                    uni_l, uni_h = _dist_parms
                    out_[_first:_last] = _rng.uniform(uni_l, uni_h, size=_sz)
                case _:
                    "Unreachable. The validator would have rejected this as invalid."

        with concurrent.futures.ThreadPoolExecutor(self.nthreads) as executor_:
            for _i in range(self.nthreads):
                range_first = _i * step_size
                range_last = min(len(self.values), (_i + 1) * step_size)

                executor_.submit(
                    _fill,
                    random_generators[_i],
                    dist_type,
                    self.dist_parms,
                    self.values,
                    range_first,
                    range_last,
                )
