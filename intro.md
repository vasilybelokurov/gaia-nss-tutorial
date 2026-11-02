# Non-single stars in Gaia

About half of all Sun-like stars have a stellar companion, and Gaia sees many of them without resolving them: the
companion makes the star's light centre wobble, its velocity change, or its brightness dip. This tutorial teaches how
these companions are found and characterised in Gaia data, from the binarity indicators of every Gaia source (RUWE,
excess noise, radial-velocity scatter) to the orbits of the Gaia DR3 non-single-star catalogue, and on to the epoch
astrometry that Gaia DR4 (scheduled for 2 December 2026) will publish for every star.

Each chapter is a self-contained Jupyter notebook that runs in Google Colab or locally, downloads any
external data automatically with checksum checks, and pairs figures with explicit numerical checks (`assert`). The v0.2.1
tutorial contains Chapters 00–10; the expanded data release is data-v0.3.

**Chapters**

0. The Gaia DR3 non-single-star catalogue
1. The photocentre wobble: how a companion perturbs Gaia astrometry (a toy Gaia)
2. RUWE and excess noise in the 100-pc sample
3. Astrometric orbits: validation, masses, and Gaia BH1
4. Spectroscopic binaries and radial-velocity variability
5. Gaia DR4 epoch astrometry: refitting stars and orbits (Gaia BH3, HD 114762, Gaia-4b)

6. Accelerations and Hipparcos–Gaia proper-motion anomalies
7. Photometric binaries: eclipses, ellipsoidal modulation and sampling
8. Combining channels and recognising hierarchical systems
9. Compact companions: prediction and follow-up
10. Selection functions: a controlled experiment

Chapter 10 uses simulated observations to teach completeness and population correction. A real-survey
selection benchmark, wide binaries and a full public DR4 catalogue analysis remain on the v0.3 roadmap in
`STRUCTURE.md`.

**Prerequisites.** Basic Python (numpy, matplotlib) and elementary astronomy (magnitudes, parallax, Kepler's laws).

**Data.** Gaia DR3 (and APOGEE DR17) extracted from the WSDB database in Cambridge, and the June 2026 pre-release of
Gaia DR4 epoch astrometry. See `data/README.md` for sources and licences.
