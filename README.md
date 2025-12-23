# 🦠 AMR-Trends-Kurdistan-Iraq

## Twelve-Year Antimicrobial Resistance Surveillance in a Regional Hospital: Patterns, Trends, and Clinical Implications (2013–2025)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: Clinical](https://img.shields.io/badge/Data-Clinical%20Laboratory-blue.svg)]()
[![Region: Kurdistan-Iraq](https://img.shields.io/badge/Region-Kurdistan--Iraq-green.svg)]()

---

## 📋 Overview

This repository contains **12 years of antimicrobial resistance (AMR) surveillance data** from Zakho General Emergency Hospital in the Kurdistan Region of Iraq (2013–2025). The dataset represents one of the few comprehensive, long-term AMR surveillance studies from this underrepresented region in global resistance databases.

### Why This Matters

- **Geographic Gap**: AMR data from the Kurdistan Region of Iraq is scarce in global databases (GLASS, EARS-Net)
- **Longitudinal Value**: 12+ years of continuous surveillance enables meaningful trend analysis
- **Clinical Relevance**: Real-world data from an active hospital microbiology laboratory
- **Open Science**: Reproducible analysis with open data and code

---

## 📊 Dataset Summary

| Attribute | Value |
|-----------|-------|
| **Time Period** | November 2013 – November 2025 |
| **Total Records** | ~1,200+ isolates |
| **Sample Types** | Urine (primary), Sputum, Wound swabs, HVS, Ear swabs |
| **Key Organisms** | *E. coli*, *Klebsiella* spp., *Staphylococcus* spp., *Streptococcus* spp., *Pseudomonas*, *Proteus* |
| **Antibiotics Tested** | 30+ agents across multiple classes |
| **Setting** | Zakho General Emergency Hospital, Kurdistan Region, Iraq |

---

## 🗂️ Repository Structure

```
AMR-Trends-Kurdistan-Iraq/
│
├── README.md                          # Project overview (you are here)
├── LICENSE                            # MIT License
├── CITATION.cff                       # Citation information
│
├── data/
│   ├── raw/                           # Original anonymized datasets
│   │   ├── amr_data_2013_2022.csv     # Historical data
│   │   └── amr_data_2024_2025.csv     # Recent surveillance data
│   └── processed/                     # Cleaned, analysis-ready data
│       └── amr_combined_clean.csv
│
├── scripts/
│   ├── 01_data_cleaning.py            # Data preprocessing pipeline
│   ├── 02_analysis.py                 # Statistical analysis
│   ├── 03_visualizations.py           # Charts and graphs
│   └── utils.py                       # Helper functions
│
├── results/
│   ├── figures/                       # Generated visualizations
│   │   ├── resistance_trends.png
│   │   ├── organism_distribution.png
│   │   └── antibiotic_heatmap.png
│   └── tables/                        # Summary statistics
│       └── resistance_rates.csv
│
├── reports/
│   └── summary_report.md              # Key findings narrative
│
└── docs/
    ├── methodology.md                 # Detailed methods
    ├── data_dictionary.md             # Variable definitions
    └── antibiotic_codes.md            # Antibiotic abbreviations
```

---

## 🔬 Key Research Questions

1. **Temporal Trends**: How have resistance rates changed over 12 years?
2. **Critical Antibiotics**: What are the resistance patterns for carbapenems, fluoroquinolones, and third-generation cephalosporins?
3. **Organism-Specific Patterns**: Which organisms show the highest/fastest-increasing resistance?
4. **MDR Tracking**: What is the prevalence of multi-drug resistant (MDR) organisms?
5. **Sample-Type Analysis**: Do resistance patterns differ by specimen type?

---

## 🧪 Organisms Included

| Gram-Negative | Gram-Positive |
|---------------|---------------|
| *Escherichia coli* | *Staphylococcus aureus* |
| *Klebsiella pneumoniae* | *Staphylococcus epidermidis* |
| *Pseudomonas aeruginosa* | *Streptococcus* spp. |
| *Proteus mirabilis* | *Enterococcus* spp. |
| *Enterobacter* spp. | *Corynebacterium* spp. |

---

## 💊 Antibiotics Tested

### β-Lactams
- Penicillins: Ampicillin (AM), Amoxicillin (AX), Penicillin (P)
- Cephalosporins: Cefixime (CFM), Ceftriaxone (CRO), Cefotaxime (CTX), Cefepime (FEP)
- Carbapenems: Imipenem (IPM), Meropenem (MEM)
- β-Lactam combinations: Amoxicillin-Clavulanate (AMC), Piperacillin-Tazobactam (TPZ)

### Aminoglycosides
- Amikacin (AK), Gentamicin (CN), Tobramycin (TOB)

### Fluoroquinolones
- Ciprofloxacin (CIP), Levofloxacin (LEV), Norfloxacin (NOR), Ofloxacin (OFX)

### Others
- Tetracyclines: Doxycycline (DO), Tetracycline (TE), Tigecycline (TGC)
- Macrolides: Erythromycin (E), Azithromycin (AZM)
- Glycopeptides: Vancomycin (VA), Teicoplanin (TEC)
- Nitrofurans: Nitrofurantoin (F)
- Sulfonamides: Trimethoprim-Sulfamethoxazole (SXT)

---

## 🚀 Getting Started

### Prerequisites

```bash
# Python 3.8+
pip install pandas numpy matplotlib seaborn scipy openpyxl
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AMR-Trends-Kurdistan-Iraq.git
cd AMR-Trends-Kurdistan-Iraq

# Run the analysis pipeline
python scripts/01_data_cleaning.py
python scripts/02_analysis.py
python scripts/03_visualizations.py
```

---

## 📈 Preliminary Findings

*To be updated after analysis*

- Overall resistance trends (2013-2025)
- Most concerning resistance patterns
- Comparison with regional/global data

---

## 🔒 Data Privacy

- All patient identifiers have been removed
- Only aggregate demographic data (age, sex) is included
- Data has been reviewed for compliance with hospital ethics requirements

---

## 📄 Citation

If you use this dataset or code, please cite:

```bibtex
@dataset{amr_kurdistan_2025,
  author       = {[Your Name]},
  title        = {Twelve-Year Antimicrobial Resistance Surveillance in Kurdistan Region, Iraq (2013-2025)},
  year         = {2025},
  publisher    = {GitHub},
  url          = {https://github.com/YOUR_USERNAME/AMR-Trends-Kurdistan-Iraq}
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

---

## 📬 Contact

**[Your Name]**  
Assistant Biologist, Microbiology Laboratory  
Zakho General Emergency Hospital  
Kurdistan Region, Iraq

📧 [Your Email]  
🔗 [LinkedIn/ORCID]

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Zakho General Emergency Hospital Microbiology Laboratory
- Online Research Club collaborators
- [Any other acknowledgments]

---

*Last updated: December 2025*
