# Non-single stars in Gaia

About half of all Sun-like stars have a stellar companion, and Gaia sees many of them without resolving them: the
companion makes the star's light centre wobble, its velocity change, or its brightness dip. This tutorial teaches how
these companions are found and characterised in Gaia data, from the binarity indicators of every Gaia source (RUWE,
excess noise, radial-velocity scatter) to the orbits of the Gaia DR3 non-single-star catalogue, and on to the epoch
astrometry that Gaia DR4 (scheduled for 2 December 2026) will publish for every star.

Each chapter is a Jupyter notebook that runs on its own (in Google Colab, or locally), downloads the small data files
it needs, and backs every claim with a figure and an explicit numerical check (`assert`).

**Chapters**

0. The Gaia DR3 non-single-star catalogue
1. The photocentre wobble: how a companion perturbs Gaia astrometry (a toy Gaia)
2. RUWE and excess noise in the 100-pc sample
3. Astrometric orbits: validation, masses, and Gaia BH1
4. Spectroscopic binaries and radial-velocity variability
5. Gaia DR4 epoch astrometry: refitting stars and orbits (Gaia BH3, HD 114762, Gaia-4b)

Later chapters (accelerations and Hipparcos–Gaia proper-motion anomalies, eclipsing and ellipsoidal binaries, triples,
compact companions and their follow-up, selection functions, and the DR4 catalogue) are planned in `STRUCTURE.md` in
the repository.

**Prerequisites.** Basic Python (numpy, matplotlib) and elementary astronomy (magnitudes, parallax, Kepler's laws).

**Data.** Gaia DR3 (and APOGEE DR17) extracted from the WSDB database in Cambridge, and the June 2026 pre-release of
Gaia DR4 epoch astrometry. See `data/README.md` for sources and licences.
