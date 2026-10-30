# AGENTS.md

## Project

A Python tutorial, in Jupyter notebooks published from a public git repo, on non-single stars in Gaia data:
companions of stars detected through astrometry (orbits, accelerations, and the excess noise and RUWE of single-star
solutions), spectroscopy (orbits and radial-velocity scatter) and photometry (eclipses, ellipsoidal variation). It uses
Gaia DR3 — the non-single-star (NSS) tables and the binarity indicators of `gaia_source` — to prepare for Gaia DR4 and
its epoch data. Data come from WSDB (Whole Sky Database) and are shipped to students as pre-extracted files.
**Public data only.**

## Rules

1. **Write the least code that works.**
2. **Always reproduce bugs with a failing test** before fixing them.
3. **Show a plot before claiming a result.**

## Workflow

- Chapters are `notebooks/NN_<slug>.ipynb`, committed without outputs; each runs standalone in Colab.
- Students have no WSDB access: `scripts/build_data.py` queries WSDB (sqlutilpy; every plan checked with `EXPLAIN`)
  and writes the parquet files that notebooks download (with a SHA-256 check against `data/MANIFEST.json`).
  Published files are never changed in place: a changed selection gets a new file name.
- Each notebook backs every claim with a numbered figure (**Figure N.k** caption that states what is plotted, axes,
  units, colours and samples), a discussion of what the figure shows, and an `assert` with a stated tolerance against
  a known result (a published value, an analytic expectation, or a simulation with known input).
- Comment the code for beginners: at each point of use explain the physics (which formula a line implements) and the
  non-obvious numpy/scipy idioms.
- Before pushing: `pytest tests/ --nbmake notebooks/` and `jupyter-book build . -W -n --keep-going`.
- Every literature reference carries a working ADS/arXiv/DOI link, checked before it is committed.
