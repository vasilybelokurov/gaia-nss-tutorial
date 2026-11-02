# STRUCTURE.md

Plan of the tutorial **Non-single stars in Gaia**. Audience: students (beginner upwards: numpy, matplotlib,
magnitudes and parallaxes) who want to find and interpret stellar companions in Gaia data. Exit level: select, validate
and interpret binary candidates in Gaia DR3 (excess noise and RUWE, astrometric and spectroscopic orbits, radial-velocity
scatter), and fit orbits to Gaia DR4 epoch astrometry. Gaia DR4 (66 months of data, 25 July 2014 – 20 January 2020) is
scheduled for 2 December 2026 (https://www.cosmos.esa.int/web/gaia/data-release-4); its epoch astrometry for 12 sources,
including Gaia BH3, was pre-released in June 2026 (https://www.cosmos.esa.int/web/gaia/dr4-prerelease) and is used here.

A first draft of this plan was reviewed independently by Codex (OpenAI; web research, 2026-10-30) and by Claude Fable
(2026-10-30). Adopted changes:

- **Physics corrected.** The photocentre semimajor axis is a0 = a |B − β| (B = q/(1+q), β = l/(1+l)): zero for
  equal-mass twins. For a circular orbit and random scan angles the along-scan rms of the wobble is
  a0 √(1 + cos² i)/2 (a0/√2 face-on, a0/2 edge-on; checked with a simulation before adoption), not a0/√2 in general.
  The "UWE peaks at P ≈ T" statement holds only at fixed masses (a0 ∝ P^{2/3}), not at fixed a0.
- **Catalogue values are not simulation values.** Gaia's excess noise (AEN) has an attitude/calibration floor, and RUWE an
  empirical normalisation; the toy is compared with the data only through ratios and limiting cases.
- **Doubt before masses.** Orbit validation (publication filters, aliases, ESA's list of false orbits) comes before
  masses and AMRF triage, in the same chapter.
- **No tautological or single-draw asserts.** All NSS astrometric solutions were preselected with RUWE ≥ 1.4 (verified:
  minimum RUWE 1.4000 for Orbital, AstroSpectroSB1, Acceleration7/9 in a 2% sample), so "binaries have high RUWE" is a
  selection, taught as such. Stochastic checks use ensembles (pull distributions), not single realisations.
- **Benchmarks matched to the same data and likelihood.** Gaia BH1: the DR3 astrometry-only solution gives
  M2 = 12.8 ± 2.0 M☉ (El-Badry et al. 2023a, Table 1); the joint Gaia + RV fit 9.62 ± 0.18 M☉. We reproduce the former
  and discuss the difference. Gaia BH3: asserts against the astrometry-only column of Gaia Collaboration, Panuzzo et al.
  (2024, Table 2), from the same DR4 pre-release data. BH2 has a giant primary: no main-sequence AMRF class is asserted.
- **Errata and failures taught.** `ipd_gof_harmonic_amplitude/phase` were computed from the G flux (ESA DR3 known issues,
  9 Oct 2024): not used. Four NSS orbits are declared false by ESA (WD 0141−675, HIP 64690, 54 Cas, HIP 66074). Follow-up
  shows most extreme-mass-function DR3 orbits were wrong (Simon et al. 2026; El-Badry et al. 2026).
- **Chapter 10 on real data.** The DR4 epoch astrometry pre-release replaces the purely synthetic DR4 chapter.

## Principles

1. **Doubt first.** A deviation from a single-star model is not a companion until resolved pairs, variability, calibration
   and selection have been ruled out; a published orbit is not a mass until its validation has been checked.
2. **One model, three channels.** Astrometry, spectroscopy and photometry measure projections of the same Keplerian
   orbit. The along-scan design matrix of Chapter 1 is the one used on real DR4 epoch data in Chapter 5.
3. **Toy first, then data.** Each effect is first produced in a simulation with known input, then found in the catalogue.
4. **Public data as pre-extracted files.** Students have no WSDB access. `scripts/build_data.py` queries WSDB (sqlutilpy;
   every plan checked with `EXPLAIN`), and downloads the DR4 pre-release, writing parquet files plus a manifest (query,
   rows, SHA-256). Files are attached to the GitHub release `data-v0.3` (earlier releases remain available unchanged); notebooks download them and check the SHA-256.
   Published assets stay unchanged: a changed selection gets a new name and a new release with the expanded manifest.
5. **Plot + assertion.** Every claim comes with a numbered figure, a caption that says what is plotted, a discussion, and
   an `assert` with a stated tolerance. Asserts are of four kinds, named as such: reproducibility (a published number from
   the same data), mathematical identity or limit, statistical calibration (ensemble of simulations), and descriptive
   checks on the data (frozen after a development run).
6. **Least code that works.** Each notebook is self-contained (runs alone in Colab); small helpers are repeated.

## Releases

| Release | Content | Status |
|---|---|---|
| **v0.1** | Ch 00–05: the DR3 NSS catalogue; the photocentre wobble (toy Gaia); RUWE and AEN in a 100-pc sample; astrometric orbits (validation, masses, AMRF, Gaia BH1); spectroscopic binaries and RV variability (with APOGEE); DR4 epoch astrometry (Gaia BH3) | built 2026-10-30 |
| v0.2 | Accelerations and the Hipparcos–Gaia proper-motion anomaly; eclipsing and ellipsoidal binaries in epoch photometry; combining channels and hierarchical triples; compact-companion candidates and their follow-up | core Chapters 06–09 implemented; data-v0.3 |
| v0.3 | Selection functions (Lam et al. 2025; El-Badry et al. 2024b); wide binaries; Gaia DR4 NSS catalogue (after public release) | started locally: Chapter 10 draft |

## Core release and future development

The v0.2 book contains Chapters 00–09. New extracts are distributed with data-v0.3. Chapter 10 remains a
local draft outside the published book and repository release; its real-survey benchmark is unfinished.
The remaining chapter numbers reserve future topics.

| Chapter | First deliverable | Data and release gate |
|---|---|---|
| **06 — Accelerations** | Taylor expansion, DR3 accelerations, simulated anomaly, real HGCA covariance calculation reproducing Table 3, and exact-ID comparison | Released `hgca_edr3` extract built from a pinned author copy |
| **07 — Photometric binaries** | Uniform-disk and harmonic models; two observed eclipsing light curves plus an observed ellipsoidal candidate with a published amplitude check; NSS count; eclipse geometry and cadence | Released `eb_epoch_examples` extract: both brightest NSS eclipsing systems, 123 returned transits with flags retained; `ellipsoidal_epoch_example` for Gomel Table 3 |
| **08 — Combining channels and triples** | Published joint-solution counts; one-to-one separate-solution joins; SB2 mass identities; hierarchical photocentre cancellation | Existing `nss_two_body`; no additional data required |
| **09 — Compact-companion follow-up** | Published RV mass functions, original Gaia predictions, inclination dependence and BH1 fit history | Released `compact_followup` extract from auditable paper-table transcription; fitted parameters, not epoch RVs |
| **10 — Selection functions** | Running draft: analytic versus injected detection probabilities, independent test-population recovery, and inclination mismatch | No external data yet; next reproduce a published DR3 selection-function benchmark with matched assumptions |
| 11 — Wide binaries | Identify and validate a resolved-pair sample | Public pair catalogue and an explicit contamination/selection treatment |
| 12 — DR4 catalogue | Compare released DR4 solutions with the earlier chapters | Wait for the public catalogue, validate its schema and selection rules, then create new versioned extracts |

The core sequence now runs through `notebooks/09_compact_companions.ipynb`. Chapter 10 remains a separate draft.
They contain numbered figures, analytic or published checks, and explicit limits. Chapter 06 now uses all 115,346 real HGCA rows, reproduces its ten-star printed benchmark to 0.051 in chi-square,
and finds 3,235 exact-ID DR3 acceleration matches. Chapter 10 is not a calibrated Gaia selection function. References were checked against
ADS and the linked arXiv records. Changed extracts get new filenames and a new data release.

## v0.1 chapters (built 2026-10-30)

Measured values are in brackets. Tolerances marked "frozen" were set before the comparison was run; where a pre-set
expectation failed, the table says so.

| Ch | Notebook | Learning objective | Data | Assert (kind; tolerance) [result] |
|---|---|---|---|---|
| 00 | `00_data` | The DR3 NSS products: tables, solution types, solutions vs sources, the `non_single_star` bits; channels in the CMD and in period; the astrometric preselection (G < 19, RUWE > 1.4, ≥ 12 visibility periods, `ipd_frac_multi_peak` ≤ 2, `ipd_gof_harmonic_amplitude` < 0.1) | `nss_two_body`, `nss_acceleration`, `nss_other` | reproducibility: all counts of Arenou et al. 2023 Table 1, 839 098 solutions, 813 687 sources [exact]; descriptive: median P eclipsing < spectroscopic < astrometric [1, 117, 600 d]; preselection visible in the catalogue: min RUWE ≥ 1.4 [1.4000], harmonic amplitude < 0.1 [max 0.09999], `ipd_frac_multi_peak` > 2 in < 0.1% [141 of 506 280, all = 3] |
| 01 | `01_photocentre_wobble` | Photocentre a0 = a\|B − β\| (twins invisible); toy Gaia (transits of 9 CCDs, random scan angles, 5-parameter least squares); UWE and excess noise vs period; E[χ²] = ν + ‖(I − H)s‖² | synthetic | identity: flux-weighted photocentre = \|B − β\| for three flux ratios, twin a0 = 0 (the earlier check of B against its own definition was tautological); calibration: mean UWE² of 300 single stars = 1 within 3σ [1.008 ± 0.005]; ε/a0 = √(1+cos²i)/2 · √(1 − 5/N_tr) within 3% [the factor √(1 − 5/N_tr) was found necessary: without it the simulation is 8% low]; fixed-mass UWE peak within a factor 2 of T [2.3 yr]; ensemble ⟨χ²⟩ = projection formula within 3σ |
| 02 | `02_ruwe_aen` | Cleaning a 100-pc sample (6-parameter and G > 19 sources are mostly spurious); RUWE vs G and distance; AEN floor; RUWE > 1.4 fraction across the CMD and vs height above the MS; resolved pairs (`ipd_frac_multi_peak`; IPD harmonic erratum); AEN vs the toy prediction for DR3 orbits, with eccentricity | `gcns100`, `nss_two_body` | descriptive: RUWE mode rises with parallax at 13 < G < 15 [1.085, 1.115, 1.155; a pre-set expectation "mode within 0.03 of 1" failed: 1.035]; RUWE > 1.4 fraction 0.4–0.75 mag above the MS > on it, 95% intervals disjoint [0.397 vs 0.126]; multi-peak > 30% vs none: > 3× [0.89 vs 0.14]; identity: eccentric along-scan rms formula = simulation within 1%; regression (tolerance set after a development run, so not independent): median AEN/prediction within 15% of 1 [0.951 eccentric; 0.879 with the circular formula used in v0.1] |
| 03 | `03_astrometric_orbits` | Thiele–Innes ↔ Campbell; `corr_vec` decoding (packing verified on the data, parameter order from the data model) and Monte Carlo errors; validation: Halbwachs filters, 1-yr deficit, ESA's four false orbits (three `OrbitalTargetedSearch`, one `…Validated`); follow-up outcomes (Sozzetti 2023, Marcussen & Albrecht 2023, Simon 2026, El-Badry 2026); mass function; AMRF classes with the triple domain q ≤ 2 (Shahaf et al. 2019, Eq. 13; white-dwarf band at 𝒜 ≈ 0.55 reproduced); Gaia BH1 | `nss_two_body`, `isochrones_gaia_solar` | identity: round trip < 1e-9 mas [9e-12]; column-major `corr_vec` positive definite [100% vs 0% row-major]; all eccentric orbits pass the filters [100%]; 1-yr deficit ratio < 0.5 [0.06]; AMRF boundaries finite over the whole primary-mass range (regression: v0.1 had NaN boundaries above 1.375 M☉ that put 517 stars in class III) [classes 18 271 / 4250 / 885, was 17 796 / 4098 / 1512]; reproducibility: BH1 a0 = 3.00 ± 0.05, σ(a0) within 30% of 0.22, i within 1° of 121.2 [2.978 ± 0.221, 121.3], M2 within 2.0 of 12.8 M☉ (astrometry only) [13.2], class III |
| 04 | `04_spectroscopic_binaries` | SB1 K1, P, e, f(M); SB1C as the pipeline's fallback (Gosset et al. 2025, Sect. 6.3.3); e–log P (circular below ~8 d); Katz et al. 2023 RV-variability criterion; validation with APOGEE DR17 `vscatter`, restricted to stars where the criterion applies | `nss_two_body`, `apogee_gaia` | identity: f(M) formula on a twin edge-on orbit; regression: median e < 0.1 at 3–8 d and > 0.2 above 30 d for cool and hot dwarfs; Gaia variable fraction among eligible stars rises with APOGEE vscatter (bins to 30 km/s, > 3σ per step) for cool dwarfs and giants [0.06 → 0.98; 0.04 → 0.97]; hot stars: 51% eligible, 12–19% flagged at 0.3–30 km/s, cause not established. Bashi et al.'s temperature-dependent cut-off is not reproduced (needs the upper envelope of clean solutions: exercise) |
| 05 | `05_dr4_epoch_astrometry` | DR4 epoch astrometry (pre-release): the DR4-like 6-parameter source model of `gaiasupdate` (colour prior, AGIS excess noise in the weights) reproduced; excess noise vs UWE as binarity indicators; DR4 vs DR3 precision; within- vs between-transit χ² (CCDs are not independent epochs); the data on the sky (measured along-scan + predicted across-scan; conventions tested) and, for each binary, the sequence astrometry → path on the sky → proper motion removed → proper motion and parallax removed (the orbit ellipse); Keplerian fit linear in Thiele–Innes constants, colour prior in the objective, transit-bootstrap uncertainties; Campbell elements, mass function; Gaia BH3 and the DR3 time window (χ² profile minimised at every period); HD 114762 and Gaia-4b against DR3 and the literature | `dr4_prerelease_epoch_astrometry`, `dr4_prerelease_dr3` | identity: parallax and χ² equal to `gaiasupdate` 0.1.2 for all 12 [< 1e-9 mas, < 5e-6]; conventions: low-precision solar ephemeris reproduces `parallax_factor_al` and `_ac` to 0.02 [< 0.01], across-scan sign reproduces `calculated_pos_ac` to 0.2 mas for all 12 [≤ 0.12], flipped sign ≥ 10× worse where z spans > 10 mas [up to 1457 mas]; calibration: UWE against σ of 9 quasars and single stars in [0.9, 1.15] [0.98–1.04], quasar parallaxes < 3σ, UWE against σ²+ε² of all 12 in [0.9, 1.1] [0.98–1.05]; DR4/DR3 uncertainty, 9 non-binaries, median within 0.1 of (34/66)^½ and (34/66)^{3/2} [0.70, 0.29], parallaxes within 2.5σ of DR3; within-transit χ²/ν of non-binaries in [0.85, 1.2] [0.95–1.10], binaries' between > 10× within; reproducibility: BH3 elements within 3σ of Panuzzo et al. 2024 astrometry only [all < 1.6σ]; BH3 period: DR4 scaled Δχ² > 100 beyond a factor 2 [231; the v0.1 assert "> 10³ unscaled" rested on a coarse (e, Tp) grid and was wrong: 701 at 8610 d], DR3 window: best orbit more than a factor 2 from the DR4 period and better than any orbit at it [18 209 d, e = 0.98; Δχ² = 110] (replaces v0.1's "Δχ² < 25 over 1500–30 000 d", an artefact of the same grid); HD 114762 and Gaia-4 P, e within 3σ of DR3 [< 1.3σ]; HD 114762 M2 and i within 3σ of Winn 2022 (joint DR3 + Doppler) [0.195–0.223 vs 0.215 ± 0.013 M☉; 9 ± 6° vs 3.63°]; Gaia-4b a0, e, M2 within 3σ of the adopted Gaia+RV solution of Stefánsson et al. 2025 [1.1σ, 1.2σ, 0.9σ; v0.1 compared with their DR3-only a0], ≥ 95% of bootstrap M2 < 13 MJ [96%]. Not asserted: Gaia-4 P = 579 ± 3 d vs 571.3 ± 1.4 d (2.2σ) |

## External review (2026-10-30)

Two independent reviews of Chapters 0–5 against the literature: Fable (a Claude model, with ADS/SciX and the papers'
tables) and Codex (OpenAI, read-only, `ask-codex` skill). Every finding was checked against the code, the data or the
cited paper before acting on it. Accepted and fixed: the AMRF class-III fall-through and triple domain (Ch 3); the
coarse-grid BH3 period profile and the asserts built on it (Ch 5); Gaia-4b compared with the adopted Gaia+RV solution,
not DR3 (Ch 5); HD 114762 benchmarked against Winn 2022 (Ch 5); the full Halbwachs preselection (Ch 0); the misquoted
follow-up results of Simon 2026 / El-Badry 2026 (Ch 3); eccentric AEN prediction (Ch 2); APOGEE comparison restricted
to stars where the Katz criterion applies (Ch 4); SB1C semantics, `rv_amplitude_robust` definition, f(M) arithmetic,
σ(UWE) (Ch 1, 4); tautological and post-hoc asserts relabelled; reference metadata. Not changed: the bootstrap is not
calibrated for BH3's incomplete long-period arc (stated in Ch 5 as a limitation). A later, separate
injection–recovery check tests a 600-day synthetic orbit with independent and shared transit noise; see
`validation/README.md`. It also exposed an eccentricity-boundary bug: refinement now returns the clipped
eccentricity used by its objective, with regression tests at both boundaries. The data-build
script uses locked atomic writes and query-checked checkpoints. Offline tests now cover unsafe query plans,
stale checkpoints, interrupted Parquet writes, and refusal to overwrite an existing data name with changed content.

## Data (v0.1)

| File | Content |
|---|---|
| `nss_two_body` | all 443,205 rows of `gaia_dr3.nss_two_body_orbit` (elements, errors, `corr_vec`, quality) joined with the binarity, photometry and RV columns of `gaia_source` |
| `nss_acceleration` | all 338,215 rows of `nss_acceleration_astro`, joined with `gaia_source` |
| `nss_other` | `nss_non_linear_spectro` (56,808) and `nss_vim_fl` (870): type and goodness of fit, with `gaia_source` photometry |
| `gcns100` | `gaia_source` stars with ϖ > 10 mas and ϖ/σ_ϖ > 5, binarity columns (541 958 rows; cleaned in Chapter 2) |
| `apogee_gaia` | APOGEE DR17 stars with ≥ 3 visits, `vscatter`, Teff, log g, joined with the Gaia DR3 RV columns |
| `isochrones_gaia_solar` | PARSEC isochrones in Gaia bands near solar metallicity (primary masses) |
| `dr4_prerelease_epoch_astrometry` | the June 2026 DR4 pre-release epoch astrometry, one row per CCD observation |
| `dr4_prerelease_dr3` | DR3 `gaia_source` and `nss_two_body_orbit` entries of the 12 pre-release sources |

## Literature (checked in ADS)

Gaia DR3 NSS: Gaia Collab., Arenou et al. 2023 https://ui.adsabs.harvard.edu/abs/2023A&A...674A..34G ·
Halbwachs et al. 2023 https://ui.adsabs.harvard.edu/abs/2023A&A...674A...9H ·
Holl et al. 2023a (orbits, MCMC) https://ui.adsabs.harvard.edu/abs/2023A&A...674A..10H ·
Holl et al. 2023b (scan-angle signals) https://ui.adsabs.harvard.edu/abs/2023A&A...674A..25H ·
Gosset et al. 2025 (SB1) https://ui.adsabs.harvard.edu/abs/2025A&A...693A.124G ·
Mowlavi et al. 2023 (EBs) https://ui.adsabs.harvard.edu/abs/2023A&A...674A..16M ·
Gomel et al. 2023 (ellipsoidals) https://ui.adsabs.harvard.edu/abs/2023A&A...674A..19G ·
Babusiaux et al. 2023 https://ui.adsabs.harvard.edu/abs/2023A&A...674A..32B ·
Katz et al. 2023 (RVs) https://ui.adsabs.harvard.edu/abs/2023A&A...674A...5K ·
Lindegren et al. 2021 https://ui.adsabs.harvard.edu/abs/2021A&A...649A...2L ·
ESA DR3 known issues https://www.cosmos.esa.int/web/gaia/dr3-known-issues

Unresolved binaries in astrometry: Belokurov et al. 2020 https://ui.adsabs.harvard.edu/abs/2020MNRAS.496.1922B ·
Penoyre et al. 2020 https://ui.adsabs.harvard.edu/abs/2020MNRAS.495..321P ·
Penoyre et al. 2022a,b https://ui.adsabs.harvard.edu/abs/2022MNRAS.513.2437P , https://ui.adsabs.harvard.edu/abs/2022MNRAS.513.5270P ·
Andrew et al. 2022 https://ui.adsabs.harvard.edu/abs/2022MNRAS.516.3661A ·
Castro-Ginard et al. 2024 https://ui.adsabs.harvard.edu/abs/2024A&A...688A...1C ·
Kervella et al. 2019, 2022 https://ui.adsabs.harvard.edu/abs/2019A&A...623A..72K , https://ui.adsabs.harvard.edu/abs/2022A&A...657A...7K ·
Brandt 2021 (HGCA) https://ui.adsabs.harvard.edu/abs/2021ApJS..254...42B

Masses, triage, compact companions: Shahaf et al. 2019, 2023, 2024 https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.5610S ,
https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.2991S , https://ui.adsabs.harvard.edu/abs/2024MNRAS.529.3729S ·
El-Badry et al. 2023a (BH1) https://ui.adsabs.harvard.edu/abs/2023MNRAS.518.1057E ·
El-Badry et al. 2023b (BH2) https://ui.adsabs.harvard.edu/abs/2023MNRAS.521.4323E ·
Nagarajan et al. 2024 (BH1 ESPRESSO) https://ui.adsabs.harvard.edu/abs/2024PASP..136a4202N ·
Gaia Collab., Panuzzo et al. 2024 (BH3) https://ui.adsabs.harvard.edu/abs/2024A&A...686L...2G ·
El-Badry et al. 2024a (NS candidates) https://ui.adsabs.harvard.edu/abs/2024OJAp....7E..58E ·
El-Badry et al. 2024b (generative model) https://ui.adsabs.harvard.edu/abs/2024OJAp....7E.100E ·
Lam et al. 2025 (selection function) https://ui.adsabs.harvard.edu/abs/2025ApJ...987..215L ·
Simon et al. 2026 https://ui.adsabs.harvard.edu/abs/2026ApJ..1007..160S ·
El-Badry et al. 2026 https://ui.adsabs.harvard.edu/abs/2026arXiv260806453E ·
El-Badry & Rix 2022 https://ui.adsabs.harvard.edu/abs/2022MNRAS.515.1266E ·
Nagarajan et al. 2023 (ellipsoidal follow-up) https://ui.adsabs.harvard.edu/abs/2023MNRAS.524.4367N ·
El-Badry 2024 (review) https://ui.adsabs.harvard.edu/abs/2024NewAR..9801694E

Spectroscopic binaries: Bashi et al. 2022 https://ui.adsabs.harvard.edu/abs/2022MNRAS.517.3888B ·
Bashi et al. 2023 https://ui.adsabs.harvard.edu/abs/2023MNRAS.522.1184B ·
Abdurro'uf et al. 2022 (APOGEE DR17) https://ui.adsabs.harvard.edu/abs/2022ApJS..259...35A ·
Katz et al. 2023 criterion, Sect. 3.7 · Stefánsson et al. 2025 (Gaia-4b) https://ui.adsabs.harvard.edu/abs/2025AJ....169..107S ·
Gaia Collab., Smart et al. 2021 (GCNS) https://ui.adsabs.harvard.edu/abs/2021A&A...649A...6G

## Repository layout

```
notebooks/      NN_<slug>.ipynb, committed without outputs, each runs standalone in Colab
scripts/        build_data.py (WSDB and DR4 pre-release → parquet + manifest; instructor only)
data/           README.md (licences, columns) and MANIFEST.json; parquet files are release assets
tests/          pytest tests
_config.yml, _toc.yml, intro.md   Jupyter Book
_static/custom.css                page layout as in the dynamics and substructure tutorials
.github/workflows/book.yml        tests, executes notebooks, publishes to GitHub Pages
```

## Testing

`pytest tests/ --nbmake notebooks/` executes every notebook in a fresh kernel; notebooks contain explicit `assert`
cells; fixed random seeds. `jupyter-book build . -W -n --keep-going` builds the site. Both run in CI on every push.
