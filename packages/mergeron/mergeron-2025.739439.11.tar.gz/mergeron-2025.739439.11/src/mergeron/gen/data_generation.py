"""Methods to generate data for analyzing merger enforcement policy."""

from __future__ import annotations

import zipfile
from itertools import starmap
from typing import TypedDict

import numpy as np
from attrs import Attribute, Converter, define, field, validators
from joblib import Parallel, cpu_count, delayed, parallel_config  # type: ignore
from numpy.random import SeedSequence
from ruamel import yaml

from .. import (  # noqa: TID252  # noqa
    _PKG_NAME,
    NTHREADS,
    VERSION,
    RECForm,
    this_yaml,
    yaml_rt_mapper,
)
from ..core import guidelines_boundaries as gbl  # noqa: TID252
from ..core.guidelines_boundaries import HMGThresholds  # noqa: TID252
from . import (
    INVResolution,  # noqa: F401
    MarketSampleData,
    PCMDistribution,
    PCMRestriction,
    PCMSpec,
    PriceSpec,
    SeedSequenceData,
    ShareSpec,
    SHRDistribution,
    SSZConstant,
    UPPTestRegime,
    UPPTestsCounts,
)
from .data_generation_functions import (
    gen_divr_array,
    gen_margin_price_data,
    gen_share_data,
)
from .upp_tests import compute_upp_test_counts

__version__ = VERSION

H5_CHUNK_SIZE = 10**6


class SamplingFunctionKWArgs(TypedDict, total=False):
    """Keyword arguments of sampling methods defined below."""

    sample_size: int
    """number of draws to generate"""

    seed_data: SeedSequenceData | None
    """seed data to ensure independent and replicable draws"""

    nthreads: int
    """number of parallel threads to use"""


def _seed_data_conv(_v: SeedSequenceData | None, _i: MarketSample) -> SeedSequenceData:
    if isinstance(_v, SeedSequenceData):
        return _v

    _sseq = tuple(SeedSequence(pool_size=8) for _ in range(4))
    _sdtt = _i.share_spec.dist_type == SHRDistribution.UNI
    _pst = _i.price_spec == PriceSpec.RNG

    return SeedSequenceData(
        share=_sseq[0],
        pcm=_sseq[1],
        fcounts=(None if _sdtt else _sseq[2]),
        price=(None if not _pst else (_sseq[2] if _sdtt else _sseq[3])),
    )


@this_yaml.register_class
@define(kw_only=True)
class MarketSample:
    """Parameter specification for market data generation."""

    share_spec: ShareSpec = field(
        default=ShareSpec(SHRDistribution.UNI),
        validator=validators.instance_of(ShareSpec),
    )
    """Market-share specification, see :class:`ShareSpec`"""

    pcm_spec: PCMSpec = field(
        default=PCMSpec(PCMDistribution.UNI), validator=validators.instance_of(PCMSpec)
    )
    """Margin specification, see :class:`PCMSpec`"""

    @pcm_spec.validator
    def _psv(self, _a: Attribute[PCMSpec], _v: PCMSpec, /) -> None:
        if (
            self.share_spec.recapture_form == RECForm.FIXED
            and _v.pcm_restriction == PCMRestriction.MNL
        ):
            raise ValueError(
                f'Specification of "PCMSpec.pcm_restriction", as {PCMRestriction.MNL!r} '
                f'requires that "ShareSpec.recapture_form" be {RECForm.INOUT!r} '
                f"or {RECForm.OUTIN!r}, not {RECForm.FIXED!r} as presently specified"
            )

    price_spec: PriceSpec = field(
        default=PriceSpec.SYM, validator=validators.instance_of(PriceSpec)
    )
    """Price specification, see :class:`PriceSpec`"""

    hsr_filing_test_type: SSZConstant = field(
        default=SSZConstant.ONE, validator=validators.instance_of(SSZConstant)
    )
    """Method for modeling HSR filing thresholds, see :class:`SSZConstant`"""

    sample_size: int = field(default=10**6, validator=validators.instance_of(int))
    """number of draws to simulate"""

    seed_data: SeedSequenceData = field(
        converter=Converter(_seed_data_conv, takes_self=True)  # type: ignore
    )
    """sequence of SeedSequences to ensure replicable data generation with
    appropriately independent random streams
    """

    @seed_data.default
    def __dsd(self) -> SeedSequenceData | None:
        return _seed_data_conv(None, self)

    @seed_data.validator
    def _sdv(
        _i: MarketSample, _a: Attribute[SeedSequenceData], _v: SeedSequenceData, /
    ) -> None:
        if _i.share_spec.dist_type == SHRDistribution.UNI and any((
            _v.fcounts,
            _v.price,
        )):
            raise ValueError(
                "Attribute, seed_data.fcounts is ignored as irrelevant when "
                "market shares are drawn with Uniform distribution. "
                "Set seed_data.fcounts to None and retry."
            )

        if _i.price_spec != PriceSpec.RNG and _v.price is not None:
            raise ValueError(
                "Attribute, seed_data.price is ignored as irrelevant unless "
                "prices are asymmetric and uncorrelated and price-cost margins "
                "are also not symmetric. Set seed_data.price to None and retry."
            )

    nthreads: int = field(default=NTHREADS, validator=validators.instance_of(int))
    """number of parallel threads to use"""

    dataset: MarketSampleData | None = field(default=None, init=False)

    enf_counts: UPPTestsCounts | None = field(default=None, init=False)

    def _gen_market_sample(
        self, /, *, sample_size: int, seed_data: SeedSequenceData, nthreads: int
    ) -> MarketSampleData:
        """
        Generate share, diversion ratio, price, and margin data for MarketSpec.

        see :attr:`SamplingFunctionKWArgs` for description of keyword parameters

        Returns
        -------
            Merging firms' shares, margins, etc. for each hypothetical  merger
            in the sample

        """
        # Scale up sample size to offset discards based on specified criteria
        shr_sample_size = sample_size * self.hsr_filing_test_type
        shr_sample_size *= (
            SSZConstant.MNL_DEP
            if self.pcm_spec.pcm_restriction == PCMRestriction.MNL
            else 1
        )
        shr_sample_size = int(shr_sample_size)

        # Generate share data
        mktshr_data = gen_share_data(
            shr_sample_size,
            self.share_spec,
            seed_data.fcounts,
            seed_data.share,
            nthreads,
        )
        mktshr_array_ = mktshr_data.mktshr_array
        fcounts_ = mktshr_data.fcounts
        aggregate_purchase_prob_ = mktshr_data.aggregate_purchase_prob
        nth_firm_share_ = mktshr_data.nth_firm_share
        del mktshr_data

        # Generate merging-firm price and PCM data
        margin_data, price_data = gen_margin_price_data(
            mktshr_array_[:, :2],
            nth_firm_share_,
            aggregate_purchase_prob_,
            self.pcm_spec,
            self.price_spec,
            self.hsr_filing_test_type,
            seed_data.pcm,
            seed_data.price,
            nthreads,
        )
        pcm_array_ = margin_data.pcm_array
        price_array_ = price_data.price_array

        if shr_sample_size > sample_size:
            mnl_test_rows = margin_data.mnl_test_array * price_data.hsr_filing_test

            mktshr_array_ = mktshr_array_[mnl_test_rows][:sample_size]
            pcm_array_ = margin_data.pcm_array[mnl_test_rows][:sample_size]
            price_array_ = price_data.price_array[mnl_test_rows][:sample_size]
            fcounts_ = fcounts_[mnl_test_rows][:sample_size]
            aggregate_purchase_prob_ = aggregate_purchase_prob_[mnl_test_rows][
                :sample_size
            ]
            nth_firm_share_ = nth_firm_share_[mnl_test_rows][:sample_size]

            del mnl_test_rows

        # Calculate diversion ratios
        divr_array = gen_divr_array(
            self.share_spec.recapture_form,
            self.share_spec.recapture_ratio,
            mktshr_array_[:, :2],
            aggregate_purchase_prob_,
        )

        return MarketSampleData(
            mktshr_array_[:, :2],
            pcm_array_,
            price_array_,
            divr_array,
            np.einsum("ij,ij->i", mktshr_array_[:, :2], mktshr_array_[:, [1, 0]])[
                :, None
            ],
            aggregate_purchase_prob_,
            fcounts_,
            nth_firm_share_,
            (
                np.einsum("ij,ij->i", mktshr_array_[:, :2], mktshr_array_[:, [1, 0]])
                + np.einsum("ij,ij->i", mktshr_array_, mktshr_array_)
            )[:, None],
        )

    def generate_sample(self, /) -> None:
        """Populate :attr:`data` with generated data.

        Returns
        -------
        None

        """
        self.dataset = self._gen_market_sample(
            seed_data=self.seed_data,
            sample_size=self.sample_size,
            nthreads=self.nthreads,
        )

    def __sim_enf_cnts(
        self,
        _upp_test_parms: gbl.HMGThresholds,
        _sim_test_regime: UPPTestRegime,
        /,
        *,
        seed_data: SeedSequenceData,
        sample_size: int = 10**6,
        nthreads: int = NTHREADS,
    ) -> UPPTestsCounts:
        """Generate market data and compute UPP test counts on same.

        Parameters
        ----------
        _upp_test_parms
            Guidelines thresholds for testing UPP and related statistics

        _sim_test_regime
            Configuration to use for testing; UPPTestsRegime object
            specifying whether investigation results in enforcement, clearance,
            or both; and aggregation methods used for GUPPI and diversion ratio
            measures

        sample_size
            Number of draws to generate

        seed_data
            List of seed sequences, to assure independent samples in each thread

        nthreads
            Number of parallel processes to use

        Returns
        -------
            UPPTestCounts object with  of test counts by firm count, ΔHHI and concentration zone

        """
        market_data_sample = self._gen_market_sample(
            sample_size=sample_size, seed_data=seed_data, nthreads=nthreads
        )

        upp_test_arrays: UPPTestsCounts = compute_upp_test_counts(
            market_data_sample, _upp_test_parms, _sim_test_regime
        )

        return upp_test_arrays

    def __sim_enf_cnts_ll(
        self, _enf_parm_vec: gbl.HMGThresholds, _sim_test_regime: UPPTestRegime, /
    ) -> UPPTestsCounts:
        """Parallelize data-generation and testing.

        The parameters `_sim_enf_cnts_kwargs` are passed unaltered to
        the parent function, `sim_enf_cnts()`, except that, if provided,
        `seed_data` is used to spawn a seed sequence for each thread,
        to assure independent samples in each thread, and `nthreads` defines
        the number of parallel processes used. The number of draws in
        each thread may be tuned, by trial and error, to the amount of
        memory (RAM) available.

        Parameters
        ----------
        _enf_parm_vec
            Guidelines thresholds to test against

        _sim_test_regime
            Configuration to use for testing

        Returns
        -------
            Arrays of enforcement counts or clearance counts by firm count,
            ΔHHI and concentration zone

        """
        sample_sz = self.sample_size
        subsample_sz = H5_CHUNK_SIZE
        iter_count = (sample_sz / subsample_sz).__ceil__()
        thread_count = self.nthreads or cpu_count()

        if (
            self.share_spec.recapture_form != RECForm.OUTIN
            and self.share_spec.recapture_ratio != _enf_parm_vec.rec
        ):
            raise ValueError(
                "{} {} {}".format(
                    f"Recapture ratio from market sample spec, {self.share_spec.recapture_ratio}",
                    f"must match the value, {_enf_parm_vec.rec}",
                    "the guidelines thresholds vector.",
                )
            )

        rng_seed_data = list(
            starmap(
                SeedSequenceData,
                zip(
                    *[
                        _s.spawn(iter_count) if _s else [None] * iter_count
                        for _s in (
                            getattr(self.seed_data, _a.name)
                            for _a in self.seed_data.__attrs_attrs__
                        )
                    ],
                    strict=True,
                ),
            )
        )

        sim_enf_cnts_kwargs: SamplingFunctionKWArgs = SamplingFunctionKWArgs({
            "sample_size": subsample_sz,
            "nthreads": thread_count,
        })

        with parallel_config(
            backend="threading",
            n_jobs=min(thread_count, iter_count),
            return_as="generator",
        ):
            res_list = Parallel()(
                delayed(self.__sim_enf_cnts)(
                    _enf_parm_vec,
                    _sim_test_regime,
                    **sim_enf_cnts_kwargs,
                    seed_data=_rng_seed_data_ch,
                )
                for _rng_seed_data_ch in rng_seed_data
            )

        res_list_stacks = UPPTestsCounts(*[
            np.stack([getattr(_j, _k) for _j in res_list])
            for _k in ("by_firm_count", "by_delta", "by_conczone")
        ])

        upp_test_results = UPPTestsCounts(*[
            (
                np.array([], int)
                if not (_gv := getattr(res_list_stacks, _g.name)).any()
                else np.hstack((
                    _gv[0, :, :_h],
                    np.einsum("ijk->jk", _gv[:, :, _h:], dtype=int),
                ))
            )
            for _g, _h in zip(res_list_stacks.__attrs_attrs__, [1, 1, 3], strict=True)
        ])
        del res_list, res_list_stacks

        return upp_test_results

    def estimate_enf_counts(
        self, _enf_parm_vec: HMGThresholds, _upp_test_regime: UPPTestRegime, /
    ) -> None:
        """Populate :attr:`enf_counts` with estimated UPP test counts.

        Parameters
        ----------
        _enf_parm_vec
            Threshold values for various Guidelines criteria

        _upp_test_regime
            Specifies whether to analyze enforcement, clearance, or both
            and the GUPPI and diversion ratio aggregators employed, with
            default being to analyze enforcement based on the maximum
            merging-firm GUPPI and maximum diversion ratio between the
            merging firms

        Returns
        -------
        None

        """
        if self.dataset is None:
            self.enf_counts = self.__sim_enf_cnts_ll(_enf_parm_vec, _upp_test_regime)
        else:
            self.enf_counts = compute_upp_test_counts(
                self.dataset, _enf_parm_vec, _upp_test_regime
            )

    def to_archive(
        self, zip_: zipfile.ZipFile, _subdir: str = "", /, *, save_dataset: bool = False
    ) -> None:
        """Serialize market sample to Zip archive."""
        zpath = zipfile.Path(zip_, at=_subdir)
        name_root = f"{_PKG_NAME}_market_sample"

        with (zpath / f"{name_root}.yaml").open("w") as _yfh:
            this_yaml.dump(self, _yfh)

        if save_dataset:
            if self.dataset is None and self.enf_counts is None:
                raise ValueError(
                    "No dataset and/or enforcement counts available for saving. "
                    "Generate some data or set save_dataset to False to proceed."
                )

            else:
                if self.dataset is not None:
                    with (zpath / f"{name_root}_dataset.h5").open("wb") as _hfh:
                        _hfh.write(self.dataset.to_h5bin())

                if self.enf_counts is not None:
                    with (zpath / f"{name_root}_enf_counts.yaml").open("w") as _yfh:
                        this_yaml.dump(self.enf_counts, _yfh)

    @staticmethod
    def from_archive(
        zip_: zipfile.ZipFile, _subdir: str = "", /, *, restore_dataset: bool = False
    ) -> MarketSample:
        """Deserialize market sample from Zip archive."""
        zpath = zipfile.Path(zip_, at=_subdir)
        name_root = f"{_PKG_NAME}_market_sample"

        market_sample_: MarketSample = this_yaml.load(
            (zpath / f"{name_root}.yaml").read_text()
        )

        if restore_dataset:
            _dt = (_dp := zpath / f"{name_root}_dataset.h5").is_file()
            _et = (_ep := zpath / f"{name_root}_enf_counts.yaml").is_file()
            if not (_dt or _et):
                raise ValueError(
                    "Archive has no sample data to restore. "
                    "Delete second argument, or set it False, and rerun."
                )
            else:
                if _dt:
                    with _dp.open("rb") as _hfh:
                        object.__setattr__(
                            market_sample_, "dataset", MarketSampleData.from_h5f(_hfh)
                        )
                if _et:
                    object.__setattr__(
                        market_sample_, "enf_counts", this_yaml.load(_ep.read_text())
                    )
        return market_sample_

    @classmethod
    def to_yaml(
        cls, _r: yaml.representer.RoundTripRepresenter, _d: MarketSample
    ) -> yaml.MappingNode:
        """Serialize market sample to YAML representation."""
        retval: yaml.MappingNode = _r.represent_mapping(
            f"!{cls.__name__}",
            {
                _a.name: getattr(_d, _a.name)
                for _a in _d.__attrs_attrs__
                if _a.name not in {"dataset", "enf_counts"}
            },
        )
        return retval

    @classmethod
    def from_yaml(
        cls, _c: yaml.constructor.RoundTripConstructor, _n: yaml.MappingNode
    ) -> MarketSample:
        """Deserialize market sample from YAML representation."""
        return cls(**yaml_rt_mapper(_c, _n))
