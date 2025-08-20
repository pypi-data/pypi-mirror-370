"""Defines constants, specifications and containers for industry data generation and testing."""

from __future__ import annotations

import enum
import io
import zipfile
from collections.abc import Sequence
from operator import attrgetter
from typing import IO

import h5py  # type: ignore
import numpy as np
from attrs import Attribute, Converter, cmp_using, field, frozen
from numpy.random import SeedSequence

from .. import (  # noqa: TID252
    DEFAULT_REC_RATIO,
    VERSION,
    ArrayBIGINT,
    ArrayBoolean,
    ArrayDouble,
    ArrayFloat,
    ArrayINT,
    Enameled,
    RECForm,
    UPPAggrSelector,
    allclose,
    this_yaml,
    yamelize_attrs,
)
from ..core.empirical_margin_distribution import margin_data_builder  # noqa: TID252
from ..core.pseudorandom_numbers import (  # noqa: TID252
    DEFAULT_BETA_DIST_PARMS,
    DEFAULT_DIST_PARMS,
)

__version__ = VERSION

DEFAULT_FCOUNT_WTS = np.asarray((_nr := np.arange(6, 0, -1)) / _nr.sum(), float)

DEFAULT_BETA_BND_DIST_PARMS = np.array([0.5, 1.0, 0.0, 1.0], float)


@frozen
class SeedSequenceData:
    """Seed sequence values for shares, margins, and, optionally, firm-counts and prices."""

    share: SeedSequence = field(eq=attrgetter("state"))
    pcm: SeedSequence = field(eq=attrgetter("state"))
    fcounts: SeedSequence | None = field(eq=lambda x: x if x is None else x.state)
    price: SeedSequence | None = field(eq=lambda x: x if x is None else x.state)


@this_yaml.register_class
@enum.unique
class PriceSpec(tuple[bool, str | None], Enameled):
    """Price specification.

    Whether prices are symmetric and, if not, the direction of correlation, if any.
    """

    SYM = (True, None)
    RNG = (False, None)
    NEG = (False, "negative share-correlation")
    POS = (False, "positive share-correlation")
    CSY = (False, "market-wide cost-symmetry")


@this_yaml.register_class
@enum.unique
class SHRDistribution(str, Enameled):
    """Market share distributions."""

    UNI = "Uniform"
    R"""Uniform distribution over :math:`s_1 + s_2 \leqslant 1`"""

    DIR_FLAT = "Flat Dirichlet"
    """Shape parameter for all merging-firm-shares is unity (1)"""

    DIR_FLAT_CONSTR = "Flat Dirichlet - Constrained"
    """Impose minimum probability weight on each firm-count

    Only firm-counts with probability weight of 3% or more
    are included for data generation.
    """

    DIR_ASYM = "Asymmetric Dirichlet"
    """Share distribution for merging-firm shares has a higher peak share

    By default, shape parameter for merging-firm-share is 2.5, and
    1.0 for all others. Defining, :attr:`.ShareSpec.dist_parms`
    as a vector of shape parameters with length matching
    that of :attr:`.ShareSpec.dist_parms` allows flexible specification
    of Dirichlet-distributed share-data generation.
    """

    DIR_COND = "Conditional Dirichlet"
    """Shape parameters for non-merging firms is proportional

    Shape parameters for merging-firm-share are 2.0 each; and
    are equiproportional and add to 2.0 for all non-merging-firm-shares.
    """


def _fc_wts_conv(
    _v: Sequence[float | int] | ArrayDouble | ArrayINT | None, _i: ShareSpec
) -> ArrayFloat | None:
    if _i.dist_type == SHRDistribution.UNI:
        return None
    elif _v is None or len(_v) == 0 or np.array_equal(_v, DEFAULT_FCOUNT_WTS):
        return DEFAULT_FCOUNT_WTS
    else:
        return _tv if (_tv := np.asarray(_v, float)).sum() == 1 else _tv / _tv.sum()


def _shr_dp_conv(_v: Sequence[float] | ArrayFloat | None, _i: ShareSpec) -> ArrayFloat:
    if _v is None or len(_v) == 0 or np.array_equal(_v, DEFAULT_DIST_PARMS):
        if _i.dist_type == SHRDistribution.UNI:
            return DEFAULT_DIST_PARMS
        else:
            fc_max = 1 + (
                len(DEFAULT_FCOUNT_WTS)
                if _i.firm_counts_weights is None
                else len(_i.firm_counts_weights)
            )

            match _i.dist_type:
                case SHRDistribution.DIR_FLAT | SHRDistribution.DIR_FLAT_CONSTR:
                    return np.ones(fc_max, float)
                case SHRDistribution.DIR_ASYM:
                    return np.array([2.0] * 6 + [1.5] * 5 + [1.25] * fc_max, float)
                case SHRDistribution.DIR_COND:
                    return np.array([], float)
                case _ if isinstance(_i.dist_type, SHRDistribution):
                    raise ValueError(
                        f"No default defined for market share distribution, {_i.dist_type!r}"
                    )
                case _:
                    raise ValueError(
                        f"Unsupported distribution for market share generation, {_i.dist_type!r}"
                    )
    elif isinstance(_v, Sequence | np.ndarray):
        return np.asarray(_v, float)
    else:
        raise ValueError(
            f"Input, {_v!r} has invalid type. Must be None, Sequence of floats, or Numpy ndarray."
        )


@frozen
class ShareSpec:
    """Market share specification.

    A salient feature of market-share specification in this package is that
    the draws represent markets with multiple different firm-counts.
    Firm-counts are unspecified if the share distribution is
    :attr:`.SHRDistribution.UNI`, for Dirichlet-distributed market-shares,
    the default specification is that firm-counts  vary between
    2 and 7 firms with each value equally likely.

    Notes
    -----
    If :attr:`.dist_type` == :attr:`.SHRDistribution.UNI`, it is then infeasible that
    :attr:`.recapture_form` == :attr:`mergeron.RECForm.OUTIN`.
    In other words, recapture ratios cannot be estimated using
    outside-good choice probabilities if the distribution of markets over firm-counts
    is unspecified.
    """

    dist_type: SHRDistribution = field(kw_only=False)
    """See :class:`SHRDistribution`"""

    firm_counts_weights: ArrayFloat | None = field(
        kw_only=True,
        eq=cmp_using(eq=np.array_equal),
        converter=Converter(_fc_wts_conv, takes_self=True),  # type: ignore
    )
    """Relative or absolute frequencies of pre-merger firm counts

    Defaults to :attr:`DEFAULT_FCOUNT_WTS`, which specifies pre-merger
    firm-counts of 2 to 7 with weights in descending order from 6 to 1.

    ALERT: Firm-count weights are irrelevant when the merging firms' shares are specified
    to have uniform distribution; therefore this attribute is forced to None if
    :attr:`.dist_type` == :attr:`.SHRDistribution.UNI`.
    """

    @firm_counts_weights.default
    def __fcwd(_i: ShareSpec) -> ArrayFloat | None:
        return _fc_wts_conv(None, _i)

    @firm_counts_weights.validator
    def __fcv(_i: ShareSpec, _a: Attribute[ArrayFloat], _v: ArrayFloat) -> None:
        if _i.dist_type != SHRDistribution.UNI and not len(_v):
            raise ValueError(
                f"Attribute, {'"firm_counts_weights"'} must be populated if the share distribution is "
                "other than uniform distribution."
            )

    dist_parms: ArrayFloat = field(
        kw_only=True,
        converter=Converter(_shr_dp_conv, takes_self=True),  # type: ignore
        eq=cmp_using(eq=np.array_equal),
    )
    """Parameters for tailoring market-share distribution

    For Uniform distribution, bounds of the distribution; defaults to `(0, 1)`;
    for Dirichlet-type distributions, a vector of shape parameters of length
    equal to 1 plus the length of firm-count weights below; defaults depend on
    type of Dirichlet-distribution specified.
    """

    @dist_parms.default
    def __dpd(_i: ShareSpec) -> ArrayFloat:
        # converters run after defaults, and we
        # avoid redundancy and confusion here
        return _shr_dp_conv(None, _i)

    @dist_parms.validator
    def __dpv(_i: ShareSpec, _a: Attribute[ArrayFloat], _v: ArrayFloat) -> None:
        if (
            _i.firm_counts_weights is not None
            and _v is not None
            and 0 < len(_v) < (1 + len(_i.firm_counts_weights))
        ):
            raise ValueError(
                "If specified, the number of distribution parameters must equal or "
                "exceed the maximum firm-count premerger, which is "
                "1 plus the length of the vector specifying firm-count weights."
            )

    recapture_form: RECForm = field(default=RECForm.INOUT)
    """See :class:`mergeron.RECForm`"""

    @recapture_form.validator
    def __rfv(_i: ShareSpec, _a: Attribute[RECForm], _v: RECForm) -> None:
        if _i.dist_type == SHRDistribution.UNI and _v == RECForm.OUTIN:
            raise ValueError(
                "Outside-good choice probabilities cannot be generated if the "
                "merging firms' market shares have uniform distribution over the "
                "3-dimensional simplex with the distribution of markets over "
                "firm-counts unspecified."
            )

    recapture_ratio: float | None = field(kw_only=True)
    """A value between 0 and 1.

    :code:`None` if market share specification requires direct generation of
    outside good choice probabilities (:attr:`mergeron.RECForm.OUTIN`).

    The recapture ratio is usually calibrated to the numbers-equivalent of the
    HHI threshold for the presumption of harm from unilateral competitive effects
    in published merger guidelines. Accordingly, the recapture ratio rounded to
    the nearest 5% is:

    * 0.85, **7-to-6 merger from symmetry**; US Guidelines, 1992, 2023
    * 0.80, 5-to-4 merger from symmetry
    * 0.80, **5-to-4 merger to symmetry**; US Guidelines, 2010

    Highlighting indicates hypothetical mergers in the neighborhood of (the boundary of)
    the Guidelines presumption of harm. (In the EU Guidelines, concentration measures serve as
    screens for further investigation, rather than as the basis for presumptions of harm or
    presumptions no harm.)

    ALERT: If diversion ratios are estimated by specifying a choice probability for the
    outside good, the recapture ratio is set to None, overriding any user-specified value.
    """

    @recapture_ratio.default
    def __rrd(_i: ShareSpec) -> float | None:
        return None if _i.recapture_form == RECForm.OUTIN else DEFAULT_REC_RATIO

    @recapture_ratio.validator
    def __rrv(_i: ShareSpec, _a: Attribute[float], _v: float) -> None:
        if _v and not (0 < _v <= 1):
            raise ValueError("Recapture ratio must lie in the interval, [0, 1).")
        elif _v is None and _i.recapture_form != RECForm.OUTIN:
            raise ValueError(
                f"Recapture specification, {_i.recapture_form!r} requires that "
                "the market sample specification includes a recapture ratio in the "
                "interval [0, 1)."
            )


@this_yaml.register_class
@enum.unique
class PCMDistribution(str, Enameled):
    """Margin distributions."""

    UNI = "Uniform"
    BETA = "Beta"
    BETA_BND = "Bounded Beta"
    EMPR = "Damodaran margin data, resampled"


@this_yaml.register_class
@enum.unique
class PCMRestriction(str, Enameled):
    """Restriction on generated Firm 2 margins."""

    IID = "independent and identically distributed (IID)"
    MNL = "Nash-Bertrand equilibrium with multinomial logit (MNL) demand"
    SYM = "symmetric"


def _pcm_dp_conv(_v: ArrayFloat | Sequence[float] | None, _i: PCMSpec) -> ArrayFloat:
    if _v is None or len(_v) == 0 or np.array_equal(_v, DEFAULT_DIST_PARMS):
        if _i.dist_type == PCMDistribution.EMPR:
            return margin_data_builder()[0]
        match _i.dist_type:
            case PCMDistribution.BETA:
                return DEFAULT_BETA_DIST_PARMS
            case PCMDistribution.BETA_BND:
                return DEFAULT_BETA_BND_DIST_PARMS
            case _:
                return DEFAULT_DIST_PARMS
    elif _i.dist_type == PCMDistribution.EMPR and not isinstance(_v, np.ndarray):
        raise ValueError(
            "Invalid specification; use ..core.empirical_margin_distribution.margin_data_builder()[0]."
        )
    elif isinstance(_v, Sequence | np.ndarray):
        return np.asarray(_v, float)
    else:
        raise ValueError(
            f"Input, {_v!r} has invalid type. Must be None, sequence of floats,"
            "sequence of Numpy arrays, or Numpy ndarray."
        )


@frozen
class PCMSpec:
    """Price-cost margin (PCM) specification.

    If price-cost margins are specified as having Beta distribution,
    `dist_parms` is specified as a pair of positive, non-zero shape parameters of
    the standard Beta distribution. Specifying shape parameters :code:`np.array([1, 1])`
    is known equivalent to specifying uniform distribution over
    the interval :math:`[0, 1]`. If price-cost margins are specified as having
    Bounded-Beta distribution, `dist_parms` is specified as
    the tuple, (`mean`, `std deviation`, `min`, `max`), where `min` and `max`
    are lower- and upper-bounds respectively within the interval :math:`[0, 1]`.
    """

    dist_type: PCMDistribution = field()
    """See :class:`PCMDistribution`"""

    @dist_type.default
    def __dtd(_i: PCMSpec) -> PCMDistribution:
        return PCMDistribution.UNI

    dist_parms: ArrayFloat = field(
        kw_only=True,
        eq=cmp_using(eq=allclose),
        converter=Converter(_pcm_dp_conv, takes_self=True),  # type: ignore
    )
    """Parameter specification for tailoring PCM distribution

    For Uniform distribution, bounds of the distribution; defaults to `(0, 1)`;
    for Beta distribution, shape parameters, defaults to `(1, 1)`;
    for Bounded-Beta distribution, vector of (min, max, mean, std. deviation), non-optional;
    for empirical distribution based on Damodaran margin data, optional, ignored
    """

    @dist_parms.default
    def __dpwd(_i: PCMSpec) -> ArrayFloat:
        return _pcm_dp_conv(None, _i)

    @dist_parms.validator
    def __dpv(
        _i: PCMSpec,
        _a: Attribute[ArrayFloat | Sequence[ArrayDouble] | None],
        _v: ArrayFloat | Sequence[ArrayDouble] | None,
    ) -> None:
        if _i.dist_type.name.startswith("BETA"):
            if (
                _v is None
                or not hasattr(_v, "len")
                or (isinstance(_v, np.ndarray) and not any(_v.shape))
            ):
                pass
            elif np.array_equal(_v, DEFAULT_DIST_PARMS):
                raise ValueError(
                    f"The distribution parameters, {DEFAULT_DIST_PARMS!r} "
                    "are not valid with margin distribution, {_dist_type_pcm!r}"
                )
            elif (
                _i.dist_type == PCMDistribution.BETA and len(_v) != len(("a", "b"))
            ) or (
                _i.dist_type == PCMDistribution.BETA_BND
                and len(_v) != len(("mu", "sigma", "max", "min"))
            ):
                raise ValueError(
                    f"Given number, {len(_v)} of parameters "
                    f'for PCM with distribution, "{_i.dist_type}" is incorrect.'
                )

        elif _i.dist_type == PCMDistribution.EMPR and not isinstance(_v, np.ndarray):
            raise ValueError(
                "Empirical distribution requires deserialized margin data from Prof. Damodaran, NYU"
            )

    pcm_restriction: PCMRestriction = field(kw_only=True, default=PCMRestriction.IID)
    """See :class:`PCMRestriction`"""

    @pcm_restriction.validator
    def __prv(_i: PCMSpec, _a: Attribute[PCMRestriction], _v: PCMRestriction) -> None:
        if _v == PCMRestriction.MNL and _i.dist_type == PCMDistribution.EMPR:
            print(
                "NOTE: For consistency of generated Firm 2 margins with source data,",
                "respecify PCMSpec with pcm_restriction=PCMRestriction.IID.",
                sep="\n",
            )


@this_yaml.register_class
@enum.unique
class SSZConstant(float, Enameled):
    """
    Scale factors to offset sample size reduction.

    Sample size reduction occurs when imposing a HSR filing test
    or equilibrium condition under MNL demand.
    """

    HSR_NTH = 1.666667
    """
    For HSR filing requirement.

    When filing requirement is assumed met if maximum merging-firm shares exceeds
    ten (10) times the n-th firm's share and minimum merging-firm share is
    no less than n-th firm's share. To assure that the number of draws available
    after applying the given restriction, the initial number of draws is larger than
    the sample size by the given scale factor.
    """

    HSR_TEN = 1.234567
    """
    For alternative HSR filing requirement,

    When filing requirement is assumed met if merging-firm shares exceed 10:1 ratio
    to each other.
    """

    MNL_DEP = 1.25
    """
    For restricted PCM's.

    When merging firm's PCMs are constrained for consistency with f.o.c.s from
    profit maximization under Nash-Bertrand oligopoly with MNL demand.
    """

    ONE = 1.00
    """When initial set of draws is not restricted in any way."""


@frozen
class MarketSampleData:
    """Container for generated market sample dataset."""

    frmshr_array: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Merging-firm shares (with two merging firms)"""

    pcm_array: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Merging-firms' prices (normalized to 1, in default specification)"""

    price_array: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Merging-firms' price-cost margins (PCM)"""

    divr_array: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Diversion ratio between the merging firms"""

    hhi_delta: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Change in HHI from combination of merging firms"""

    aggregate_purchase_prob: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """
    One (1) minus probability that the outside good is chosen

    Converts market shares to choice probabilities by multiplication.
    """

    @aggregate_purchase_prob.default
    def __appd(_i: MarketSampleData) -> ArrayDouble:
        retval: ArrayDouble = np.empty_like(_i.frmshr_array[:, :1], float)
        retval.fill(np.nan)
        return retval

    fcounts: ArrayINT = field(eq=cmp_using(np.array_equal))
    """Number of firms in market"""

    @fcounts.default
    def __fcd(_i: MarketSampleData) -> ArrayINT:
        return np.zeros_like(_i.frmshr_array[:, :1], np.uint8)

    nth_firm_share: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Market-share of n-th firm

    Relevant for testing draws that do or
    do not meet HSR filing thresholds.
    """

    @nth_firm_share.default
    def __nfsd(_i: MarketSampleData) -> ArrayDouble:
        retval: ArrayDouble = np.empty_like(_i.frmshr_array[:, :1], float)
        retval.fill(np.nan)
        return retval

    hhi_post: ArrayDouble = field(eq=cmp_using(np.array_equal))
    """Post-merger contribution to Herfindahl-Hirschman Index (HHI)"""

    @hhi_post.default
    def __hpd(_i: MarketSampleData) -> ArrayDouble:
        retval: ArrayDouble = np.empty_like(_i.frmshr_array[:, :1], float)
        retval.fill(np.nan)
        return retval

    def to_h5bin(self) -> bytes:
        """Save market sample data to HDF5 file."""
        byte_stream = io.BytesIO()
        with h5py.File(byte_stream, "w") as _h5f:
            for _a in self.__attrs_attrs__:
                if all((
                    (_arr := getattr(self, _a.name)).any(),
                    not np.isnan(_arr).all(),
                )):
                    _h5f.create_dataset(_a.name, data=_arr, fletcher32=True)
        return byte_stream.getvalue()

    @classmethod
    def from_h5f(
        cls, _hfh: io.BufferedReader | zipfile.ZipExtFile | IO[bytes]
    ) -> MarketSampleData:
        """Load market sample data from HDF5 file."""
        with h5py.File(_hfh, "r") as _h5f:
            _retval = cls(**{_a: _h5f[_a][:] for _a in _h5f})
        return _retval


@frozen
class ShareSampleData:
    """Container for generated market shares.

    Includes related measures of market structure
    and aggregate purchase probability.
    """

    mktshr_array: ArrayDouble
    """All-firm shares (with two merging firms)"""

    fcounts: ArrayINT
    """All-firm-count for each draw"""

    nth_firm_share: ArrayDouble
    """Market-share of n-th firm"""

    aggregate_purchase_prob: ArrayDouble
    """Converts market shares to choice probabilities by multiplication."""


@frozen
class PriceSampleData:
    """Container for generated price array, and related."""

    price_array: ArrayDouble
    """Merging-firms' prices"""

    hsr_filing_test: ArrayBoolean
    """Flags draws as meeting HSR filing thresholds or not"""


@frozen
class MarginSampleData:
    """Container for generated margin array and related MNL test array."""

    pcm_array: ArrayDouble
    """Merging-firms' PCMs"""

    mnl_test_array: ArrayBoolean
    """Flags infeasible observations as False and rest as True

    Applying restrictions from Bertrand-Nash oligopoly with MNL demand results
    in some draws of Firm 2 PCM falling outside the feasible interval, :math:`[0, 1]`
    for certain combinations of merging firms shares as initially drawn. Such draws
    are flagged as infeasible (False) in :code:`mnl_test_array` while draws with
    feaseible PCM values flagged True. This array is used to exclude infeasible draws
    when imposing MNL demand in simulations.
    """


@this_yaml.register_class
@enum.unique
class INVResolution(str, Enameled):
    """Report investigations resulting in clearance; enforcement; or both, respectively."""

    CLRN = "clearance"
    ENFT = "enforcement"
    BOTH = "clearance and enforcement, respectively"


@frozen
class UPPTestRegime:
    """Configuration for UPP tests."""

    resolution: INVResolution = field(kw_only=False, default=INVResolution.ENFT)
    """Whether to test clearance, enforcement."""

    @resolution.validator
    def _resvdtr(
        _i: UPPTestRegime, _a: Attribute[INVResolution], _v: INVResolution
    ) -> None:
        if _v == INVResolution.BOTH:
            raise ValueError(
                "GUPPI test cannot be performed with both resolutions; only useful for reporting"
            )
        elif _v not in {INVResolution.CLRN, INVResolution.ENFT}:
            raise ValueError(
                f"Must be one of, {INVResolution.CLRN!r} or {INVResolution.ENFT!r}"
            )

    guppi_aggregator: UPPAggrSelector = field(kw_only=False)
    """Aggregator for GUPPI test."""

    @guppi_aggregator.default
    def __gad(_i: UPPTestRegime) -> UPPAggrSelector:
        return (
            UPPAggrSelector.MIN
            if _i.resolution == INVResolution.ENFT
            else UPPAggrSelector.MAX
        )

    divr_aggregator: UPPAggrSelector = field(kw_only=False)
    """Aggregator for diversion ratio test."""

    @divr_aggregator.default
    def __dad(_i: UPPTestRegime) -> UPPAggrSelector:
        return _i.guppi_aggregator


@frozen
class UPPTestsCounts:
    """Counts of markets resolved as specified.

    Resolution may be either :attr:`INVResolution.ENFT`,
    :attr:`INVResolution.CLRN`, or :attr:`INVResolution.BOTH`.
    In the case of :attr:`INVResolution.BOTH`, two columns of counts
    are returned: one for each resolution.
    """

    by_firm_count: ArrayBIGINT = field(eq=cmp_using(eq=np.array_equal))
    by_delta: ArrayBIGINT = field(eq=cmp_using(eq=np.array_equal))
    by_conczone: ArrayBIGINT = field(eq=cmp_using(eq=np.array_equal))
    """Zones are "unconcentrated", "moderately concentrated", and "highly concentrated",
    with further detail by HHI and ΔHHI for mergers in the "unconcentrated" and
    "moderately concentrated" zones. See
    :attr:`mergeron.gen.enforcement_stats.HMG_PRESUMPTION_ZONE_MAP` and
    :attr:`mergeron.gen.enforcement_stats.ZONE_VALS` for more detail.
    """


for _typ in (SeedSequenceData, ShareSpec, PCMSpec, UPPTestsCounts, UPPTestRegime):
    yamelize_attrs(_typ)
