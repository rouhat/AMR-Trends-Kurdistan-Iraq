# AMR-Trends-Kurdistan-Iraq

**Antimicrobial resistance surveillance in a secondary-care hospital, Kurdistan Region of Iraq (2013–2025)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: analysis in progress](https://img.shields.io/badge/Status-analysis%20in%20progress-orange.svg)](#status)

---

## Overview

This repository holds an antimicrobial resistance (AMR) surveillance dataset
assembled from the microbiology laboratory records of Zakho General Emergency
Hospital, Kurdistan Region of Iraq, covering 2013–2025.

The Kurdistan Region of Iraq does not appear in the major international
resistance surveillance networks (WHO GLASS, EARS-Net). Routine susceptibility
testing is carried out in hospitals across the region, but the results are
read once, filed, and rarely aggregated or analysed over time. This dataset is
an attempt to close part of that gap for one hospital.

The work is carried out independently, without research funding or academic
supervision, alongside full-time laboratory employment.

---

## Status

**Data assembled. Analysis in progress.**

The dataset has been compiled and de-identified. Cleaning and analysis are
ongoing, and no resistance estimates are published here yet. Results will be
added once the data has been validated and denominators confirmed.

Earlier exploratory figures have been withdrawn pending that validation.

---

## Dataset

| | |
|---|---|
| **Setting** | Zakho General Emergency Hospital, Zakho, Kurdistan Region of Iraq |
| **Period** | 2013–2025 |
| **Isolates** | ~1,350 |
| **Specimen types** | Urine (predominant), wound swabs, sputum, HVS, ear swabs |
| **Organisms** | *E. coli*, *Klebsiella* spp., *Staphylococcus* spp., *Streptococcus* spp., *Pseudomonas aeruginosa*, *Proteus* spp., *Enterococcus* spp. and others |
| **Susceptibility testing** | Kirby–Bauer disk diffusion, CLSI standards |
| **Antibiotics** | 40+ agents across the period; panels vary by year and organism |

The records come from two sources with different antibiotic coding
conventions, which are being harmonised as part of the cleaning process.

---

## Planned analysis

1. Resistance rates by organism and by antibiotic, with denominators and
   confidence intervals reported for every estimate.
2. Temporal trends across the twelve-year period for key agents.
3. Prevalence of multi-drug resistance.
4. Variation by specimen type.

Rates will be reported per organism rather than pooled across organisms, and
estimates based on small numbers of isolates will be reported as counts rather
than percentages, following CLSI M39 guidance on cumulative antibiograms.

---

## Data availability

Raw isolate-level data is **not publicly available**. It is held at the
hospital and contains routine clinical laboratory records.

Aggregate results and the full analysis code will be published in this
repository once the analysis is complete.

The dataset has been de-identified: no patient names or identifiers are
retained.

---

## Repository contents

- `scripts/` — data cleaning and analysis pipeline (Python)
- `README.md` — this file
- `LICENSE` — MIT

---

## Limitations

- **Single centre.** Findings describe one hospital and should not be read as
  regional prevalence.
- **Clinical isolates only.** Specimens come from patients with suspected
  infection, not from community surveillance, so resistance is expected to be
  higher than in the general population.
- **Phenotypic testing only.** Resistance mechanisms have not been confirmed
  genotypically.
- **Varying panels.** The antibiotics tested differ by year, organism and
  specimen, so denominators differ between agents.
- **No linked outcomes.** The dataset contains susceptibility results, not
  patient outcomes.

---

## Citation

```bibtex
@dataset{abdullah_amr_kurdistan,
  author    = {Abdullah, Rohat},
  title     = {Antimicrobial Resistance Surveillance, Kurdistan Region of Iraq (2013--2025)},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/rouhat/AMR-Trends-Kurdistan-Iraq}
}
```

---

## Contact

**Rohat Haji**
Biologist, Microbiology Laboratory
Zakho General Emergency Hospital, Kurdistan Region of Iraq

[ORCID 0000-0002-1661-6913](https://orcid.org/0000-0002-1661-6913) · rouhat.abdullah@gmail.com

---

## Acknowledgements

Microbiology Laboratory, Zakho General Emergency Hospital.

---

## License

MIT — see [LICENSE](LICENSE).
