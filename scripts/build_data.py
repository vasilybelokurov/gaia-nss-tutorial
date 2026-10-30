"""Build the data files of the tutorial from WSDB; they are attached to a GitHub release, not stored in git.

Usage:  python scripts/build_data.py [name ...|all]   (writes data_build/<name>.parquet and data/MANIFEST.json)

Needs access to WSDB (Cambridge) through sqlutilpy. Every query of a large table goes through an index (q3c or
source_id), and its plan is checked with EXPLAIN before it runs (a sequential scan of gaia_source is refused). The
same public tables are in the Gaia archive (https://gea.esac.esa.int/archive/), so the SQL below documents each
selection exactly.

Missing values are NaN (integer columns: -1).
"""
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sqlutilpy as sqlutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data_build"
MANIFEST = ROOT / "data" / "MANIFEST.json"

# gaia_source columns that carry binarity information, with photometry and astrometry
SRC = """g.source_id, g.ra, g.dec, g.l, g.b, g.parallax, g.parallax_error, g.pmra, g.pmra_error, g.pmdec, g.pmdec_error,
         g.phot_g_mean_mag, g.bp_rp, g.phot_bp_rp_excess_factor, g.ruwe, g.astrometric_excess_noise,
         g.astrometric_excess_noise_sig, g.astrometric_n_good_obs_al, g.astrometric_params_solved, g.visibility_periods_used,
         g.ipd_gof_harmonic_amplitude, g.ipd_frac_multi_peak, g.ipd_frac_odd_win, g.duplicated_source, g.non_single_star,
         g.phot_variable_flag, g.radial_velocity, g.radial_velocity_error, g.rv_method_used, g.rv_nb_transits,
         g.rv_chisq_pvalue, g.rv_renormalised_gof, g.rv_amplitude_robust, g.grvs_mag, g.rv_template_teff, g.vbroad"""
# orbital elements and quality of the two-body solutions (corr_vec, the correlation matrix, is kept as a list)
TBO = """n.nss_solution_type, n.ra AS nss_ra, n.parallax AS nss_parallax, n.parallax_error AS nss_parallax_error,
         n.pmra AS nss_pmra, n.pmdec AS nss_pmdec, n.a_thiele_innes, n.a_thiele_innes_error, n.b_thiele_innes,
         n.b_thiele_innes_error, n.f_thiele_innes, n.f_thiele_innes_error, n.g_thiele_innes, n.g_thiele_innes_error,
         n.c_thiele_innes, n.c_thiele_innes_error, n.h_thiele_innes, n.h_thiele_innes_error, n.period, n.period_error,
         n.t_periastron, n.t_periastron_error, n.eccentricity, n.eccentricity_error, n.center_of_mass_velocity,
         n.center_of_mass_velocity_error, n.semi_amplitude_primary, n.semi_amplitude_primary_error,
         n.semi_amplitude_secondary, n.semi_amplitude_secondary_error, n.mass_ratio, n.mass_ratio_error,
         n.inclination, n.arg_periastron, n.arg_periastron_error, n.astrometric_n_good_obs_al AS nss_n_good_obs_al,
         n.rv_n_good_obs_primary, n.rv_n_good_obs_secondary, n.phot_g_n_good_obs, n.bit_index, n.obj_func,
         n.goodness_of_fit, n.efficiency, n.significance, n.flags, n.conf_spectro_period, n.g_luminosity_ratio,
         n.astrometric_jitter, n.corr_vec"""
ACC = """n.nss_solution_type, n.parallax AS nss_parallax, n.parallax_error AS nss_parallax_error, n.pmra AS nss_pmra,
         n.pmdec AS nss_pmdec, n.accel_ra, n.accel_ra_error, n.accel_dec, n.accel_dec_error, n.deriv_accel_ra,
         n.deriv_accel_ra_error, n.deriv_accel_dec, n.deriv_accel_dec_error, n.astrometric_n_good_obs_al AS nss_n_good_obs_al,
         n.goodness_of_fit, n.significance, n.flags"""
# The 12 pre-release source_ids, which (for this curated sample, not in general) are also DR3 source_ids
DR4_IDS = (2237987199365376, 60730287810150016, 10973744521070720, 4181040337841125632, 3926186255616949504,
           435469040545191680, 1663617687609809280, 2309425390592896, 20694084440761600, 3937211745905473024,
           1457486023639239296, 4318465066420528000)
QUERIES = {
    # every two-body solution, with the gaia_source columns of its star; in 64 source_id ranges (run in parallel)
    "nss_two_body": [f"SELECT {TBO}, {SRC} FROM gaia_dr3.nss_two_body_orbit n JOIN gaia_dr3.gaia_source g USING (source_id) "
                     f"WHERE n.source_id >= {k * 2**57} AND n.source_id < {(k + 1) * 2**57}" for k in range(64)],
    # every accelerating astrometric solution (7- and 9-parameter models)
    "nss_acceleration": [f"SELECT {ACC}, {SRC} FROM gaia_dr3.nss_acceleration_astro n JOIN gaia_dr3.gaia_source g USING (source_id) "
                         f"WHERE n.source_id >= {k * 2**57} AND n.source_id < {(k + 1) * 2**57}" for k in range(64)],
    # trend-only spectroscopic solutions and variability-induced movers: types and fit quality only
    "nss_other": ["""SELECT 'nss_non_linear_spectro' AS nss_table, n.source_id, n.nss_solution_type, n.goodness_of_fit,
                     g.phot_g_mean_mag, g.bp_rp, g.parallax, g.ruwe
                     FROM gaia_dr3.nss_non_linear_spectro n JOIN gaia_dr3.gaia_source g USING (source_id)
                     UNION ALL
                     SELECT 'nss_vim_fl', n.source_id, n.nss_solution_type, n.goodness_of_fit, g.phot_g_mean_mag, g.bp_rp,
                     g.parallax, g.ruwe FROM gaia_dr3.nss_vim_fl n JOIN gaia_dr3.gaia_source g USING (source_id)"""],
    # APOGEE DR17 stars with >= 3 visits and S/N > 50 (duplicates removed: EXTRATARG bit 4), with the RV columns of
    # their Gaia DR3 source (EDR3 and DR3 source_id are the same); the LATERAL join forces one index lookup per star
    "apogee_gaia": ["""WITH a AS MATERIALIZED (SELECT apogee_id, gaiaedr3_source_id AS source_id, nvisits, snr, vscatter,
                       vhelio_avg, teff, logg, m_h, vsini, aspcapflag, starflag FROM apogee_dr17.allstar
                       WHERE nvisits >= 3 AND snr > 50 AND gaiaedr3_source_id > 0 AND vscatter IS NOT NULL
                       AND gaiaedr3_phot_g_mean_mag < 13 AND (extratarg & 16) = 0)
                       SELECT a.*, g.* FROM a CROSS JOIN LATERAL (SELECT g.phot_g_mean_mag, g.bp_rp, g.parallax, g.ruwe,
                       g.radial_velocity, g.radial_velocity_error, g.rv_method_used, g.rv_nb_transits, g.rv_chisq_pvalue,
                       g.rv_renormalised_gof, g.rv_amplitude_robust, g.rv_time_duration, g.grvs_mag, g.rv_template_teff,
                       g.vbroad, g.non_single_star FROM gaia_dr3.gaia_source g WHERE g.source_id = a.source_id) g"""],
    # the DR3 catalogue entries of the 12 DR4 pre-release sources, and their DR3 orbits if any (at most one each),
    # for comparison with the DR4 epoch data (corr_vec dropped: sqlutilpy cannot read a NULL array)
    "dr4_prerelease_dr3": [f"SELECT {SRC}, g.nu_eff_used_in_astrometry, g.pseudocolour, {TBO.replace(", n.corr_vec", "")} FROM gaia_dr3.gaia_source g "
                           f"LEFT JOIN gaia_dr3.nss_two_body_orbit n USING (source_id) WHERE g.source_id IN {DR4_IDS}"],
    # PARSEC isochrones in Gaia bands (WSDB isochrones.gaia_1804): [Fe/H] = 0, ages 1, 3.16 and 10 Gyr, for primary masses
    "isochrones_gaia_solar": ["""SELECT age, feh, mini, label, gmag, g_bpmag, g_rpmag FROM isochrones.gaia_1804
                                 WHERE feh = 0 AND age IN (1e9, 3.16e9, 1e10) ORDER BY age, mini"""],
}
# The Gaia DR4 pre-release of epoch astrometry for 12 sources (June 2026), https://www.cosmos.esa.int/web/gaia/dr4-prerelease
DR4_PRE = "https://anonftp.cosmos.esa.int/pub/GAIA_PUBLIC_DATA/Gaia_DR4/dr4-prerelease/gaia-dr4-prerelease-epoch-astrometry_2026-06-26.zip"
# Chunked scans of gaia_source by source_id ranges (2**51 wide: the 3072 nside-16 HEALPix pixels), for selections
# that no index supports (e.g. on parallax). name: (selection, columns)
SCANS = {
    # stars within 100 pc with a well-measured parallax: the binarity indicators of a volume-limited sample
    "gcns100": ("g.parallax > 10 AND g.parallax_over_error > 5", SRC),
}


def check_plan(q):
    """Refuse a query whose plan sequentially scans gaia_source (i.e. misses the source_id index)."""
    plan = "\n".join(r[0] for r in zip(*sqlutil.get("EXPLAIN " + q, batched=False)))
    if "Seq Scan on gaia_source" in plan:
        raise RuntimeError("plan contains a sequential scan of gaia_source:\n" + plan)


def save(name, df, queries, shrink=True):
    OUT.mkdir(exist_ok=True)
    for c in df.columns if shrink else []:    # float32 for everything except positions and times; sentinels -> NaN
        if df[c].dtype.kind == "f":
            v = df[c].to_numpy()
            keep64 = c in ("ra", "dec", "ra0", "dec0", "nss_ra", "t_periastron", "period")
            df[c] = v if keep64 else v.astype(np.float32)
    path, tmp = OUT / f"{name}.parquet", OUT / f"{name}.parquet.tmp"
    df.to_parquet(tmp, compression="zstd", index=False)
    tmp.replace(path)                          # atomic: an interrupted run never leaves a partial file
    import fcntl
    lock = open(OUT / ".manifest.lock", "w")
    fcntl.flock(lock, fcntl.LOCK_EX)           # several builds may run at once: update the manifest one at a time
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    man[name] = {"rows": len(df), "bytes": path.stat().st_size,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                 "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "columns": list(df.columns), "queries": [" ".join(q.split()) for q in queries]}
    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(dict(sorted(man.items())), indent=1))
    print(f"{name}: {len(df):,} rows, {path.stat().st_size / 1e6:.1f} MB")


def get(q):
    """Run a query; return a DataFrame (integer NULLs -> -1, as sqlutilpy needs a value)."""
    return pd.DataFrame(sqlutil.get(q, asDict=True, intNullVal=-1))


def build(name):
    t = time.time()
    if name in SCANS:
        return build_scan(name)
    if name == "dr4_prerelease_epoch_astrometry":
        return build_dr4_prerelease(name)
    from concurrent.futures import ThreadPoolExecutor
    queries = QUERIES[name]
    for q in queries:
        check_plan(q)
    with ThreadPoolExecutor(6) as ex:          # several queries at once: the index lookups are I/O bound on the server
        parts = list(ex.map(get, queries))
    df = pd.concat([p for p in parts if len(p)], ignore_index=True)
    print(f"  query time {time.time() - t:.1f} s")
    return save(name, df, queries)


def build_scan(name, workers=4):
    """gaia_source in 3072 source_id chunks, `workers` at a time, resumable (partial results are pickled)."""
    from concurrent.futures import ThreadPoolExecutor
    where, cols = SCANS[name]
    step = 2**51
    q = f"SELECT {cols} FROM gaia_dr3.gaia_source g WHERE g.source_id >= %s AND g.source_id < %s AND {where}"
    check_plan(q % (0, step))
    partial = OUT / f"{name}.partial.pkl"
    done = pd.read_pickle(partial) if partial.exists() else {}
    todo = [k for k in range(3072) if k not in done]

    def run(k):
        return k, pd.DataFrame(sqlutil.get(q, (k * step, (k + 1) * step), asDict=True, intNullVal=-1))

    OUT.mkdir(exist_ok=True)
    with ThreadPoolExecutor(workers) as ex:
        for i, (k, df) in enumerate(ex.map(run, todo)):
            done[k] = df
            if i % 100 == 99 or len(done) == 3072:
                pd.to_pickle(done, partial)
                print(f"  {len(done)}/3072 chunks", flush=True)
    df = pd.concat(done.values(), ignore_index=True).sort_values("source_id", ignore_index=True)
    save(name, df, [q.replace("%s", "{lo}", 1).replace("%s", "{hi}", 1) + "  -- for lo = k * 2**51, hi = lo + 2**51, k = 0..3071"])
    partial.unlink()


def build_dr4_prerelease(name):
    """Download the DR4 pre-release VOTable and write one row per CCD observation (times stay int64 nanoseconds)."""
    import io
    import urllib.request
    import zipfile
    from astropy.io.votable import parse
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(DR4_PRE).read()))
    xml = [n for n in z.namelist() if n.endswith(".xml")][0]
    t = parse(io.BytesIO(z.read(xml))).get_first_table().to_table()
    def filled(a):                             # masked values -> NaN (floats), -1 (integers), False (booleans)
        a = np.ma.asarray(a)
        return a.filled({"f": np.nan, "b": False}.get(a.dtype.kind, -1))

    # every column is kept at its native precision; per-transit scalars are repeated on each CCD row, and the two
    # across-scan centroid arrays, empty in this release, are dropped
    arrays = [c for c in t.colnames if t[c].dtype == object and len(t[c][0]) > 0]
    scalars = [c for c in t.colnames if t[c].dtype != object]
    rows = []
    for r in t:
        n = len(r["centroid_pos_al"])
        assert all(len(r[c]) == n for c in arrays)
        rows.append(pd.DataFrame({**{c: [filled(r[c])[()]] * n for c in scalars}, "ccd": np.arange(n),
                                  **{c: filled(r[c]) for c in arrays}}))
    df = pd.concat(rows, ignore_index=True)
    save(name, df, [DR4_PRE + f"  ({xml}; per-CCD arrays exploded into rows)"], shrink=False)


ALL = list(QUERIES) + list(SCANS) + ["dr4_prerelease_epoch_astrometry"]

if __name__ == "__main__":
    names = sys.argv[1:] or ["all"]
    for n in (ALL if names == ["all"] else names):
        build(n)
