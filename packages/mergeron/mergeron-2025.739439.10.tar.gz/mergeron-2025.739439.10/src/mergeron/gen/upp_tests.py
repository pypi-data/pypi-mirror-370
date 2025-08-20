"""Methods to compute intrinsic enforcement/clearance rates from generated market data."""

from collections.abc import Sequence
from typing import TypedDict

import numpy as np
from numpy.random import SeedSequence

from .. import (  # noqa
    VERSION,
    ArrayBIGINT,
    ArrayBoolean,
    ArrayDouble,
    ArrayFloat,
    ArrayINT,
    HMGPubYear,
    UPPAggrSelector,
)
from ..core import guidelines_boundaries as gbl  # noqa: TID252
from . import INVResolution, MarketSampleData, UPPTestRegime, UPPTestsCounts
from . import enforcement_stats as esl

__version__ = VERSION


class INVRESCntsArgs(TypedDict, total=False):
    """Keyword arguments of function, :code:`sim_enf_cnts`."""

    sample_size: int
    seed_seq_list: Sequence[SeedSequence] | None
    nthreads: int


def compute_upp_test_counts(
    _market_data_sample: MarketSampleData,
    _upp_test_parms: gbl.HMGThresholds,
    _upp_test_regime: UPPTestRegime,
    /,
) -> UPPTestsCounts:
    """Estimate enforcement and clearance counts from market data sample.

    Parameters
    ----------
    _market_data_sample
        Market data sample

    _upp_test_parms
        Threshold values for various Guidelines criteria

    _upp_test_regime
        Specifies whether to analyze enforcement, clearance, or both
        and the GUPPI and diversion ratio aggregators employed, with
        default being to analyze enforcement based on the maximum
        merging-firm GUPPI and maximum diversion ratio between the
        merging firms

    Returns
    -------
    UPPTestsCounts
        Enforced and cleared counts

    """
    g_bar_, divr_bar_, cmcr_bar_, ipr_bar_ = (
        getattr(_upp_test_parms, _f) for _f in ("guppi", "divr", "cmcr", "ipr")
    )

    guppi_array, ipr_array, cmcr_array = (
        np.empty_like(_market_data_sample.price_array) for _ in range(3)
    )

    np.einsum(
        "ij,ij,ij->ij",
        _market_data_sample.divr_array,
        _market_data_sample.pcm_array[:, ::-1],
        _market_data_sample.price_array[:, ::-1] / _market_data_sample.price_array,
        out=guppi_array,
    )

    np.divide(
        np.einsum(
            "ij,ij->ij", _market_data_sample.pcm_array, _market_data_sample.divr_array
        ),
        1 - _market_data_sample.divr_array,
        out=ipr_array,
    )

    np.divide(ipr_array, 1 - _market_data_sample.pcm_array, out=cmcr_array)

    (divr_test_vector,) = _compute_test_array_seq(
        (_market_data_sample.divr_array,),
        _market_data_sample.frmshr_array,
        _upp_test_regime.divr_aggregator,
    )

    (guppi_test_vector, cmcr_test_vector, ipr_test_vector) = _compute_test_array_seq(
        (guppi_array, cmcr_array, ipr_array),
        _market_data_sample.frmshr_array,
        _upp_test_regime.guppi_aggregator,
    )
    del cmcr_array, ipr_array, guppi_array

    if _upp_test_regime.resolution == INVResolution.ENFT:
        upp_test_arrays = np.hstack((
            guppi_test_vector >= g_bar_,
            (guppi_test_vector >= g_bar_) | (divr_test_vector >= divr_bar_),
            cmcr_test_vector >= cmcr_bar_,
            ipr_test_vector >= ipr_bar_,
        ))
    else:
        upp_test_arrays = np.hstack((
            guppi_test_vector < g_bar_,
            (guppi_test_vector < g_bar_) & (divr_test_vector < divr_bar_),
            cmcr_test_vector < cmcr_bar_,
            ipr_test_vector < ipr_bar_,
        ))

    fcounts, hhi_delta, hhi_post = (
        getattr(_market_data_sample, _g) for _g in ("fcounts", "hhi_delta", "hhi_post")
    )

    # Clearance counts by firm count
    enf_cnts_sim_byfirmcount_array = esl.enf_cnts_byfirmcount(
        np.hstack((fcounts, np.ones_like(fcounts), upp_test_arrays))
    )

    # Clearance counts by Delta and Concentration Zone
    hhi_zone_ranged = (
        esl.hhi_zone_post_ranger(hhi_post).astype(int)
        if hhi_post.any() and not np.isnan(hhi_post).all()
        else np.zeros_like(hhi_post, int)
    )
    hhi_delta_ranged = esl.hhi_delta_ranger(hhi_delta).astype(int)

    enf_cnts_sim_byhhianddelta_array = np.hstack(
        (
            hhi_zone_ranged,
            hhi_delta_ranged,
            np.ones_like(hhi_delta_ranged),
            upp_test_arrays,
        ),
        dtype=int,
    )

    enf_cnts_sim_bydelta_array = esl.enf_cnts_bydelta(enf_cnts_sim_byhhianddelta_array)
    enf_cnts_sim_byconczone_array = esl.enf_cnts_byconczone(
        enf_cnts_sim_byhhianddelta_array
    )

    return UPPTestsCounts(
        enf_cnts_sim_byfirmcount_array,
        enf_cnts_sim_bydelta_array,
        enf_cnts_sim_byconczone_array,
    )


def _compute_test_array_seq(
    _test_measure_seq: tuple[ArrayDouble, ...],
    _wt_array: ArrayDouble,
    _aggregator: UPPAggrSelector,
) -> tuple[ArrayDouble, ...]:
    _wt_array = (
        _wt_array / np.einsum("ij->i", _wt_array)[:, None]
        if _aggregator
        in {
            UPPAggrSelector.CPA,
            UPPAggrSelector.CPD,
            UPPAggrSelector.OSA,
            UPPAggrSelector.OSD,
        }
        else np.array([0.5, 0.5], float)
    )

    match _aggregator:
        case UPPAggrSelector.AVG:
            test_array_seq = (
                1 / 2 * np.einsum("ij->i", _g)[:, None] for _g in _test_measure_seq
            )
        case UPPAggrSelector.CPA:
            test_array_seq = (
                np.einsum("ij,ij->i", _wt_array[:, ::-1], _g)[:, None]
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.CPD:
            test_array_seq = (
                np.sqrt(np.einsum("ij,ij,ij->i", _wt_array[:, ::-1], _g, _g))[:, None]
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.CPG:
            test_array_seq = (
                np.expm1(
                    np.einsum("ij,ij->i", _wt_array[:, ::-1], np.log1p(_g))[:, None]
                )
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.DIS:
            test_array_seq = (
                np.sqrt(1 / 2 * np.einsum("ij,ij->i", _g, _g))[:, None]
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.GMN:
            test_array_seq = (
                np.expm1(np.einsum("ij->i", np.log1p(_g))[:, None] / _g.shape[1])
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.MAX:
            test_array_seq = (_g.max(axis=1, keepdims=True) for _g in _test_measure_seq)
        case UPPAggrSelector.MIN:
            test_array_seq = (_g.min(axis=1, keepdims=True) for _g in _test_measure_seq)
        case UPPAggrSelector.OSA:
            test_array_seq = (
                np.einsum("ij,ij->i", _wt_array, _g)[:, None]
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.OSD:
            test_array_seq = (
                np.sqrt(np.einsum("ij,ij,ij->i", _wt_array, _g, _g)[:, None])
                for _g in _test_measure_seq
            )
        case UPPAggrSelector.OSG:
            test_array_seq = (
                np.expm1(np.einsum("ij,ij->i", _wt_array, np.log1p(_g))[:, None])
                for _g in _test_measure_seq
            )
        case _:
            raise ValueError("GUPPI/diversion ratio aggregation method is invalid.")
    return tuple(test_array_seq)


if __name__ == "__main__":
    print(
        "This module defines classes with methods for generating UPP test arrays and UPP test-counts arrays on given data."
    )
