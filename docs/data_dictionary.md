# Data Dictionary

## Overview
This document describes all variables in the AMR surveillance dataset.

---

## Patient Demographics

| Variable | Description | Values/Format |
|----------|-------------|---------------|
| `record_number` | Unique identifier for each isolate | Integer |
| `sample_date` | Date of sample collection | YYYY-MM-DD |
| `age` | Patient age in years | Integer (0-100+) |
| `gender` | Patient gender | Male, Female |

---

## Sample Information

| Variable | Description | Values |
|----------|-------------|--------|
| `sample_type` | Type of clinical specimen | Urine, Sputum, Swab, HVS, Wound swab, Ear swab, Throat swab |
| `site` | Anatomical site (for swabs) | Wound, Ear, Throat, Abdomen, HVS, etc. |
| `growth_result` | Culture result | Growth, No growth |

---

## Microbiology Results

| Variable | Description | Values |
|----------|-------------|--------|
| `organism` | Primary organism identified | See organism codes below |
| `other_organism` | Additional organism specification | Free text |

### Organism Codes

| Code | Full Name |
|------|-----------|
| E. coli | *Escherichia coli* |
| Klebsiella | *Klebsiella pneumoniae* / *Klebsiella* spp. |
| S. aureus | *Staphylococcus aureus* |
| Staphylococcus | *Staphylococcus* spp. (coagulase-negative) |
| Streptococcus | *Streptococcus* spp. |
| Pseudomonas | *Pseudomonas aeruginosa* |
| Proteus | *Proteus mirabilis* / *Proteus* spp. |
| Enterobacter | *Enterobacter* spp. |
| Enterococcus | *Enterococcus* spp. |
| Corynebacterium | *Corynebacterium* spp. |

---

## Antimicrobial Susceptibility Results

### Result Interpretation

| Code | Interpretation | Description |
|------|----------------|-------------|
| S | Sensitive | Organism is susceptible to the antibiotic |
| I | Intermediate | Reduced susceptibility; may respond to higher doses |
| R | Resistant | Organism is resistant to the antibiotic |
| IM | Intermediate | Alternative coding for intermediate |
| (blank) | Not Tested | Antibiotic was not tested for this isolate |

---

## Antibiotic Variables

### Penicillins
| Code | Full Name | Class |
|------|-----------|-------|
| AM | Ampicillin | Penicillin |
| AX | Amoxicillin | Penicillin |
| P | Penicillin G | Penicillin |

### Penicillin Combinations
| Code | Full Name | Class |
|------|-----------|-------|
| AMC | Amoxicillin/Clavulanic acid | β-lactam/β-lactamase inhibitor |
| SAM | Ampicillin/Sulbactam | β-lactam/β-lactamase inhibitor |
| TPZ | Piperacillin/Tazobactam | β-lactam/β-lactamase inhibitor |
| TIM | Ticarcillin/Clavulanic acid | β-lactam/β-lactamase inhibitor |

### Cephalosporins
| Code | Full Name | Generation |
|------|-----------|------------|
| KF | Cephalothin | 1st |
| CFR | Cefadroxil | 1st |
| FOX | Cefoxitin | 2nd |
| CFM | Cefixime | 3rd |
| CRO | Ceftriaxone | 3rd |
| CTX | Cefotaxime | 3rd |
| CAZ | Ceftazidime | 3rd |
| CPO/CPD | Cefpodoxime | 3rd |
| FEP | Cefepime | 4th |

### Carbapenems
| Code | Full Name | Class |
|------|-----------|-------|
| IPM | Imipenem | Carbapenem |
| MEM | Meropenem | Carbapenem |

### Monobactams
| Code | Full Name | Class |
|------|-----------|-------|
| ATM | Aztreonam | Monobactam |

### Aminoglycosides
| Code | Full Name | Class |
|------|-----------|-------|
| AK | Amikacin | Aminoglycoside |
| CN | Gentamicin | Aminoglycoside |
| TOB | Tobramycin | Aminoglycoside |
| NET | Netilmicin | Aminoglycoside |
| S | Streptomycin | Aminoglycoside |
| K | Kanamycin | Aminoglycoside |

### Fluoroquinolones
| Code | Full Name | Class |
|------|-----------|-------|
| CIP | Ciprofloxacin | Fluoroquinolone |
| LEV | Levofloxacin | Fluoroquinolone |
| NOR | Norfloxacin | Fluoroquinolone |
| OFX | Ofloxacin | Fluoroquinolone |
| NA | Nalidixic acid | Quinolone (1st gen) |

### Macrolides
| Code | Full Name | Class |
|------|-----------|-------|
| E | Erythromycin | Macrolide |
| AZM | Azithromycin | Macrolide |

### Tetracyclines
| Code | Full Name | Class |
|------|-----------|-------|
| TE | Tetracycline | Tetracycline |
| DO | Doxycycline | Tetracycline |
| TGC | Tigecycline | Glycylcycline |

### Glycopeptides
| Code | Full Name | Class |
|------|-----------|-------|
| VA | Vancomycin | Glycopeptide |
| TEC | Teicoplanin | Glycopeptide |

### Lincosamides
| Code | Full Name | Class |
|------|-----------|-------|
| DA | Clindamycin | Lincosamide |

### Oxazolidinones & Related
| Code | Full Name | Class |
|------|-----------|-------|
| CX | Cloxacillin | Isoxazolyl penicillin |
| OX | Oxacillin | Isoxazolyl penicillin |
| ME | Methicillin | Isoxazolyl penicillin |

### Other Antibiotics
| Code | Full Name | Class |
|------|-----------|-------|
| SXT | Trimethoprim/Sulfamethoxazole | Sulfonamide combination |
| TMP | Trimethoprim | Dihydrofolate reductase inhibitor |
| F | Nitrofurantoin | Nitrofuran |
| FF | Fosfomycin | Phosphonic acid |
| CL | Colistin | Polymyxin |
| PY | Polymyxin B | Polymyxin |
| RA | Rifampicin | Rifamycin |
| C | Chloramphenicol | Phenicol |
| MET | Metronidazole | Nitroimidazole |

---

## Data Quality Notes

1. **Missing Values**: Blank cells indicate the antibiotic was not tested
2. **Historical Data (2013-2022)**: Uses abbreviated codes (S, R, IM)
3. **Recent Data (2024-2025)**: Uses full descriptions (Sensitive, Resistant, Intermediate)
4. **Date Formats**: Historical data may have varied date formats requiring standardization

---

## MDR Definitions

### Multi-Drug Resistant (MDR)
Resistance to at least one agent in ≥3 antimicrobial categories

### Extensively Drug-Resistant (XDR)
Resistance to at least one agent in all but ≤2 antimicrobial categories

### Pan-Drug Resistant (PDR)
Resistance to all agents in all antimicrobial categories

---

*Last updated: December 2025*
