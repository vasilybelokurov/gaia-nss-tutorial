"""Small injection–recovery check of Chapter 5's local transit-bootstrap uncertainties.

Run from any directory: python scripts/check_transit_bootstrap.py
Outputs go to _build/bootstrap_validation; no database access is needed.
"""
import argparse
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks/05_dr4_epoch_astrometry.ipynb"
PARAMETERS = ["P", "e", "a0", "parallax", "fM"]


def notebook_functions():
    """Load only the required definitions, without running the notebook's plots or fits.

    Reading the AST keeps this check tied to the actual teaching code, without a second fitter to maintain.
    """
    names = {"load", "design", "kepler_xy", "fit", "chi2", "refine", "campbell", "elements",
             "bootstrap", "spread", "mass_function"}
    env = dict(np=np, pd=pd, minimize=minimize, Path=Path, hashlib=hashlib, urllib=urllib,
               MANIFEST=json.loads((ROOT / "data/MANIFEST.json").read_text()))
    found = set()
    for cell in json.loads(NOTEBOOK.read_text())["cells"]:
        if cell["cell_type"] != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                key = node.targets[0].id
                if key in {"JD_REF", "COLOUR_PRIOR", "DATA_URL"}:
                    env[key] = ast.literal_eval(node.value)
            if isinstance(node, ast.FunctionDef) and node.name in names:
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(NOTEBOOK), "exec"), env)
                found.add(node.name)
    assert found == names, f"notebook definitions changed: missing {names - found}"
    return env


def wilson(k, n):
    """95% binomial interval: show the sampling uncertainty of the measured coverage."""
    z, p = 1.96, k / n
    centre = (p + z*z / (2*n)) / (1 + z*z/n)
    half = z * np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return centre - half, centre + half


def run(trials, n_boot, seed, out):
    nb = notebook_functions()
    raw = nb["load"]("dr4_prerelease_epoch_astrometry", cache=ROOT / "notebooks/data")
    s = raw[(raw.source_id == 1457486023639239296) & raw.used_by_agis_al].copy()
    s["t"] = (2455197.5 + (s.obs_time_tcb + s.obs_time_bary_corr.astype(float)) / 86400e9
              - nb["JD_REF"]) / 365.25
    # A strong, well-sampled synthetic orbit; these are not estimates for Gaia-4.
    q_true = np.array([600 / 365.25, 0.3, 0.2])                  # P [yr], e, Tp [yr from J2017.5]
    p_true = np.array([0, 0, 10, 5, -3, 0, 0.80, 0.12, -0.40, 0.60])  # source + A,F,B,G [mas]
    signal = nb["design"](s, tuple(q_true)) @ p_true
    a0 = nb["campbell"](p_true[6], p_true[8], p_true[7], p_true[9])[0]
    truth = dict(P=600.0, e=0.3, a0=a0, parallax=10.0)
    truth["fM"] = nb["mass_function"](truth)
    # First check that the noiseless injection recovers the known inputs to relative tolerance 1e-6.
    s["centroid_pos_al"] = signal
    exact = nb["elements"](s, nb["refine"](s, q_true))
    np.testing.assert_allclose([exact[k] for k in PARAMETERS[:-1]],
                               [truth[k] for k in PARAMETERS[:-1]], rtol=1e-6, atol=1e-8)
    transit, ids = pd.factorize(s.transit_id)
    sigma = s.centroid_pos_error_al.to_numpy()
    # A deliberately simple correlated error: one Gaussian offset per transit, of size median CCD sigma.
    jitter = float(np.median(sigma))
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for case, shared_sigma in [("independent", 0.0), ("shared transit noise", jitter)]:
        # Matched random draws make the comparison less noisy; trials within each case remain independent.
        rng = np.random.default_rng(seed)
        for trial in range(trials):
            noise = rng.normal(size=len(s)) * sigma + shared_sigma * rng.normal(size=len(ids))[transit]
            s["centroid_pos_al"] = signal + noise
            q = nb["refine"](s, q_true.copy())                # local uncertainty check, conditional on this basin
            el = nb["elements"](s, q)
            boot = nb["bootstrap"](s, q, n=n_boot, seed=seed + trial + 1)
            el["fM"] = nb["mass_function"](el)
            boot["fM"] = nb["mass_function"](boot)
            assert np.isfinite(boot.to_numpy()).all() and boot.P.gt(0).all() and boot.e.between(0, 0.99).all()
            spread = nb["spread"](boot, el)
            for k in PARAMETERS:
                assert np.isfinite(el[k]) and np.isfinite(spread[k]) and spread[k] > 0
                rows.append(dict(case=case, trial=trial, parameter=k, truth=truth[k], estimate=el[k],
                                 sigma=spread[k], pull=(el[k] - truth[k]) / spread[k]))
            print(f"{case}: {trial + 1}/{trials}", flush=True)
            pd.DataFrame(rows).to_csv(out / "recoveries.csv", index=False)

    results = pd.DataFrame(rows)
    summary = []
    for (case, k), g in results.groupby(["case", "parameter"], sort=False):
        # This matches the notebook's reported estimate +/- half the bootstrap 16–84% range.
        hits = int((g.pull.abs() <= 1).sum())
        lo, hi = wilson(hits, len(g))
        summary.append(dict(case=case, parameter=k, truth=truth[k], coverage=hits / len(g),
                            coverage_lo=lo, coverage_hi=hi, mean_pull=g.pull.mean(),
                            mean_pull_se=g.pull.std(ddof=1) / np.sqrt(len(g)),
                            pull_sd=g.pull.std(ddof=1), median_sigma=g.sigma.median()))
    summary = pd.DataFrame(summary)
    summary.to_csv(out / "summary.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    for j, (case, g) in enumerate(summary.groupby("case", sort=False)):
        g = g.set_index("parameter").loc[PARAMETERS]
        x = np.arange(len(g)) + (j - 0.5) * 0.15
        axes[0].errorbar(x, g.mean_pull, yerr=g.mean_pull_se, fmt="o", label=case)
        axes[1].errorbar(x, g.coverage, yerr=[g.coverage - g.coverage_lo, g.coverage_hi - g.coverage],
                         fmt="o", label=case)
    for ax in axes:
        ax.set_xticks(range(len(PARAMETERS)), ["P", "e", "$a_0$", "parallax", "$f_M$"])
    axes[0].axhline(0, color="k", ls="--", lw=1)
    axes[0].set(ylabel="mean (estimate − truth) / bootstrap sigma", title="Recovery bias (±1 standard error)")
    axes[1].axhline(0.6827, color="k", ls="--", lw=1, label="nominal Gaussian 68.3%")
    axes[1].set(ylim=(0, 1), ylabel="fraction with |estimate − truth| ≤ sigma",
                title="Coverage (95% binomial intervals)")
    axes[1].legend(fontsize=8, loc="lower left")
    fig.suptitle(f"600-day synthetic orbit · Gaia-4 sampling · {trials} trials × {n_boot} resamples per noise case")
    for suffix in ("png", "pdf"):
        fig.savefig(out / f"coverage.{suffix}", dpi=160)
    plt.close(fig)
    metadata = dict(trials=trials, bootstrap=n_boot, seed=seed, observations=len(s), transits=len(ids),
                    shared_sigma_mas=jitter, q_true=q_true.tolist(), p_true=p_true.tolist(),
                    notebook_sha256=hashlib.sha256(NOTEBOOK.read_bytes()).hexdigest(),
                    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    data_sha256=nb["MANIFEST"]["dr4_prerelease_epoch_astrometry"]["sha256"],
                    versions={p: importlib.metadata.version(p) for p in ("numpy", "scipy", "pandas", "matplotlib")})
    (out / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(summary.round(4).to_string(index=False))
    print(f"Saved results and Figure V.1 to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--bootstrap", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20261102)
    parser.add_argument("--out", type=Path, default=ROOT / "_build/bootstrap_validation")
    args = parser.parse_args()
    if args.trials < 2 or args.bootstrap < 10:
        parser.error("use at least 2 trials and 10 bootstrap resamples")
    run(args.trials, args.bootstrap, args.seed, args.out)
