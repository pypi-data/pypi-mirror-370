"""Methods to format and print summary statistics on merger enforcement patterns."""

import enum
from collections.abc import Mapping

import numpy as np
from scipy.interpolate import make_interp_spline  # type: ignore

from .. import VERSION, ArrayBIGINT, Enameled, this_yaml  # noqa: TID252
from ..core import INVData, INVTableData  # noqa: TID252
from ..core import ftc_merger_investigations_data as fid  # noqa: TID252
from . import INVResolution

__version__ = VERSION


@this_yaml.register_class
@enum.unique
class IndustryGroup(str, Enameled):
    """Industry group of reported markets."""

    ALL = "All Markets"
    GRO = "Grocery Markets"
    OIL = "Oil Markets"
    CHM = "Chemical Markets"
    PHM = "Pharmaceuticals Markets"
    HOS = "Hospital Markets"
    EDS = "Electronically-Controlled Devices and Systems Markets"
    BRD = "Branded Consumer Goods Markets"
    OTH = '"Other" Markets'
    IIC = "Industries in Common"


@this_yaml.register_class
@enum.unique
class OtherEvidence(str, Enameled):
    """Additional evidence available, if any, for reported markets."""

    HOT = "Hot Documents Identified"
    NHT = "No Hot Documents Identified"
    HTU = "No Evidence on Hot Documents"
    NCC = "No Strong Customer Complaints"
    SCC = "Strong Customer Complaints"
    CCU = "No Evidence on Customer Complaints"
    END = "Entry Difficult"
    EEY = "Entry Easy"
    EEU = "No Entry Evidence"
    UNR = "Unrestricted on additional evidence"


@this_yaml.register_class
@enum.unique
class StatsGrpSelector(str, Enameled):
    """Measure used to summarize investigations data."""

    FC = "ByFirmCount"
    HD = "ByHHIandDelta"
    DL = "ByDelta"
    ZN = "ByConcZone"


@this_yaml.register_class
@enum.unique
class StatsReturnSelector(str, Enameled):
    """Statistics to report on investigations data."""

    CNT = "count"
    RPT = "rate, point"
    RIN = "rate, interval"


@this_yaml.register_class
@enum.unique
class SortSelector(str, Enameled):
    """Sort order for reporting investigations data."""

    UCH = "unchanged"
    REV = "reversed"


# Parameters and functions to interpolate selected HHI and ΔHHI values
#   recorded in fractions to ranges of values in points on the HHI scale
HHI_DELTA_KNOTS = np.array([0, 100, 200, 300, 500, 800, 1200, 2500, 5001], int)
HHI_POST_ZONE_KNOTS = np.array([0, 1800, 2400, 10001], int)
hhi_delta_ranger, hhi_zone_post_ranger = (
    make_interp_spline(_f / 1e4, _f, k=0)
    for _f in (HHI_DELTA_KNOTS, HHI_POST_ZONE_KNOTS)
)


HMG_PRESUMPTION_ZONE_MAP: dict[int, dict[int, tuple[int, int, int]]] = {
    HHI_POST_ZONE_KNOTS[0]: {
        HHI_DELTA_KNOTS[0]: (0, 0, 0),
        HHI_DELTA_KNOTS[1]: (0, 0, 0),
        HHI_DELTA_KNOTS[2]: (0, 0, 0),
    },
    HHI_POST_ZONE_KNOTS[1]: {
        HHI_DELTA_KNOTS[0]: (0, 1, 1),
        HHI_DELTA_KNOTS[1]: (1, 1, 2),
        HHI_DELTA_KNOTS[2]: (1, 1, 2),
    },
    HHI_POST_ZONE_KNOTS[2]: {
        HHI_DELTA_KNOTS[0]: (0, 2, 1),
        HHI_DELTA_KNOTS[1]: (1, 2, 3),
        HHI_DELTA_KNOTS[2]: (2, 2, 4),
    },
}

ZONE_VALS = np.unique(
    np.vstack([
        tuple(HMG_PRESUMPTION_ZONE_MAP[_k].values()) for _k in HMG_PRESUMPTION_ZONE_MAP
    ]),
    axis=0,
)

ZONE_STRINGS = {
    0: R"Green Zone (Safeharbor)",
    1: R"Yellow Zone",
    2: R"Red Zone (SLC Presumption)",
    fid.TTL_KEY: "TOTAL",
}
ZONE_DETAIL_STRINGS_HHI = {
    0: Rf"HHI < {HHI_POST_ZONE_KNOTS[1]} pts.",
    1: R"HHI ∈ [{}, {}) pts. and ".format(*HHI_POST_ZONE_KNOTS[1:3]),
    2: Rf"HHI ⩾ {HHI_POST_ZONE_KNOTS[2]} pts. and ",
}
ZONE_DETAIL_STRINGS_DELTA = {
    0: "",
    1: Rf"ΔHHI < {HHI_DELTA_KNOTS[1]} pts.",
    2: Rf"ΔHHI ⩾ {HHI_DELTA_KNOTS[1]} pts.}}",
    3: R"ΔHHI ∈ [{}, {}) pts.".format(*HHI_DELTA_KNOTS[1:3]),
    4: Rf"ΔHHI ⩾ {HHI_DELTA_KNOTS[2]} pts.",
}


def enf_cnts_obs_by_group(
    _invdata_array_dict: INVData,
    _study_period: str,
    _table_ind_grp: IndustryGroup,
    _table_evid_cond: OtherEvidence,
    _stats_group: StatsGrpSelector,
    _enf_spec: INVResolution,
    /,
) -> ArrayBIGINT:
    """Summarize investigations data by reporting group.

    Parameters
    ----------
    _invdata_array_dict
        raw investigations data
    _study_period
        study period
    _table_ind_grp
        industry group
    _table_evid_cond
        additional evidence
    _stats_group
        grouping measure
    _enf_spec
        enforcement specification (see, :class:`mergeron.gen.INVResolution`)

    Returns
    -------
    ArrayBIGINT
        Counts of markets resolved as enforced, cleared, or both, respectively.
    """
    if _stats_group == StatsGrpSelector.HD:
        raise ValueError(
            f"Clearance/enforcement statistics, '{_stats_group}' not valied here."
        )

    match _stats_group:
        case StatsGrpSelector.FC:
            cnts_func = enf_cnts_byfirmcount
            cnts_listing_func = enf_cnts_obs_byfirmcount
        case StatsGrpSelector.DL:
            cnts_func = enf_cnts_bydelta
            cnts_listing_func = enf_cnts_obs_byhhianddelta
        case StatsGrpSelector.ZN:
            cnts_func = enf_cnts_byconczone
            cnts_listing_func = enf_cnts_obs_byhhianddelta

    return cnts_func(
        cnts_listing_func(
            _invdata_array_dict,
            _study_period,
            _table_ind_grp,
            _table_evid_cond,
            _enf_spec,
        )
    )


def enf_cnts_obs_byfirmcount(
    _data_array_dict: INVData,
    _data_period: str = "1996-2003",
    _table_ind_group: IndustryGroup = IndustryGroup.ALL,
    _table_evid_cond: OtherEvidence = OtherEvidence.UNR,
    _enf_spec: INVResolution = INVResolution.ENFT,
    /,
) -> ArrayBIGINT:
    """Summarize investigations data by firm count.

    Parameters
    ----------
    _data_array_dict
        raw investigations data
    _data_period
        data period
    _table_ind_group
        industry group
    _table_evid_cond
        additional evidence
    _enf_spec
        enforcement specification (see, :class:`mergeron.gen.INVResolution`)

    Returns
    -------
    ArrayBIGINT
        Counts of markets resolved as enforced, cleared, or both, respectively,
        reported by number of pre-merger firms.
    """
    if _data_period not in _data_array_dict:
        raise ValueError(
            f"Invalid value of data period, {f'"{_data_period}"'}."
            f"Must be one of, {tuple(_data_array_dict.keys())!r}."
        )

    data_array_dict_sub = _data_array_dict[_data_period][fid.TABLE_TYPES[1]]

    table_no_ = table_no_lku(data_array_dict_sub, _table_ind_group, _table_evid_cond)

    cnts_array = data_array_dict_sub[table_no_].data_array

    ndim_in = 1
    stats_kept_indxs = []
    match _enf_spec:
        case INVResolution.CLRN:
            stats_kept_indxs = [-1, -2]
        case INVResolution.ENFT:
            stats_kept_indxs = [-1, -3]
        case INVResolution.BOTH:
            stats_kept_indxs = [-1, -3, -2]

    return np.hstack([cnts_array[:, :ndim_in], cnts_array[:, stats_kept_indxs]])


def enf_cnts_obs_byhhianddelta(
    _data_array_dict: INVData,
    _data_period: str = "1996-2003",
    _table_ind_group: IndustryGroup = IndustryGroup.ALL,
    _table_evid_cond: OtherEvidence = OtherEvidence.UNR,
    _enf_spec: INVResolution = INVResolution.ENFT,
    /,
) -> ArrayBIGINT:
    """Summarize investigations data by HHI and ΔHHI.

    Parameters
    ----------
    _data_array_dict
        raw investigations data
    _data_period
        data period
    _table_ind_group
        industry group
    _table_evid_cond
        additional evidence
    _enf_spec
        enforcement specification (see, :class:`mergeron.gen.INVResolution`)

    Returns
    -------
    ArrayBIGINT
        Counts of markets resolved as enforced, cleared, or both, respectively,
        reported by HHI and ΔHHI.
    """
    if _data_period not in _data_array_dict:
        raise ValueError(
            f"Invalid value of data period, {f'"{_data_period}"'}."
            f"Must be one of, {tuple(_data_array_dict.keys())!r}."
        )

    data_array_dict_sub = _data_array_dict[_data_period][fid.TABLE_TYPES[0]]

    table_no_ = table_no_lku(data_array_dict_sub, _table_ind_group, _table_evid_cond)

    cnts_array = data_array_dict_sub[table_no_].data_array

    ndim_in = 2
    stats_kept_indxs = []
    match _enf_spec:
        case INVResolution.CLRN:
            stats_kept_indxs = [-1, -2]
        case INVResolution.ENFT:
            stats_kept_indxs = [-1, -3]
        case INVResolution.BOTH:
            stats_kept_indxs = [-1, -3, -2]

    return np.hstack([cnts_array[:, :ndim_in], cnts_array[:, stats_kept_indxs]])


def table_no_lku(
    _data_array_dict_sub: Mapping[str, INVTableData],
    _table_ind_group: IndustryGroup = IndustryGroup.ALL,
    _table_evid_cond: OtherEvidence = OtherEvidence.UNR,
    /,
) -> str:
    """Lookup table number based on industry group and additional evidence."""
    if _table_evid_cond not in (
        _egl := [
            _data_array_dict_sub[_v].additional_evidence for _v in _data_array_dict_sub
        ]
    ):
        raise ValueError(
            f"Invalid value for additional evidence, {f'"{_table_evid_cond}"'}."
            f"Must be one of {_egl!r}"
        )
    if _table_ind_group not in (
        _igl := [_data_array_dict_sub[_v].industry_group for _v in _data_array_dict_sub]
    ):
        raise ValueError(
            f"Invalid value for industry group, {f'"{_table_ind_group}"'}."
            f"Must be one of {_igl!r}"
        )

    tno_ = next(
        _t
        for _t in _data_array_dict_sub
        if all((
            _data_array_dict_sub[_t].industry_group == _table_ind_group,
            _data_array_dict_sub[_t].additional_evidence == _table_evid_cond,
        ))
    )

    return tno_


def enf_cnts_byfirmcount(_cnts_array: ArrayBIGINT, /) -> ArrayBIGINT:
    """Summarize investigations data by firm count.

    Parameters
    ----------
    _cnts_array
        raw investigations data array

    Returns
    -------
    ArrayBIGINT
        Subtotals for columns other than the first, grouped by the first column.
    """
    if not _cnts_array[:, 0].any():
        return np.array([], int)

    ndim_in = 1
    return np.vstack([
        np.concatenate([
            (_i,),
            np.einsum(
                "ij->j", _cnts_array[_cnts_array[:, 0] == _i][:, ndim_in:], dtype=int
            ),
        ])
        for _i in np.unique(_cnts_array[:, 0])
    ])


def enf_cnts_bydelta(_cnts_array: ArrayBIGINT, /) -> ArrayBIGINT:
    """Summarize investigations data by ΔHHI.

    Parameters
    ----------
    _cnts_array
        raw investigations data array

    Returns
    -------
    ArrayBIGINT
        Subtotals for columns higher than the second, grouped by the second column.
    """
    if not _cnts_array[:, 1].any():
        return np.array([], int)
    ndim_in = 2
    return np.vstack([
        np.concatenate([
            (_k,),
            np.einsum(
                "ij->j", _cnts_array[_cnts_array[:, 1] == _k][:, ndim_in:], dtype=int
            ),
        ])
        for _k in HHI_DELTA_KNOTS[:-1]
    ])


def enf_cnts_byconczone(_cnts_array: ArrayBIGINT, /) -> ArrayBIGINT:
    """Summarize investigations data by concentration zone, as defined in the Guidelines.

    Includes sub-total detail for "Moderately Concentrated" and "Unconcentrated" markets.

    Parameters
    ----------
    _cnts_array
        raw investigations data array

    Returns
    -------
    ArrayBIGINT
        Subtotals range of HHI and ΔHHI, with detail
    """
    if not _cnts_array[:, 0].any() or np.isnan(_cnts_array[:, 0]).all():
        return np.array([], int)
    # Step 1: Tag and agg. from HHI-post and ΔHHI to zone triple
    # NOTE: Although you could just map and not (partially) aggregate in this step,
    # the mapped array is a copy, and is larger without partial aggregation, so
    # aggregation reduces the footprint of this step in memory. Although this point
    # is more relevant for generated than observed data, using the same coding pattern
    # in both cases does make life easier
    _ndim_in = 2
    _nkeys = 3
    cnts_byhhipostanddelta: ArrayBIGINT = np.zeros(
        (1, _nkeys + _cnts_array.shape[1] - _ndim_in), dtype=int
    )
    cnts_byconczone: ArrayBIGINT = np.zeros(
        (1, _nkeys + _cnts_array.shape[1] - _ndim_in), dtype=int
    )

    # Prepare to tag clearance stats by presumption zone
    hhi_zone_post_ranged = hhi_zone_post_ranger(_cnts_array[:, 0] / 1e4)
    hhi_delta_ranged = hhi_delta_ranger(_cnts_array[:, 1] / 1e4)
    for _hhi_zone_post_lim in HHI_POST_ZONE_KNOTS[:-1]:
        zone_test = hhi_zone_post_ranged == _hhi_zone_post_lim

        for hhi_zone_delta_lim in HHI_DELTA_KNOTS[:3]:
            delta_test = (
                (hhi_delta_ranged >= hhi_zone_delta_lim)
                if hhi_zone_delta_lim == HHI_DELTA_KNOTS[2]
                else (hhi_delta_ranged == hhi_zone_delta_lim)
            )

            zone_val = HMG_PRESUMPTION_ZONE_MAP[_hhi_zone_post_lim][hhi_zone_delta_lim]

            conc_test = zone_test & delta_test

            cnts_byhhipostanddelta = np.vstack((
                cnts_byhhipostanddelta,
                np.array(
                    (
                        *zone_val,
                        *np.einsum(
                            "ij->j", _cnts_array[:, _ndim_in:][conc_test], dtype=int
                        ),
                    ),
                    dtype=int,
                ),
            ))
    cnts_byhhipostanddelta = cnts_byhhipostanddelta[1:]

    for zone_val in ZONE_VALS:
        # Logical-and of multiple vectors:
        hhi_zone_test = (
            1
            * np.stack(
                [
                    cnts_byhhipostanddelta[:, _idx] == _val
                    for _idx, _val in enumerate(zone_val)
                ],
                axis=1,
            )
        ).prod(axis=1) == 1

        cnts_byconczone = np.vstack((
            cnts_byconczone,
            np.concatenate(
                (
                    zone_val,
                    np.einsum(
                        "ij->j",
                        cnts_byhhipostanddelta[hhi_zone_test][:, _nkeys:],
                        dtype=int,
                    ),
                ),
                dtype=int,
            ),
        ))

    return cnts_byconczone[1:]
