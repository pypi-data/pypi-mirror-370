"""Functions to parse margin data compiled by Prof. Aswath Damodaran, Stern School of Business, NYU.

Provides :func:`margin_data_resampler` for generating margin data
from an estimated Gaussian KDE from the source (margin) data.

Data are downloaded or reused from a local copy, on demand.

For terms of use of Prof. Damodaran's data, please see:
https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datahistory.html

Notes
-----
Prof. Damodaran notes that the data construction may not be
consistent from iteration to iteration. He also notes that,
"the best use for my data is in real time corporate financial analysis
and valuation." Here, gross margin data compiled by Prof. Damodaran are
optionally used to model the distribution of price-cost margin
across firms that antitrust enforcement agencies are likely to review in
merger enforcement investigations over a multi-year span. The
implicit assumption is that refinements in source-data construction from
iteration to iteration do not result in inconsistent estimates of
the empirical distribution of margins estimated using
a Gaussian kernel density estimator (KDE).

Second, other procedures included in this package allow the researcher to
generate margins for a single firm and impute margins of other firms in
a model relevant antitrust market based on FOCs for profit maximization by
firms facing MNL demand. In that exercise, the distribution of
inferred margins does not follow the empirical distribution estimated
from the source data, due to restrictions resulting from the distribution of
generated market shares across firms and the feasibility condition that
price-cost margins fall in the interval :math:`[0, 1]`.

"""

import datetime
import os
import re
import zipfile
from pathlib import Path
from types import MappingProxyType

import certifi
import numpy as np
import urllib3
from bs4 import BeautifulSoup
from joblib import Parallel, delayed, parallel_config  # type: ignore
from numpy.random import Generator, SeedSequence
from python_calamine import CalamineWorkbook
from scipy import stats  # type: ignore

from .. import NTHREADS, VERSION, ArrayDouble, this_yaml  # noqa: TID252
from .. import WORK_DIR as PKG_WORK_DIR  # noqa: TID252
from . import DEFAULT_BITGENERATOR, _mappingproxy_from_mapping

__version__ = VERSION

WORK_DIR = globals().get("WORK_DIR", PKG_WORK_DIR)
"""Redefined, in case the user defines WORK_DIR between module imports."""

MGNDATA_ARCHIVE_PATH = WORK_DIR / "damodaran_margin_data_serialized.zip"

type DamodaranMarginData = MappingProxyType[
    str, MappingProxyType[str, MappingProxyType[str, float | int]]
]

FINANCIAL_INDUSTRIES = {
    _i.upper()
    for _i in (
        "Bank (Money Center)",
        "Banks (Regional)",
        "Brokerage & Investment Banking",
        "Financial Svcs. (Non-bank & Insurance)",
        "Insurance (General)",
        "Insurance (Life)",
        "Insurance (Prop/Cas.)",
        "Investments & Asset Management",
        "R.E.I.T.",
        "Retail (REITs)",
        "Reinsurance",
    )
}


def margin_data_resampler(
    _dist_parms: ArrayDouble,
    /,
    *,
    sample_size: int | tuple[int, ...],
    seed_sequence: SeedSequence | None = None,
    nthreads: int = NTHREADS,
) -> ArrayDouble:
    """Generate draws from the empirical distribution based on Prof. Damodaran's margin data.

    The empirical distribution is estimated using a Gaussian KDE; the bandwidth
    selected using Silverman's rule is narrowed to reflect that the margin data
    are multimodal. Margins for firms in finance, investment, insurance,
    reinsurance, and REITs are excluded from the sample used to estimate the
    empirical distribution.

    Parameters
    ----------
    _dist_parms
        Array of margins and firm counts extracted from Prof. Damodaran's margin data

    sample_size
        Number of draws; if tuple, (number of draws, number of columns)

    seed_sequence
        SeedSequence for seeding random-number generator when results
        are to be repeatable

    nthreads
        Number of threads to use in generating margin data.

    Returns
    -------
        Array of margin values

    """
    _dist_parms = margin_data_builder()[0] if _dist_parms is None else _dist_parms

    _seed = seed_sequence or SeedSequence(pool_size=8)

    _x, _w = _dist_parms[:, 0], _dist_parms[:, 1]

    margin_kde = stats.gaussian_kde(_x, weights=_w, bw_method="silverman")
    # preserve multiplicity of modes:
    margin_kde.set_bandwidth(bw_method=margin_kde.factor / 3.0)

    if isinstance(sample_size, int):
        ret_array: ArrayDouble = margin_kde.resample(
            sample_size, seed=Generator(DEFAULT_BITGENERATOR(_seed))
        ).T

    elif isinstance(sample_size, tuple) and len(sample_size) == 2:
        ret_array = np.empty(sample_size, float)

        _ssz, _ncol = sample_size
        with parallel_config(
            backend="threading", n_jobs=min(nthreads, _ncol), return_as="generator"
        ):
            dat_list = Parallel()(
                delayed(margin_kde.resample)(
                    _ssz, seed=Generator(DEFAULT_BITGENERATOR(_col_seed))
                )
                for _col_seed in _seed.spawn(_ncol)
            )

        for _i in range(_ncol):
            ret_array[:, _i] = dat_list[_i][0]
    else:
        raise ValueError(f"Invalid sample size: {sample_size!r}")

    return ret_array


def margin_data_builder(
    _margin_data_dict: DamodaranMarginData | None = None,
) -> tuple[ArrayDouble, ArrayDouble]:
    """Derive average firm-counts and gross-margins by industry from source data."""
    _margin_data_dict = (
        margin_data_getter() if _margin_data_dict is None else _margin_data_dict
    )
    dmd_keys = set()
    for _k, _v in _margin_data_dict.items():
        dmd_keys.update(set(_v.keys()))
    dmd_keys = sorted(dmd_keys)

    dist_parms = np.array([np.nan, np.nan], dtype=float)
    for _sk in dmd_keys:
        if _sk in FINANCIAL_INDUSTRIES or _sk.startswith("TOTAL"):
            continue

        _missing = {"GROSS MARGIN": 0.0, "NUMBER OF FIRMS": 0.0}
        gm, fc = zip(*[
            [_v.get(_sk, _missing)[_f] for _f in _missing]
            for _v in _margin_data_dict.values()
        ])

        average_margin, firm_count = np.array(gm, float), np.array(fc, int)
        # print(firm_count, average_margin)
        dist_parms = np.vstack((
            dist_parms,
            np.array((
                np.average(
                    average_margin, weights=(average_margin > 0) * (firm_count > 0)
                ),
                np.average(firm_count, weights=(average_margin > 0) * (firm_count > 0)),
            )),
        ))

    dist_parms = dist_parms[1:, :]

    obs_, wts_ = (dist_parms[:, _f] for _f in range(2))

    avg_gm, num_firms = np.average(obs_, weights=wts_, returned=True)
    std_gm = np.sqrt(
        np.average((obs_ - avg_gm) ** 2, weights=wts_)
        * num_firms
        * len(obs_)
        / ((num_firms - len(obs_)) * (len(obs_) - 1))
    )

    return dist_parms, np.array([avg_gm, std_gm, obs_.min(), obs_.max()], float)


def margin_data_getter(
    *, data_archive_path: Path | None = None, data_download_flag: bool = False
) -> DamodaranMarginData:
    """Download and parse Prof.Damodaran's margin data."""
    data_archive_path = (
        MGNDATA_ARCHIVE_PATH if data_archive_path is None else data_archive_path
    )
    if data_archive_path.is_file() and not data_download_flag:
        with zipfile.ZipFile(data_archive_path) as _yzp:
            margin_data_dict: DamodaranMarginData = this_yaml.load(
                _yzp.read(data_archive_path.with_suffix(".yaml").name)
            )
        return margin_data_dict

    # Get workbooks from source
    elif data_download_flag or not list(data_archive_path.glob("margin*.xls")):
        margin_data_downloader()

    #  Parse workbooks and save margin data dictionary
    margin_data_: dict[str, dict[str, MappingProxyType[str, float]]] = {}
    for _p in (WORK_DIR / "damodaran_margin_data_archive").iterdir():
        xl_wbk = CalamineWorkbook.from_path(_p)
        xl_wks = xl_wbk.get_sheet_by_index(
            0
            if (_p.stem.startswith("margin") and _p.stem[-2:] in {"17", "18", "19"})
            else 1
        ).to_python()
        if xl_wks[8][2] != "Gross Margin":
            raise ValueError("Worksheet does not match expected layout.")
        row_keys: list[str] = [_c.upper() for _c in xl_wks[8][1:]]  # type: ignore

        _u = xl_wks[0][1]
        if not isinstance(_u, datetime.date):
            print(_u)
            print(xl_wks[:8])
            raise ValueError("Worksheet does not match expected layout.")
        update: str = _u.isoformat()[:10]

        margin_data_annual = margin_data_.setdefault(update, {})
        for xl_row in xl_wks[9:]:
            row_key = _s.upper() if isinstance((_s := xl_row[0]), str) else ""

            if not row_key or row_key.startswith("TOTAL"):
                continue
            else:
                xl_row[1] = int(xl_row[1])  # type: ignore
                margin_data_annual |= MappingProxyType({
                    row_key: MappingProxyType(
                        dict(zip(row_keys, xl_row[1:], strict=True))  # type: ignore
                    )
                })

    margin_data_map: DamodaranMarginData = _mappingproxy_from_mapping(margin_data_)
    with (
        zipfile.ZipFile(data_archive_path, "w") as _yzp,
        _yzp.open(f"{data_archive_path.stem}.yaml", "w") as _yfh,
    ):
        this_yaml.dump(margin_data_map, _yfh)

    return margin_data_map


def margin_data_downloader() -> None:
    """Download Prof.Damodaran's margin data."""
    _u3pm = urllib3.PoolManager(ca_certs=certifi.where())
    _data_source_url = "https://pages.stern.nyu.edu/~adamodar/pc/datasets/"
    _archive_source_url = "https://pages.stern.nyu.edu/~adamodar/pc/archives/"

    dest_dir = WORK_DIR / "damodaran_margin_data_archive"
    if not dest_dir.is_dir():
        dest_dir.mkdir()

    # Get current-year margin data
    workbook_name = "margin.xls"
    workbook_path = dest_dir / workbook_name
    if workbook_path.is_file():
        workbook_path.unlink()

    u3pm = urllib3.PoolManager(ca_certs=certifi.where())
    download_file(u3pm, f"{_data_source_url}{workbook_name}", workbook_path)

    # Get archived margin data
    workbook_re = re.compile(r"margin(\d{2}).xls")
    archive_html = _u3pm.request("GET", _archive_source_url).data.decode("utf-8")
    archive_tree = BeautifulSoup(archive_html, "lxml")
    for tag in archive_tree.find_all("a"):
        if (
            (_r := workbook_re.fullmatch(_w := tag.get("href", "")))
            and int(_r[1]) > 16
            and int(_r[1]) not in {98, 99}
        ):
            _url, _path = f"{_archive_source_url}{_w}", dest_dir / _w
            if _path.is_file():
                _path.unlink()

            download_file(_u3pm, _url, _path)


def download_file(_u3pm: urllib3.PoolManager, _url: str, _path: Path) -> None:
    """Download a a binary file from URL to filesystem path."""
    chunk_size_ = 1024 * 1024
    with (
        _u3pm.request("GET", _url, preload_content=False) as _uh,
        _path.open("wb") as _fh,
    ):
        while True:
            data_ = _uh.read(chunk_size_)
            if not data_:
                break
            _fh.write(data_)
    os.utime(
        _path,
        times=(
            (
                _t := datetime.datetime.strptime(
                    _uh.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
                )
                .astimezone(datetime.UTC)
                .timestamp()
            ),
            _t,
        ),
    )

    print(f"Downloaded {_url} to {_path}.")
