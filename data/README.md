# Data for the Gaia non-single-star tutorial

Small extracts of public catalogues, prepared for the notebooks of
https://github.com/vasilybelokurov/gaia-nss-tutorial and attached to its
[`data-v0.3` release](https://github.com/vasilybelokurov/gaia-nss-tutorial/releases/tag/data-v0.3).
Published assets, including a release's `MANIFEST.json`, are never replaced. For future changes, give each changed
selection or file a new name (for example, `gcns100_v2`), keep the old manifest entries, and publish the expanded
manifest and required data files in a new release. Update notebook filenames and the release URL together.
Historically, `data-v0.2` reused the name `dr4_prerelease_epoch_astrometry` for a changed file and added
`dr4_prerelease_dr3`; `data-v0.1` remains unchanged. Keep those existing releases intact.

The builder refuses to change the bytes or recorded query of a name already in the local manifest. An identical
rebuild is allowed and keeps its original provenance. For a revised SQL selection, add a new key to `QUERIES`
or `SCANS` in `scripts/build_data.py` before building it; do not delete the old manifest entry to bypass the check.
Different Parquet writer versions or row ordering can also change the checksum: use the published asset when
you need the original bytes. Data files and the manifest are replaced atomically one at a time; if a build stops
between those replacements, a complete but unlisted local file may remain. Rerun the build before publishing.

Every file is rebuilt by `scripts/build_data.py`. Gaia DR3 and APOGEE DR17 files come from WSDB (Cambridge); every
query plan was checked with `EXPLAIN` before running (no sequential scan of `gaia_source`); for the chunked scan, the
plan of the first chunk, as all chunks run the same query. `MANIFEST.json` lists, for
each file, the exact SQL (or source URL), the row count, the size, the SHA-256 checksum and the creation time.

Format: Apache Parquet (zstd). Read with `pandas.read_parquet(path)`. Angles in degrees, parallaxes and Thiele–Innes
constants in mas, proper motions in mas/yr, periods in days, velocities in km/s. Floating-point columns are float32
except positions, periods and periastron times (the DR4 pre-release file keeps every column at its native precision). Missing values: NaN (floating point), −1 (integers).

## Additional data in data-v0.3

`hgca_edr3.parquet` contains all 115,346 rows and 35 columns of Brandt (2021)'s public HGCA EDR3 catalogue,
with native precision, integer identifiers, calibrated proper motions/errors/correlations, individual reference
epochs, and correction terms. Build with `python scripts/build_data.py hgca_edr3`; no database access is used.
The author’s FITS copy is pinned to an orvara commit and checked by SHA-256 before conversion; the exact URL
and source checksum are in `MANIFEST.json`. Cite [Brandt (2021)](https://arxiv.org/abs/2105.11662), Table 4,
and retain the Gaia/Hipparcos acknowledgements. The author repository’s BSD 3-Clause notice is retained in `HGCA_SOURCE_LICENSE.txt`; retain the underlying Gaia data attribution and terms.
This extract is a data-v0.3 asset. Existing releases and their manifest entries are unchanged.

`eb_epoch_examples.parquet` retains every returned column and quality flag from the Gaia DR3 DataLink
responses for sources 5895765142704352640 and 541801332594262912, the two brightest NSS `EclipsingBinary`
entries in the existing extract. It has 123 transit rows; Chapter 7 applies its G-band quality cut explicitly.
URLs and response hashes are recorded in the manifest. Times are barycentric JD in TCB minus 2455197.5 days;
fluxes and errors use the original Gaia units. Native float precision and integer source/transit IDs are retained.
Gaia data terms and acknowledgements below apply.

`compact_followup.parquet` contains three published RV orbital-fit summaries from El-Badry et al. (2023),
Table 1, and Simon et al. (2026), Table 4. The auditable transcription is `compact_followup.json`, with source
IDs, units in field names, asymmetric marginal uncertainties, fixed-parameter flags and paper links. It is
not a set of epoch measurements or a joint posterior. BH1 uses the historical fixed-period RV-only fit;
Chapter 9 separately quotes the later Nagarajan et al. result. The builder records the transcription hash.

`ellipsoidal_epoch_example.parquet` retains the DataLink response for source 4042390512917208960,
the bright ellipsoidal candidate shown in Gomel et al. (2023), Table 3 and Figure 9
(https://arxiv.org/abs/2206.06032). Chapter 7 reproduces its 38 accepted G transits and second-harmonic
amplitude. Its candidate status is retained; the tutorial does not infer a compact companion from its amplitude.
Gaia data terms and acknowledgements apply, with the additional paper citation.

Maintainers can rebuild these additions with
`python scripts/build_data.py eb_epoch_examples ellipsoidal_epoch_example compact_followup`.
All three extracts are included in data-v0.3. The literature parameter transcription is a small attributed
compilation of published numerical facts; the tutorial adds no restrictions to those facts. Retain the paper
references and table identifiers. Do not replace an existing release asset.

## Files

| File | Content |
|---|---|
| `nss_two_body` | all 443,205 rows of `gaia_dr3.nss_two_body_orbit`: solution type, orbital elements (Thiele–Innes constants, period, eccentricity, periastron time, semi-amplitudes, …) with errors, `corr_vec` (correlation matrix, upper triangle, order given by `bit_index`), fit quality (`goodness_of_fit`, `significance`, `efficiency`, `flags`), the NSS parallax and proper motion (`nss_*`), and the `gaia_source` columns listed below |
| `nss_acceleration` | all 338,215 rows of `gaia_dr3.nss_acceleration_astro` (`Acceleration7`, `Acceleration9`): accelerations and their derivatives with errors, fit quality, NSS parallax and proper motion, and the `gaia_source` columns |
| `nss_other` | `gaia_dr3.nss_non_linear_spectro` (56,808 trend-only RV solutions) and `gaia_dr3.nss_vim_fl` (870 variability-induced movers): table, solution type, goodness of fit, G, BP − RP, parallax, RUWE |
| `gcns100` | `gaia_source` stars with parallax > 10 mas and parallax_over_error > 5 (all sky), with the columns below |
| `apogee_gaia` | APOGEE DR17 `allStar` stars with ≥ 3 visits, S/N > 50, G < 13, duplicates removed (`EXTRATARG` bit 4): `vscatter`, `vhelio_avg`, T_eff, log g, [M/H], v sin i, flags, joined with the Gaia DR3 RV columns of the same source |
| `isochrones_gaia_solar` | PARSEC isochrones (WSDB `isochrones.gaia_1804`) in Gaia G, BP, RP for [Fe/H] = 0 and ages 1, 3.16, 10 Gyr |
| `dr4_prerelease_epoch_astrometry` | the Gaia DR4 epoch-astrometry pre-release (June 2026, `Gaia DR4_RC3`; 12 sources) with one row per CCD observation (`ccd` 0 = sky mapper, 1–9 = AF1–AF9), all columns at native precision: per transit `obs_time_bary_corr` [ns, TCB(barycentric) − TCB(at Gaia), at AF4], `agis_source_excess_noise` [mas], `parallax_factor_al`, `nu_eff_used_in_astrometry`, flags; per CCD `obs_time_tcb` [ns from JD 2455197.5, TCB at Gaia], `scan_pos_angle` [deg], `centroid_pos_al` and its error [mas], `colour_factor_al`, `calculated_pos_ac` [mas], `used_by_agis_al`, `ccd_proc_flags`, … The empty across-scan centroid arrays are dropped |
| `dr4_prerelease_dr3` | the Gaia DR3 `gaia_source` entries of the 12 pre-release sources (same `source_id` for this curated sample, not in general), with their DR3 `nss_two_body_orbit` solution where one exists (Gaia-4, HD 114762; `corr_vec` omitted) |

`gaia_source` columns in `nss_*` and `gcns100`: `source_id`, `ra`, `dec`, `l`, `b`, `parallax`, `pmra`, `pmdec` and errors,
`phot_g_mean_mag`, `bp_rp`, `phot_bp_rp_excess_factor`, `ruwe`, `astrometric_excess_noise(_sig)`, `astrometric_n_good_obs_al`,
`astrometric_params_solved`, `visibility_periods_used`, `ipd_gof_harmonic_amplitude`, `ipd_frac_multi_peak`,
`ipd_frac_odd_win`, `duplicated_source`, `non_single_star`, `phot_variable_flag`, `radial_velocity(_error)`,
`rv_method_used`, `rv_nb_transits`, `rv_chisq_pvalue`, `rv_renormalised_gof`, `rv_amplitude_robust`, `grvs_mag`,
`rv_template_teff`, `vbroad`. Note: `ipd_gof_harmonic_amplitude` was computed from the G flux by mistake and should not
be used (ESA, Gaia DR3 known issues, 9 October 2024, https://www.cosmos.esa.int/web/gaia/dr3-known-issues).

## Licences and terms

The Gaia-derived extracts are distributed under **CC BY-NC 4.0**, because Gaia data are distributed under CC BY-NC 3.0 IGO
(https://www.cosmos.esa.int/web/gaia-users/license). Per product:

| Product | Terms | Please cite |
|---|---|---|
| Gaia DR3 | CC BY-NC 3.0 IGO, credit ESA/Gaia/DPAC | Gaia Collaboration 2016, https://ui.adsabs.harvard.edu/abs/2016A&A...595A...1G ; DR3: https://ui.adsabs.harvard.edu/abs/2023A&A...674A...1G ; NSS: https://ui.adsabs.harvard.edu/abs/2023A&A...674A..34G |
| Gaia DR4 epoch-astrometry pre-release | CC BY-NC 3.0 IGO, credit ESA/Gaia/DPAC | https://www.cosmos.esa.int/web/gaia/dr4-prerelease ; Gaia Collaboration, Panuzzo et al. 2024, https://ui.adsabs.harvard.edu/abs/2024A&A...686L...2G |
| APOGEE DR17 (SDSS-IV) | public data; acknowledge SDSS | Abdurro'uf et al. 2022, https://ui.adsabs.harvard.edu/abs/2022ApJS..259...35A |
| PARSEC isochrones | public | Bressan et al. 2012, https://ui.adsabs.harvard.edu/abs/2012MNRAS.427..127B |

## Acknowledgements

This work has made use of data from the European Space Agency (ESA) mission Gaia (https://www.cosmos.esa.int/gaia),
processed by the Gaia Data Processing and Analysis Consortium (DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium).
Funding for the DPAC has been provided by national institutions, in particular the institutions participating in the
Gaia Multilateral Agreement. Funding for the Sloan Digital Sky Survey IV has been provided by the Alfred P. Sloan
Foundation, the U.S. Department of Energy Office of Science, and the Participating Institutions (https://www.sdss4.org).
