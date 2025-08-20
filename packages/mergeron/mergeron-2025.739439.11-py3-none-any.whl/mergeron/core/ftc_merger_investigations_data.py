"""
Methods to parse FTC Merger Investigations Data, downloading source documents as needed.

Notes
-----
Reported row and column totals from source data are not stored.

"""

from __future__ import annotations

import re
import shutil
from collections.abc import Mapping, Sequence
from operator import itemgetter
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import urllib3
from bs4 import BeautifulSoup
from numpy.testing import assert_array_equal

from .. import EMPTY_ARRAYINT, VERSION, ArrayBIGINT, this_yaml  # noqa: TID252
from .. import WORK_DIR as PKG_WORK_DIR  # noqa: TID252
from .. import data as mdat  # noqa: TID252
from . import (
    INVData,
    INVData_in,
    INVTableData,
    _dict_from_mapping,
    _mappingproxy_from_mapping,
)

__version__ = VERSION

# cspell: "includeRegExpList": ["strings", "comments", /( {3}['"]{3}).*?\\1/g]

WORK_DIR = globals().get("WORK_DIR", PKG_WORK_DIR)
"""Redefined, in case the user defines WORK_DIR betweeen module imports."""

FID_WORK_DIR = WORK_DIR / "FTCData"
if not FID_WORK_DIR.is_dir():
    FID_WORK_DIR.mkdir(parents=True)

INVDATA_ARCHIVE_PATH = WORK_DIR / mdat.FTC_MERGER_INVESTIGATIONS_DATA.name
if not INVDATA_ARCHIVE_PATH.is_file():
    shutil.copy2(mdat.FTC_MERGER_INVESTIGATIONS_DATA, INVDATA_ARCHIVE_PATH)  # type: ignore

TABLE_NO_RE = re.compile(r"Table \d+\.\d+")
TABLE_TYPES = ("ByHHIandDelta", "ByFirmCount")
CONC_TABLE_ALL = "Table 3.1"
CNT_TABLE_ALL = "Table 4.1"

TTL_KEY = 86825
CONC_HHI_DICT = {
    "0 - 1,799": 0,
    "1,800 - 1,999": 1800,
    "2,000 - 2,399": 2000,
    "2,400 - 2,999": 2400,
    "3,000 - 3,999": 3000,
    "4,000 - 4,999": 4000,
    "5,000 - 6,999": 5000,
    "7,000 - 10,000": 7000,
    "TOTAL": TTL_KEY,
}
CONC_DELTA_DICT = {
    "0 - 100": 0,
    "100 - 200": 100,
    "200 - 300": 200,
    "300 - 500": 300,
    "500 - 800": 500,
    "800 - 1,200": 800,
    "1,200 - 2,500": 1200,
    "2,500 - 5,000": 2500,
    "TOTAL": TTL_KEY,
}
CNT_FCOUNT_DICT = {
    "2 to 1": 2,
    "3 to 2": 3,
    "4 to 3": 4,
    "5 to 4": 5,
    "6 to 5": 6,
    "7 to 6": 7,
    "8 to 7": 8,
    "9 to 8": 9,
    "10 to 9": 10,
    "10 +": 11,
    "TOTAL": TTL_KEY,
}


def invert_map(_dict: Mapping[Any, Any]) -> Mapping[Any, Any]:
    """Invert mapping, mapping values to keys of the original mapping."""
    return {_v: _k for _k, _v in _dict.items()}


def construct_data(
    _archive_path: Path = INVDATA_ARCHIVE_PATH,
    *,
    flag_backward_compatibility: bool = True,
    flag_pharma_for_exclusion: bool = True,
    rebuild_data: bool = False,
) -> INVData:
    """Construct FTC merger investigations data for added non-overlapping periods.

    FTC merger investigations data are reported in cumulative periods,
    e.g., 1996-2003 and 1996-2011, but the analyst may want data reported in
    non-overlapping periods, e.g., 2004-2011. Given the way in which FTC had
    reported merger investigations data, the above example is the only instance
    in which the 1996-2003 data can be subtracted from the cumulative data to
    extract merger investigations data for the later period.
    See also, Kwoka, Sec. 2.3.3. [#]_

    Parameters
    ----------
    _archive_path
        Path to file container for serialized constructed data
    flag_backward_compatibility
        Flag whether the reported data should be treated as backward-compatible
    flag_pharma_for_exclusion
        Flag whether data for Pharmaceuticals is included in,  the set of
        industry groups with consistent reporting in both early and late periods

    Returns
    -------
        A dictionary of merger investigations data keyed to reporting periods

    References
    ----------

    .. [#] Kwoka, J., Greenfield, D., & Gu, C. (2015). Mergers, merger control,
       and remedies: A retrospective analysis of U.S. policy. MIT Press.

    """
    if _archive_path.is_file() and not rebuild_data:
        with (
            ZipFile(_archive_path, "r") as _yzh,
            _yzh.open(f"{_archive_path.stem}.yaml", "r") as _yfh,
        ):
            invdata_: INVData = this_yaml.load(_yfh)
        if not isinstance(invdata_, MappingProxyType):
            invdata_ = _mappingproxy_from_mapping(invdata_)
            with (
                ZipFile(_archive_path, "w", compression=ZIP_DEFLATED) as _yzh,
                _yzh.open(f"{_archive_path.stem}.yaml", "w") as _yfh,
            ):
                this_yaml.dump(invdata_, _yfh)
        return invdata_

    invdata: INVData_in = _dict_from_mapping(_parse_invdata())

    # Add some data periods (
    #   only periods ending in 2011, others have few observations and
    #   some incompatibilities
    #   )
    for data_period in "2004-2011", "2006-2011", "2008-2011":
        invdata_bld = _construct_new_period_data(
            invdata,
            data_period,
            flag_backward_compatibility=flag_backward_compatibility,
        )
        invdata |= {data_period: invdata_bld}

    # Create data for industries with no evidence on entry
    for data_period in invdata:
        _construct_no_evidence_data(invdata, data_period)

    # Create a list of exclusions to named industries in the base period,
    #   for construction of aggregate enforcement statistics where feasible
    industry_exclusion_list = {
        "AllMarkets",
        "OtherMarkets",
        "IndustriesinCommon",
        "",
        ("PharmaceuticalsMarkets" if flag_pharma_for_exclusion else None),
    }

    # Construct aggregate tables
    for data_period in "1996-2003", "1996-2011", "2004-2011":
        for table_type, table_no in zip(
            TABLE_TYPES, (CONC_TABLE_ALL, CNT_TABLE_ALL), strict=True
        ):
            invdata_sub_tabletype = invdata[data_period][table_type]

            aggr_tables_list = [
                t_
                for t_ in invdata["1996-2003"][table_type]
                if re.sub(
                    r"\W", "", invdata["1996-2003"][table_type][t_].industry_group
                )
                not in industry_exclusion_list
            ]

            invdata_sub_tabletype |= {
                table_no.replace(".1", ".X"): invdata_build_aggregate_table(
                    invdata_sub_tabletype, aggr_tables_list
                )
            }

    retval: INVData = _mappingproxy_from_mapping(invdata)
    with (
        ZipFile(_archive_path, "w", compression=ZIP_DEFLATED) as _yzh,
        _yzh.open(f"{_archive_path.stem}.yaml", "w") as _yfh,
    ):
        this_yaml.dump(retval, _yfh)

    return retval


def _construct_no_evidence_data(_invdata: INVData_in, _data_period: str, /) -> None:
    invdata_ind_grp = "All Markets"
    table_nos_map = dict(
        zip(
            (
                "No Entry Evidence",
                "No Evidence on Customer Complaints",
                "No Evidence on Hot Documents",
            ),
            (
                {"ByHHIandDelta": "Table 9.X", "ByFirmCount": "Table 10.X"},
                {"ByHHIandDelta": "Table 7.X", "ByFirmCount": "Table 8.X"},
                {"ByHHIandDelta": "Table 5.X", "ByFirmCount": "Table 6.X"},
            ),
            strict=True,
        )
    )
    for invdata_evid_cond in (
        "No Entry Evidence",
        "No Evidence on Customer Complaints",
        "No Evidence on Hot Documents",
    ):
        for stats_grp in ("ByHHIandDelta", "ByFirmCount"):
            invdata_sub_evid_cond_conc = _invdata[_data_period][stats_grp]

            dtn = table_nos_map[invdata_evid_cond]["ByHHIandDelta"]
            stn0 = "Table 4.1" if stats_grp == "ByFirmCount" else "Table 3.1"
            stn1, stn2 = (dtn.replace(".X", f".{_i}") for _i in ("1", "2"))

            invdata_sub_evid_cond_conc |= {
                dtn: INVTableData(
                    invdata_ind_grp,
                    invdata_evid_cond,
                    np.hstack((
                        invdata_sub_evid_cond_conc[stn0].data_array[:, :2],
                        (
                            invdata_sub_evid_cond_conc[stn0].data_array[:, 2:]
                            - invdata_sub_evid_cond_conc[stn1].data_array[:, 2:]
                            - invdata_sub_evid_cond_conc[stn2].data_array[:, 2:]
                        ),
                    )),
                )
            }


def _construct_new_period_data(
    _invdata: INVData_in,
    _data_period: str,
    /,
    *,
    flag_backward_compatibility: bool = False,
) -> dict[str, dict[str, INVTableData]]:
    cuml_period = f"1996-{_data_period.split('-')[1]}"
    if cuml_period != "1996-2011":
        raise ValueError('Expected cumulative period, "1996-2011"')

    invdata_cuml = _invdata[cuml_period]

    base_period = "1996-{}".format(int(_data_period.split("-")[0]) - 1)
    invdata_base = _invdata[base_period]

    if tuple(invdata_cuml.keys()) != TABLE_TYPES:
        raise ValueError("Source data does not include the expected groups of tables.")

    invdata_bld = {}
    for table_type in TABLE_TYPES:
        data_typesubdict = {}
        for table_no in invdata_cuml[table_type]:
            invdata_cuml_sub_table = invdata_cuml[table_type][table_no]
            invdata_ind_group, invdata_evid_cond, invdata_cuml_array = (
                invdata_cuml_sub_table.industry_group,
                invdata_cuml_sub_table.additional_evidence,
                invdata_cuml_sub_table.data_array,
            )

            invdata_base_sub_table = invdata_base[table_type].get(
                table_no, INVTableData("", "", EMPTY_ARRAYINT)
            )

            (invdata_base_ind_group, invdata_base_evid_cond, invdata_base_array) = (
                getattr(invdata_base_sub_table, _a)
                for _a in ("industry_group", "additional_evidence", "data_array")
            )

            # Some tables can't be constructed due to inconsistencies in the data
            # across time periods
            if (
                (_data_period != "2004-2011" and invdata_ind_group != "All Markets")
                or (invdata_ind_group in {'"Other" Markets', "Industries in Common"})
                or (invdata_base_ind_group in {'"Other" Markets', ""})
            ):
                continue

            # NOTE: Clean data to enforce consistency in FTC data
            if flag_backward_compatibility:
                # Consistency here means that the number of investigations reported
                # in each period is no less than the number reported in
                # any prior period.Although the time periods for table 3.2 through 3.5
                # are not the same in the data for 1996-2005 and 1996-2007 as in
                # the data for the other periods, they are nonetheless shorter than
                # the period 1996-2011, and hence the counts reported for 1996-2011
                # cannot be less than those reported in these prior periods. Note that
                # The number of "revisions" applied below, for enforcing consistency,
                # is sufficiently small as to be unlikely to substantially impact
                # results from analysis of the data.
                invdata_cuml_array_stack = []
                invdata_base_array_stack = []

                for data_period_detail in _invdata:
                    pd_start, pd_end = (int(g) for g in data_period_detail.split("-"))
                    if pd_start == 1996:
                        invdata_cuml_array_stack += [
                            _invdata[data_period_detail][table_type][
                                table_no
                            ].data_array[:, -3:-1]
                        ]
                    if pd_start == 1996 and pd_end < int(_data_period.split("-")[0]):
                        invdata_base_array_stack += [
                            _invdata[data_period_detail][table_type][
                                table_no
                            ].data_array[:, -3:-1]
                        ]
                invdata_cuml_array_enfcls, invdata_base_array_enfcls = (
                    np.stack(_f).max(axis=0)
                    for _f in (invdata_cuml_array_stack, invdata_base_array_stack)
                )
                invdata_array_bld_enfcls = (
                    invdata_cuml_array_enfcls - invdata_base_array_enfcls
                )
            else:
                # Consistency here means that the most recent data are considered
                # the most accurate, and when constructing data for a new period
                # any negative counts for merger investigations "enforced" or "closed"
                # are reset to zero (non-negativity). The above convention is adopted
                # on the basis of discussions with FTC staff, and given that FTC does
                # not assert backward compatibility published data on
                # merger investigations. Also, FTC appears to maintain that
                # the most recently published data are considered the most accurate
                # account of the pattern of FTC investigations of horizontal mergers,
                # and that the figures for any reported period represent the most
                # accurate data for that period. The published data may not be fully
                # backward compatible due to minor variation in (applying) the criteria
                # for inclusion, as well as industry coding, undertaken to maintain
                # transparency on the enforcement process.
                invdata_array_bld_enfcls = (
                    invdata_cuml_array[:, -3:-1] - invdata_base_array[:, -3:-1]
                )

                # # // spellchecker: disable
                # To examine the number of corrected values per table,  // spellchecker: disable
                # uncomment the statements below
                # invdata_array_bld_tbc = where(
                #   invdata_array_bld_enfcls < 0, invdata_array_bld_enfcls, 0
                # )
                # if np.einsum('ij->', invdata_array_bld_tbc):
                #     print(
                #       f"{_data_period}, {_table_no}, {invdata_ind_group}:",
                #       abs(np.einsum('ij->', invdata_array_bld_tbc))
                #       )
                # #  // spellchecker: disable

                # Enforce non-negativity
                invdata_array_bld_enfcls = np.stack((
                    invdata_array_bld_enfcls,
                    np.zeros_like(invdata_array_bld_enfcls),
                )).max(axis=0)

            invdata_array_bld = np.hstack((
                invdata_cuml_array[:, :-3],
                invdata_array_bld_enfcls,
                np.einsum("ij->i", invdata_array_bld_enfcls)[:, None],
            ))

            data_typesubdict[table_no] = INVTableData(
                invdata_ind_group, invdata_evid_cond, invdata_array_bld
            )
            del invdata_ind_group, invdata_evid_cond, invdata_cuml_array
            del invdata_base_ind_group, invdata_base_evid_cond, invdata_base_array
            del invdata_array_bld
        invdata_bld[table_type] = data_typesubdict
    return invdata_bld


def invdata_build_aggregate_table(
    _data_typesub: dict[str, INVTableData], _aggr_table_list: Sequence[str]
) -> INVTableData:
    """Aggregate selected FTC merger investigations data tables within a given time period."""
    hdr_table_no = _aggr_table_list[0]

    return INVTableData(
        "Industries in Common",
        "Unrestricted on additional evidence",
        np.hstack((
            _data_typesub[hdr_table_no].data_array[:, :-3],
            np.einsum(
                "ijk->jk",
                np.stack([
                    (_data_typesub[t_]).data_array[:, -3:] for t_ in _aggr_table_list
                ]),
            ),
        )),
    )


def _parse_invdata() -> INVData:
    """Parse FTC merger investigations data reports to structured data.

    Returns
    -------
        Immutable dictionary of merger investigations data, keyed to
        reporting period, and including all tables organized by
        Firm Count (number of remaining competitors) and
        by range of HHI and ∆HHI.

    """
    raise ValueError(
        "This function is defined here as documentation.\n"
        "NOTE: License for `pymupdf`, upon which this function depends,"
        " may be incompatible with the MIT license,"
        " under which this pacakge is distributed."
        " Making this fumction operable requires the user to modify"
        " the source code as well as to install an additional package"
        " not distributed with this package or identified as a requirement."
    )
    import pymupdf  # type: ignore

    invdata_docnames = _download_invdata(FID_WORK_DIR)

    invdata: INVData_in = {}

    for invdata_docname in invdata_docnames:
        invdata_pdf_path = FID_WORK_DIR.joinpath(invdata_docname)

        invdata_doc = pymupdf.open(invdata_pdf_path)
        invdata_meta = invdata_doc.metadata
        if invdata_meta["title"] == " ":
            invdata_meta["title"] = ", ".join((
                "Horizontal Merger Investigation Data",
                "Fiscal Years",
                "1996-2005",
            ))

        data_period = "".join(  # line-break here for readability
            re.findall(r"(\d{4}) *(-) *(\d{4})", invdata_meta["title"])[0]
        )

        # Initialize containers for parsed data
        invdata[data_period] = {k: {} for k in TABLE_TYPES}

        for pdf_pg in invdata_doc.pages():
            doc_pg_blocks = pdf_pg.get_text("blocks", sort=False)
            # Across all published reports of FTC investigations data,
            #   sorting lines (PDF page blocks) by the lower coordinates
            #   and then the left coordinates is most effective for
            #   ordering table rows in top-to-bottom order; this doesn't
            #   work for the 1996-2005 data, however, so we resort later
            doc_pg_blocks = sorted([
                (f"{_f[3]:03.0f}{_f[0]:03.0f}{_f[1]:03.0f}{_f[2]:03.0f}", *_f)
                for _f in doc_pg_blocks
                if _f[-1] == 0
            ])

            data_blocks: list[tuple[str]] = [("",)]
            # Pages layouts not the same in all reports
            pg_hdr_strings = (
                "FEDERAL TRADE COMMISSION",
                "HORIZONTAL MERGER INVESTIGATION DATA: FISCAL YEARS 1996 - 2011",
            )
            if len(doc_pg_blocks) > 4:
                tnum = None
                for _pg_blk in doc_pg_blocks:
                    if tnum := TABLE_NO_RE.fullmatch(_pg_blk[-3].strip()):
                        data_blocks = [
                            b_
                            for b_ in doc_pg_blocks
                            if not b_[-3].startswith(pg_hdr_strings)
                            and (
                                b_[-3].strip()
                                not in {"Significant Competitors", "Post Merger HHI"}
                            )
                            and not re.fullmatch(r"\d+", b_[-3].strip())
                        ]
                        break
                if not tnum:
                    continue
                del tnum
            else:
                continue

            _parse_page_blocks(invdata, data_period, data_blocks)

        invdata_doc.close()

    return _mappingproxy_from_mapping(invdata)


def _parse_page_blocks(
    _invdata: INVData_in, _data_period: str, _doc_pg_blocks: Sequence[Sequence[Any]], /
) -> None:
    if _data_period != "1996-2011":
        _parse_table_blocks(_invdata, _data_period, _doc_pg_blocks)
    else:
        test_list = [
            (g, f[-3].strip())
            for g, f in enumerate(_doc_pg_blocks)
            if TABLE_NO_RE.fullmatch(f[-3].strip())
        ]
        # In the 1996-2011 report, there are 2 tables per page
        if len(test_list) == 1:
            table_a_blocks = _doc_pg_blocks
            table_b_blocks: Sequence[Sequence[Any]] = []
        else:
            table_a_blocks, table_b_blocks = (
                _doc_pg_blocks[test_list[0][0] : test_list[1][0]],
                _doc_pg_blocks[test_list[1][0] :],
            )

        for table_i_blocks in table_a_blocks, table_b_blocks:
            if not table_i_blocks:
                continue
            _parse_table_blocks(_invdata, _data_period, table_i_blocks)


def _parse_table_blocks(
    _invdata: INVData_in, _data_period: str, _table_blocks: Sequence[Sequence[str]], /
) -> None:
    invdata_evid_cond = "Unrestricted on additional evidence"
    table_num, table_ser, table_type = _identify_table_type(
        _table_blocks[0][-3].strip()
    )

    if _data_period == "1996-2011":
        invdata_ind_group = (
            _table_blocks[1][-3].split("\n")[1]
            if table_num == "Table 4.8"
            else _table_blocks[2][-3].split("\n")[0]
        )

        if table_ser > 4:
            invdata_evid_cond = (
                _table_blocks[2][-3].split("\n")[1]
                if table_ser in {9, 10}
                else _table_blocks[3][-3].strip()
            )

    elif _data_period == "1996-2005":
        _table_blocks = sorted(_table_blocks, key=itemgetter(6))

        invdata_ind_group = _table_blocks[3][-3].strip()
        if table_ser > 4:
            invdata_evid_cond = _table_blocks[5][-3].strip()

    elif table_ser % 2 == 0:
        invdata_ind_group = _table_blocks[1][-3].split("\n")[2]
        if (evid_cond_teststr := _table_blocks[2][-3].strip()) == "Outcome":
            invdata_evid_cond = "Unrestricted on additional evidence"
        else:
            invdata_evid_cond = evid_cond_teststr

    elif _table_blocks[3][-3].startswith("FTC Horizontal Merger Investigations"):
        invdata_ind_group = _table_blocks[3][-3].split("\n")[2]
        invdata_evid_cond = "Unrestricted on additional evidence"

    else:
        # print(_table_blocks)
        invdata_evid_cond = (
            _table_blocks[1][-3].strip()
            if table_ser == 9
            else _table_blocks[3][-3].strip()
        )
        invdata_ind_group = _table_blocks[4][-3].split("\n")[2]

    if invdata_ind_group == "Pharmaceutical Markets":
        invdata_ind_group = "Pharmaceuticals Markets"

    process_table_func = (
        _process_table_blks_conc_type
        if table_type == TABLE_TYPES[0]
        else _process_table_blks_cnt_type
    )

    table_array = process_table_func(_table_blocks)
    if not isinstance(table_array, np.ndarray) or table_array.dtype != int:
        print(table_num)
        print(_table_blocks)
        raise ValueError

    table_data = INVTableData(invdata_ind_group, invdata_evid_cond, table_array)
    _invdata[_data_period][table_type] |= {table_num: table_data}


def _identify_table_type(_tnstr: str = CONC_TABLE_ALL, /) -> tuple[str, int, str]:
    tnum = _tnstr.split(" ")[1]
    tsub = int(tnum.split(".")[0])
    return _tnstr, tsub, TABLE_TYPES[(tsub + 1) % 2]


def _process_table_blks_conc_type(
    _table_blocks: Sequence[Sequence[str]], /
) -> ArrayBIGINT:
    conc_row_pat = re.compile(r"((?:0|\d,\d{3}) (?:- \d+,\d{3}|\+)|TOTAL)")

    col_titles = tuple(CONC_DELTA_DICT.values())
    col_totals: ArrayBIGINT = np.zeros(len(col_titles), int)
    invdata_array: ArrayBIGINT = np.array(None)

    for tbl_blk in _table_blocks:
        if conc_row_pat.match(_blk_str := tbl_blk[-3]):
            row_list: list[str] = _blk_str.strip().split("\n")
            row_title: str = row_list.pop(0)
            row_key: int = (
                7000 if row_title.startswith("7,000") else CONC_HHI_DICT[row_title]
            )
            row_total = np.array(row_list.pop().replace(",", "").split("/"), int)
            data_row_list: list[list[int]] = []
            while row_list:
                enfd_val, clsd_val = row_list.pop(0).split("/")
                data_row_list += [
                    [
                        row_key,
                        col_titles[len(data_row_list)],
                        int(enfd_val),
                        int(clsd_val),
                        int(enfd_val) + int(clsd_val),
                    ]
                ]
            data_row_array = np.array(data_row_list, int)
            del data_row_list
            # Check row totals
            assert_array_equal(row_total, np.einsum("ij->j", data_row_array[:, 2:4]))

            if row_key == TTL_KEY:
                col_totals = data_row_array
            else:
                invdata_array = (
                    np.vstack((invdata_array, data_row_array))
                    if invdata_array.shape
                    else data_row_array
                )
            del data_row_array
        else:
            continue

    # Check column totals
    for _col_tot in col_totals:
        assert_array_equal(
            _col_tot[2:],  # type: ignore
            np.einsum(
                "ij->j",
                invdata_array[invdata_array[:, 1] == _col_tot[1]][:, 2:],  # type: ignore
            ),
        )

    return invdata_array[
        np.argsort(np.einsum("ij,ij->i", [[100, 1]], invdata_array[:, :2]))
    ]


def _process_table_blks_cnt_type(
    _table_blocks: Sequence[Sequence[str]], /
) -> ArrayBIGINT:
    cnt_row_pat = re.compile(r"(\d+ (?:to \d+|\+)|TOTAL)")

    invdata_array: ArrayBIGINT = np.array(None)
    col_totals: ArrayBIGINT = np.zeros(3, int)  # "enforced", "closed", "total"

    for _tbl_blk in _table_blocks:
        if cnt_row_pat.match(_blk_str := _tbl_blk[-3]):
            row_list_s = _blk_str.strip().replace(",", "").split("\n")
            row_list = np.array([CNT_FCOUNT_DICT[row_list_s[0]], *row_list_s[1:]], int)
            del row_list_s
            if row_list[3] != row_list[1] + row_list[2]:
                raise ValueError(
                    "Total number of investigations does not equal #enforced plus #closed."
                )
            if row_list[0] == TTL_KEY:
                col_totals = row_list
            else:
                invdata_array = (
                    np.vstack((invdata_array, row_list))
                    if invdata_array.shape
                    else row_list
                )
        else:
            continue

    if not np.array_equal(
        np.array(list(col_totals[1:]), int), np.einsum("ij->j", invdata_array[:, 1:])
    ):
        raise ValueError("Column totals don't compute.")

    return invdata_array[np.argsort(invdata_array[:, 0])]


def _download_invdata(_dl_path: Path = FID_WORK_DIR) -> tuple[str, ...]:
    if not _dl_path.is_dir():
        _dl_path.mkdir(parents=True)

    invdata_homepage_urls = (
        "https://www.ftc.gov/reports/horizontal-merger-investigation-data-fiscal-years-1996-2003",
        "https://www.ftc.gov/reports/horizontal-merger-investigation-data-fiscal-years-1996-2005-0",
        "https://www.ftc.gov/reports/horizontal-merger-investigation-data-fiscal-years-1996-2007-0",
        "https://www.ftc.gov/reports/horizontal-merger-investigation-data-fiscal-years-1996-2011",
    )
    invdata_docnames = (
        "040831horizmergersdata96-03.pdf",
        "p035603horizmergerinvestigationdata1996-2005.pdf",
        "081201hsrmergerdata.pdf",
        "130104horizontalmergerreport.pdf",
    )

    if all(
        _dl_path.joinpath(invdata_docname).is_file()
        for invdata_docname in invdata_docnames
    ):
        return invdata_docnames

    invdata_docnames_dl: tuple[str, ...] = ()
    u3pm = urllib3.PoolManager()
    chunk_size_ = 1024 * 1024
    for invdata_homepage_url in invdata_homepage_urls:
        with u3pm.request(
            "GET", invdata_homepage_url, preload_content=False
        ) as _u3handle:
            invdata_soup = BeautifulSoup(_u3handle.data, "html.parser")
            invdata_attrs = [
                (_g.get("title", ""), _g.get("href", ""))
                for _g in invdata_soup.find_all("a")
                if _g.get("title", "") and _g.get("href", "").endswith(".pdf")
            ]
        for invdata_attr in invdata_attrs:
            invdata_docname, invdata_link = invdata_attr
            invdata_docnames_dl += (invdata_docname,)
            with (
                u3pm.request(
                    "GET", f"https://www.ftc.gov/{invdata_link}", preload_content=False
                ) as _urlopen_handle,
                _dl_path.joinpath(invdata_docname).open("wb") as invdata_fh,
            ):
                while True:
                    data = _urlopen_handle.read(chunk_size_)
                    if not data:
                        break
                    invdata_fh.write(data)

    return invdata_docnames_dl


if __name__ == "__main__":
    print(
        "This module defines functions for downloading and preparing FTC merger investigations data for further analysis."
    )
