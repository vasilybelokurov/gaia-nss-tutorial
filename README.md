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
and checks their SHA-256 checksums. Files are only ever added to the release; a changed selection gets a new file name.

## Run locally

```bash
pip install -r requirements.txt jupyter pytest nbmake
pytest tests/ --nbmake notebooks/
jupyter lab notebooks/
```

## Data

The data files are extracted from Gaia DR3 and APOGEE DR17 with `scripts/build_data.py`, which records the exact SQL
(or source URL) of each file in `data/MANIFEST.json`. Sources, licences and acknowledgements:
[data/README.md](data/README.md).

## Licence

Tutorial code and text: MIT (see [LICENSE](LICENSE)). Data files: see [data/README.md](data/README.md).
