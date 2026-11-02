# Non-single stars in Gaia

A step-by-step Python tutorial on stellar companions in Gaia data — astrometric, spectroscopic and photometric
binaries — using the Gaia DR3 non-single-star catalogue and the binarity indicators of `gaia_source`, and preparing for
Gaia DR4 with the pre-released DR4 epoch astrometry.

**Read online:** https://vasilybelokurov.github.io/gaia-nss-tutorial/

Status: in development. Chapters 0–5 (release v0.1) are built; the plan, including later chapters, is in
[STRUCTURE.md](STRUCTURE.md).

## Run in the browser

Open any notebook in Google Colab, e.g.
[Chapter 1 — The photocentre wobble](https://colab.research.google.com/github/vasilybelokurov/gaia-nss-tutorial/blob/main/notebooks/01_photocentre_wobble.ipynb).
Each notebook downloads the small data files it needs from this repository's
[`data-v0.2` release](https://github.com/vasilybelokurov/gaia-nss-tutorial/releases/tag/data-v0.2)
and checks their SHA-256 checksums. Published assets stay unchanged; future data changes get new filenames
and a new release, as described in [data/README.md](data/README.md).

## Run locally

Use Python 3.13, as in CI. The scientific package versions in `requirements.txt` are pinned;
Colab uses its own preinstalled environment.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt jupyterlab
jupyter lab notebooks/
```

## Check and build the tutorial

From the repository root, in the same environment:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -q
python -m pytest tests/ --nbmake notebooks/ --nbmake-timeout=1800 --overwrite
jupyter-book build . -W -n --keep-going
```

The first check runs offline, with tiny temporary files and mocked database calls. The notebook check
downloads any missing data (about 426 MB for all files) and executes each chapter in a fresh kernel.
Chapter 5 includes orbit searches and bootstraps; allow up to 30 minutes per notebook.
`--overwrite` keeps the figures for the book, whose own execution is disabled. Before committing notebooks,
clear their outputs in Jupyter. CI uses the same dependencies and execution/build commands.

A separate [transit-bootstrap check](validation/README.md) injects a known orbit into Gaia-4's sampling and
measures interval coverage with independent and correlated transit noise. Run it with
`python scripts/check_transit_bootstrap.py`; it adds no runtime to the student notebooks or routine CI.

## Data

The data files are extracted from Gaia DR3 and APOGEE DR17 with `scripts/build_data.py`, which records the exact SQL
(or source URL) of each file in `data/MANIFEST.json`. Sources, licences and acknowledgements:
[data/README.md](data/README.md).

To rebuild extracts, install `requirements-build.txt` and configure your existing WSDB access for `sqlutilpy`,
then run, for example, `python scripts/build_data.py nss_two_body`. This writes to `data_build/` and updates
the manifest; it does not publish files. Students do not need these dependencies or database access.

## Licence

Tutorial code and text: MIT (see [LICENSE](LICENSE)). Data files: see [data/README.md](data/README.md).
