#!/usr/bin/env python3
"""
01_data_cleaning.py
AMR surveillance pipeline - Zakho General Emergency Hospital (2013-2025)

Reads both sheets of the raw workbook, harmonises the two antibiotic
code sets, and produces organism-specific resistance rates with
per-antibiotic denominators and Wilson 95% confidence intervals.

Key difference from the previous version: missing values are dropped
PER ANTIBIOTIC, not per row. A row tested against 6 agents still
contributes those 6 results instead of being discarded entirely.

Usage:  python 01_data_cleaning.py
"""

import os
import math
import pandas as pd

# ---------------------------------------------------------------- config

RAW_FILE = "data/raw/amr_data.xlsx"   # <-- set to your uploaded filename
OUT_DIR = "results/tables"

# CLSI M39 suggests ~30 isolates before reporting a percentage.
MIN_N_FOR_RATE = 30

# ------------------------------------------------- antibiotic code maps

# Codes we are confident about. Anything not listed here is reported
# as unmapped rather than guessed.
CODE_MAP = {
    "AK": "Amikacin", "AM": "Ampicillin", "AMC": "Amoxicillin-Clavulanate",
    "AX": "Amoxicillin", "AZM": "Azithromycin", "ATM": "Aztreonam",
    "C": "Chloramphenicol", "CAZ": "Ceftazidime", "CFM": "Cefixime",
    "CFR": "Cefadroxil", "CIP": "Ciprofloxacin", "CL": "Colistin",
    "CN": "Gentamicin", "GN": "Gentamicin", "CRO": "Ceftriaxone",
    "CTX": "Cefotaxime", "CX": "Cloxacillin", "DA": "Clindamycin",
    "DO": "Doxycycline", "E": "Erythromycin", "F": "Nitrofurantoin",
    "NI": "Nitrofurantoin", "FEP": "Cefepime", "FF": "Fosfomycin",
    "FOX": "Cefoxitin", "IPM": "Imipenem", "K": "Kanamycin",
    "KF": "Cephalothin", "LEV": "Levofloxacin", "MEM": "Meropenem",
    "NA": "Nalidixic acid", "NET": "Netilmicin", "NOR": "Norfloxacin",
    "OFX": "Ofloxacin", "OX": "Oxacillin", "P": "Penicillin",
    "PRL": "Piperacillin", "RA": "Rifampicin", "S": "Streptomycin",
    "SAM": "Ampicillin-Sulbactam", "SXT": "Trimethoprim-Sulfamethoxazole",
    "TE": "Tetracycline", "TEC": "Teicoplanin", "TGC": "Tigecycline",
    "TIM": "Ticarcillin-Clavulanate", "TMP": "Trimethoprim",
    "TOB": "Tobramycin", "TPZ": "Piperacillin-Tazobactam",
    "VA": "Vancomycin", "MET": "Metronidazole",
}

# Deliberately NOT mapped - confirm with the laboratory first:
#   AME, AUG, CAN, CEO, MEIL, MEK, MPM, NRO, TPM, AZT
#   CFX  (sheet 1 labels both CFX and CTX as cefotaxime)
#   CPO / CPD (both labelled cefpodoxime)
UNRESOLVED = {"AME", "AUG", "CAN", "CEO", "MEIL", "MEK", "MPM",
              "NRO", "TPM", "AZT", "CFX", "CPO", "CPD"}

# Agents that disk diffusion cannot reliably test (CLSI M100).
# Kept in the output but flagged, so they are not reported as findings.
UNRELIABLE_BY_DISK = {"Polymyxin B", "Colistin", "Methicillin"}

ORGANISM_PATTERNS = [
    ("coli", "Escherichia coli"),
    ("klebsiella", "Klebsiella spp."),
    ("aureus", "Staphylococcus aureus"),
    ("staph", "Staphylococcus spp."),
    ("strept", "Streptococcus spp."),
    ("pseudomonas", "Pseudomonas aeruginosa"),
    ("psuedomonas", "Pseudomonas aeruginosa"),
    ("proteus", "Proteus spp."),
    ("enterobacter", "Enterobacter spp."),
    ("enterococ", "Enterococcus spp."),
    ("coryn", "Corynebacterium spp."),
    ("candida", "Candida spp."),
]

SENSITIVE, RESISTANT, INTERMEDIATE = "S", "R", "I"


# ------------------------------------------------------------- helpers

def code_from_header(header):
    """'AK - Amikacin' -> 'AK';  ' CN ' -> 'CN';  'NET_Netilmicin' -> 'NET'."""
    h = str(header).strip()
    for sep in (" - ", "-", "_"):
        if sep in h:
            h = h.split(sep)[0]
            break
    return h.strip().upper()


def standardise_result(val):
    """Map a susceptibility cell to S / I / R, or None if not tested."""
    if val is None:
        return None
    v = str(val).strip().upper()
    if v in ("", "NAN", "NOT TESTED", "NT", "-"):
        return None
    if v.startswith("S") or "SENSITIVE" in v or "SUSCEPT" in v:
        return SENSITIVE
    if v.startswith("R") or "RESISTANT" in v:
        return RESISTANT
    if v.startswith("I") or "INTERMEDIATE" in v:
        return INTERMEDIATE
    return None


def standardise_organism(val):
    if val is None:
        return None
    v = str(val).strip()
    if v == "" or v.upper() in ("NAN", "NO GROWTH", "NONE"):
        return None
    low = v.lower()
    for pattern, name in ORGANISM_PATTERNS:
        if pattern in low:
            return name
    return v.title()


def wilson_ci(successes, n, z=1.96):
    """Wilson score interval - behaves sensibly at small n and at 0% or 100%."""
    if n == 0:
        return (None, None)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(100 * max(0.0, centre - half), 1),
            round(100 * min(1.0, centre + half), 1))


def find_column(columns, *candidates):
    """Locate a metadata column by fuzzy name match."""
    for cand in candidates:
        for col in columns:
            if cand.lower() in str(col).strip().lower():
                return col
    return None


# ------------------------------------------------------------- loading

def load_sheet(path, sheet):
    """Read one sheet to long format: one row per isolate-antibiotic result."""
    # keep_default_na=False stops pandas reading the 'NA' (nalidixic acid)
    # column header and blank cells as missing values.
    df = pd.read_excel(path, sheet_name=sheet, dtype=str,
                       keep_default_na=False, na_values=[])

    cols = list(df.columns)
    col_org = find_column(cols, "organism identified", "bacteria", "organism")
    col_other = find_column(cols, "other organism")
    col_age = find_column(cols, "age")
    col_sex = find_column(cols, "gender", "sex")
    col_sample = find_column(cols, "sample type", "sample")
    col_date = find_column(cols, "collection date", "date")
    col_growth = find_column(cols, "growth result")
    col_id = find_column(cols, "record number", "no.")

    meta_cols = {c for c in (col_org, col_other, col_age, col_sex, col_sample,
                             col_date, col_growth, col_id) if c}
    # Anything else that resolves to a known code is an antibiotic column.
    abx_cols = {}
    unmapped = {}
    for col in cols:
        if col in meta_cols:
            continue
        code = code_from_header(col)
        if code in CODE_MAP:
            abx_cols[col] = CODE_MAP[code]
        elif code in UNRESOLVED:
            unmapped[col] = code
        elif code and not code.startswith("_") and code not in ("ADDITIONAL NOTES",):
            unmapped[col] = code

    records = []
    for idx, row in df.iterrows():
        growth = str(row[col_growth]).strip().lower() if col_growth else ""
        if "no growth" in growth:
            continue

        organism = standardise_organism(row[col_org]) if col_org else None
        if organism is None and col_other:
            organism = standardise_organism(row[col_other])
        if organism is None:
            organism = "Unspecified"

        year = None
        if col_date:
            parsed = pd.to_datetime(str(row[col_date]).strip(),
                                    dayfirst=True, errors="coerce")
            if pd.notna(parsed):
                year = parsed.year

        base = {
            "sheet": sheet,
            "isolate_id": f"{sheet}_{idx:05d}",
            "year": year,
            "organism": organism,
            "sample_type": str(row[col_sample]).strip().title() if col_sample else None,
        }

        for col, abx in abx_cols.items():
            result = standardise_result(row[col])
            if result is None:          # not tested - skip this pair only
                continue
            records.append({**base, "antibiotic": abx, "result": result})

    return pd.DataFrame(records), unmapped


# ------------------------------------------------------------ analysis

def resistance_table(long_df, by_organism=True):
    keys = ["organism", "antibiotic"] if by_organism else ["antibiotic"]
    rows = []
    for key, grp in long_df.groupby(keys):
        n = len(grp)
        n_r = int((grp["result"] == RESISTANT).sum())
        n_i = int((grp["result"] == INTERMEDIATE).sum())
        lo, hi = wilson_ci(n_r, n)
        entry = dict(zip(keys, key if isinstance(key, tuple) else (key,)))
        entry.update({
            "n_tested": n,
            "n_resistant": n_r,
            "n_intermediate": n_i,
            "pct_resistant": round(100 * n_r / n, 1) if n else None,
            "pct_non_susceptible": round(100 * (n_r + n_i) / n, 1) if n else None,
            "ci95_low": lo,
            "ci95_high": hi,
            "reportable": n >= MIN_N_FOR_RATE,
            "disk_unreliable": entry.get("antibiotic") in UNRELIABLE_BY_DISK,
        })
        rows.append(entry)
    out = pd.DataFrame(rows)
    return out.sort_values(keys).reset_index(drop=True)


def yearly_trend(long_df, antibiotic, organism=None):
    sel = long_df[long_df["antibiotic"] == antibiotic]
    if organism:
        sel = sel[sel["organism"] == organism]
    rows = []
    for year, grp in sel.dropna(subset=["year"]).groupby("year"):
        n = len(grp)
        n_r = int((grp["result"] == RESISTANT).sum())
        lo, hi = wilson_ci(n_r, n)
        rows.append({
            "year": int(year), "antibiotic": antibiotic,
            "organism": organism or "All", "n_tested": n, "n_resistant": n_r,
            "pct_resistant": round(100 * n_r / n, 1),
            "ci95_low": lo, "ci95_high": hi,
            "reportable": n >= 10,
        })
    return pd.DataFrame(rows).sort_values("year")


# ----------------------------------------------------------------- main

def main():
    if not os.path.exists(RAW_FILE):
        raise SystemExit(f"Cannot find {RAW_FILE} - edit RAW_FILE at the top.")

    os.makedirs(OUT_DIR, exist_ok=True)
    sheets = pd.ExcelFile(RAW_FILE).sheet_names
    print(f"Sheets found: {sheets}\n")

    frames, all_unmapped = [], {}
    for sheet in sheets:
        df, unmapped = load_sheet(RAW_FILE, sheet)
        print(f"  {sheet}: {df['isolate_id'].nunique()} isolates, "
              f"{len(df)} isolate-antibiotic results")
        frames.append(df)
        all_unmapped[sheet] = unmapped

    long_df = pd.concat(frames, ignore_index=True)

    print(f"\nTotal isolates:            {long_df['isolate_id'].nunique()}")
    print(f"Total results:             {len(long_df)}")
    yrs = long_df["year"].dropna()
    if len(yrs):
        print(f"Year range:                {int(yrs.min())} - {int(yrs.max())}")

    print("\nIsolates per organism:")
    counts = long_df.groupby("organism")["isolate_id"].nunique().sort_values(ascending=False)
    for org, n in counts.items():
        flag = "" if n >= MIN_N_FOR_RATE else "   (below reporting threshold)"
        print(f"  {org:<32} {n:>5}{flag}")

    print("\nUnmapped antibiotic columns - confirm these with the laboratory:")
    for sheet, unmapped in all_unmapped.items():
        for col, code in sorted(unmapped.items(), key=lambda x: x[1]):
            print(f"  [{sheet}] {code:<8} (column: {str(col).strip()})")

    long_df.to_csv(f"{OUT_DIR}/isolate_antibiotic_long.csv", index=False)
    resistance_table(long_df, by_organism=True).to_csv(
        f"{OUT_DIR}/resistance_by_organism.csv", index=False)
    resistance_table(long_df, by_organism=False).to_csv(
        f"{OUT_DIR}/resistance_overall.csv", index=False)

    for abx in ("Ciprofloxacin", "Imipenem", "Meropenem", "Ceftriaxone"):
        for org in ("Escherichia coli", "Klebsiella spp."):
            t = yearly_trend(long_df, abx, org)
            if len(t):
                slug = f"{abx}_{org.split()[0]}".lower()
                t.to_csv(f"{OUT_DIR}/trend_{slug}.csv", index=False)

    print(f"\nWritten to {OUT_DIR}/")


if __name__ == "__main__":
    main()#!/usr/bin/env python3
"""
01_data_cleaning.py
AMR Data Cleaning Pipeline

This script cleans and standardizes the raw AMR surveillance data
from Zakho General Emergency Hospital (2013-2025).
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

# Configuration
RAW_DATA_PATH = '../data/raw/'
PROCESSED_DATA_PATH = '../data/processed/'

# Standardized antibiotic mapping (old codes to new)
ANTIBIOTIC_MAP = {
    'AK': 'Amikacin', 'AM': 'Ampicillin', 'AMC': 'Amoxicillin-Clavulanate',
    'AX': 'Amoxicillin', 'AZT': 'Aztreonam', 'AZM': 'Azithromycin',
    'C': 'Chloramphenicol', 'CAN': 'Cefadroxil', 'CAZ': 'Ceftazidime',
    'CEO': 'Cefoxitin', 'CFM': 'Cefixime', 'CFR': 'Cefadroxil',
    'CFX': 'Cefotaxime', 'CIP': 'Ciprofloxacin', 'CL': 'Colistin',
    'CN': 'Gentamicin', 'CRO': 'Ceftriaxone', 'CTX': 'Cefotaxime',
    'CX': 'Cloxacillin', 'DA': 'Clindamycin', 'DO': 'Doxycycline',
    'E': 'Erythromycin', 'F': 'Nitrofurantoin', 'FEP': 'Cefepime',
    'FF': 'Fosfomycin', 'FOX': 'Cefoxitin', 'GN': 'Gentamicin',
    'IPM': 'Imipenem', 'K': 'Kanamycin', 'KF': 'Cephalothin',
    'LEV': 'Levofloxacin', 'MEM': 'Meropenem', 'MET': 'Metronidazole',
    'NA': 'Nalidixic acid', 'NET': 'Netilmicin', 'NI': 'Nitrofurantoin',
    'NOR': 'Norfloxacin', 'OFX': 'Ofloxacin', 'OX': 'Oxacillin',
    'P': 'Penicillin', 'PRL': 'Piperacillin', 'PY': 'Polymyxin B',
    'RA': 'Rifampicin', 'S': 'Streptomycin', 'SAM': 'Ampicillin-Sulbactam',
    'SXT': 'Trimethoprim-Sulfamethoxazole', 'TE': 'Tetracycline',
    'TEC': 'Teicoplanin', 'TGC': 'Tigecycline', 'TIM': 'Ticarcillin-Clavulanate',
    'TMP': 'Trimethoprim', 'TOB': 'Tobramycin', 'TPZ': 'Piperacillin-Tazobactam',
    'VA': 'Vancomycin', 'ATM': 'Aztreonam', 'CPO': 'Cefpodoxime', 'CPD': 'Cefpodoxime',
    'ME': 'Methicillin'
}

# Standardized result mapping
RESULT_MAP = {
    'S': 'Sensitive', 's': 'Sensitive', 'Sensitive (S)': 'Sensitive',
    'R': 'Resistant', 'r': 'Resistant', 'Resistant (R)': 'Resistant',
    'I': 'Intermediate', 'IM': 'Intermediate', 'im': 'Intermediate',
    'Intermediate (I)': 'Intermediate',
    'Not Tested': np.nan, '': np.nan, ' ': np.nan
}

# Standardized organism mapping
ORGANISM_MAP = {
    'E.coli': 'Escherichia coli', 'E. coli': 'Escherichia coli',
    'Ecoli': 'Escherichia coli', 'e.coli': 'Escherichia coli',
    'Klebsiella': 'Klebsiella spp.', 'klebsiella': 'Klebsiella spp.',
    'Kle bsiella': 'Klebsiella spp.',
    'Staphylococcus': 'Staphylococcus spp.', 'staphylococcus': 'Staphylococcus spp.',
    'Staphylococcus aureus': 'Staphylococcus aureus',
    'S. aureus': 'Staphylococcus aureus',
    'staph': 'Staphylococcus spp.', 'Staph': 'Staphylococcus spp.',
    'Streptococcus': 'Streptococcus spp.', 'streptococcus': 'Streptococcus spp.',
    'Streptococcus pyogen': 'Streptococcus pyogenes',
    'Strept': 'Streptococcus spp.', 'strept': 'Streptococcus spp.',
    'Pseudomonas': 'Pseudomonas aeruginosa', 'Psuedomonas': 'Pseudomonas aeruginosa',
    'psuedomonas': 'Pseudomonas aeruginosa',
    'Proteus': 'Proteus spp.', 'proteus': 'Proteus spp.',
    'Enterobacter': 'Enterobacter spp.',
    'Enterococcus': 'Enterococcus spp.',
    'Corynbacterium': 'Corynebacterium spp.', 'Corynebacterium': 'Corynebacterium spp.',
    'corynbacterium': 'Corynebacterium spp.'
}


def standardize_date(date_val):
    """Convert various date formats to standard datetime."""
    if pd.isna(date_val):
        return np.nan
    
    date_str = str(date_val).strip()
    
    # Try multiple date formats
    formats = [
        '%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%d.%m.%y',
        '%d,%m,%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d'
    ]
    
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    
    # Try pandas default parsing
    try:
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        return np.nan


def standardize_result(val):
    """Standardize susceptibility result values."""
    if pd.isna(val):
        return np.nan
    
    val_str = str(val).strip()
    
    # Direct mapping
    if val_str in RESULT_MAP:
        return RESULT_MAP[val_str]
    
    # Check for patterns
    val_upper = val_str.upper()
    if 'SENSITIVE' in val_upper or val_upper == 'S':
        return 'Sensitive'
    elif 'RESISTANT' in val_upper or val_upper == 'R':
        return 'Resistant'
    elif 'INTERMEDIATE' in val_upper or val_upper in ['I', 'IM']:
        return 'Intermediate'
    
    return np.nan


def standardize_organism(val):
    """Standardize organism names."""
    if pd.isna(val):
        return np.nan
    
    val_str = str(val).strip()
    
    # Direct mapping
    if val_str in ORGANISM_MAP:
        return ORGANISM_MAP[val_str]
    
    # Partial matching
    val_lower = val_str.lower()
    if 'coli' in val_lower:
        return 'Escherichia coli'
    elif 'klebsiella' in val_lower:
        return 'Klebsiella spp.'
    elif 'aureus' in val_lower:
        return 'Staphylococcus aureus'
    elif 'staphylococ' in val_lower or 'staph' in val_lower:
        return 'Staphylococcus spp.'
    elif 'streptococ' in val_lower or 'strept' in val_lower:
        return 'Streptococcus spp.'
    elif 'pseudomonas' in val_lower or 'psuedomonas' in val_lower:
        return 'Pseudomonas aeruginosa'
    elif 'proteus' in val_lower:
        return 'Proteus spp.'
    elif 'enterobacter' in val_lower:
        return 'Enterobacter spp.'
    elif 'enterococ' in val_lower:
        return 'Enterococcus spp.'
    elif 'coryn' in val_lower:
        return 'Corynebacterium spp.'
    
    return val_str


def standardize_gender(val):
    """Standardize gender values."""
    if pd.isna(val):
        return np.nan
    
    val_str = str(val).strip().upper()
    
    if val_str in ['F', 'FEMALE']:
        return 'Female'
    elif val_str in ['M', 'MALE']:
        return 'Male'
    
    return np.nan


def standardize_sample_type(val):
    """Standardize sample type names."""
    if pd.isna(val):
        return np.nan
    
    val_str = str(val).strip().lower()
    
    if 'urine' in val_str:
        return 'Urine'
    elif 'sputum' in val_str:
        return 'Sputum'
    elif 'wound' in val_str:
        return 'Wound swab'
    elif 'ear' in val_str:
        return 'Ear swab'
    elif 'hvs' in val_str or 'high vaginal' in val_str:
        return 'HVS'
    elif 'throat' in val_str:
        return 'Throat swab'
    elif 'swab' in val_str:
        return 'Swab'
    elif 'pus' in val_str:
        return 'Pus'
    
    return val_str.title()


def clean_age(val):
    """Clean and validate age values."""
    if pd.isna(val):
        return np.nan
    
    try:
        age = float(val)
        if 0 <= age <= 120:
            return int(age)
        elif age < 0:
            # Handle negative ages (data entry error)
            return abs(int(age))
        else:
            return np.nan
    except:
        return np.nan


def extract_year(date_val):
    """Extract year from date for temporal analysis."""
    if pd.isna(date_val):
        return np.nan
    try:
        return date_val.year
    except:
        return np.nan


def create_unique_id(df, prefix='AMR'):
    """Create unique record identifiers."""
    return [f"{prefix}_{i:05d}" for i in range(1, len(df) + 1)]


def calculate_mdr_status(row, antibiotic_cols):
    """
    Calculate MDR status based on resistance to multiple antibiotic classes.
    MDR = Resistant to ≥1 agent in ≥3 antimicrobial categories
    """
    # Define antibiotic classes
    classes = {
        'Penicillins': ['Ampicillin', 'Amoxicillin', 'Penicillin'],
        'Cephalosporins': ['Ceftriaxone', 'Cefotaxime', 'Ceftazidime', 'Cefepime', 'Cefixime'],
        'Carbapenems': ['Imipenem', 'Meropenem'],
        'Aminoglycosides': ['Amikacin', 'Gentamicin', 'Tobramycin'],
        'Fluoroquinolones': ['Ciprofloxacin', 'Levofloxacin', 'Norfloxacin'],
        'Tetracyclines': ['Tetracycline', 'Doxycycline'],
        'Sulfonamides': ['Trimethoprim-Sulfamethoxazole'],
        'Glycopeptides': ['Vancomycin'],
        'Macrolides': ['Erythromycin', 'Azithromycin']
    }
    
    resistant_classes = 0
    
    for class_name, antibiotics in classes.items():
        for abx in antibiotics:
            if abx in antibiotic_cols and row.get(abx) == 'Resistant':
                resistant_classes += 1
                break
    
    if resistant_classes >= 3:
        return 'MDR'
    elif resistant_classes >= 1:
        return 'Resistant'
    else:
        return 'Susceptible'


def main():
    """Main data cleaning pipeline."""
    print("=" * 60)
    print("AMR Data Cleaning Pipeline")
    print("Zakho General Emergency Hospital (2013-2025)")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    
    # Note: In practice, load your actual data files here
    # df_historical = pd.read_excel(f'{RAW_DATA_PATH}amr_data_2013_2022.xlsx')
    # df_recent = pd.read_csv(f'{RAW_DATA_PATH}amr_data_2024_2025.csv')
    
    print("\n[INFO] This script provides the data cleaning framework.")
    print("[INFO] Load your raw data files and run the cleaning functions.")
    
    # Example workflow (uncomment and modify for your data):
    """
    # 1. Load data
    df = pd.read_excel('your_data.xlsx')
    
    # 2. Standardize dates
    df['sample_date'] = df['Date'].apply(standardize_date)
    df['year'] = df['sample_date'].apply(extract_year)
    
    # 3. Standardize demographics
    df['gender'] = df['Sex'].apply(standardize_gender)
    df['age'] = df['Age'].apply(clean_age)
    
    # 4. Standardize sample info
    df['sample_type'] = df['Sample'].apply(standardize_sample_type)
    df['organism'] = df['Bacteria'].apply(standardize_organism)
    
    # 5. Standardize susceptibility results
    antibiotic_cols = ['AK', 'AM', 'AMC', 'CIP', 'CN', ...]  # Your columns
    for col in antibiotic_cols:
        df[col] = df[col].apply(standardize_result)
    
    # 6. Create unique IDs
    df['record_id'] = create_unique_id(df)
    
    # 7. Calculate MDR status
    df['mdr_status'] = df.apply(
        lambda row: calculate_mdr_status(row, antibiotic_cols), axis=1
    )
    
    # 8. Save cleaned data
    df.to_csv(f'{PROCESSED_DATA_PATH}amr_combined_clean.csv', index=False)
    
    # 9. Generate summary
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['year'].min()} - {df['year'].max()}")
    print(f"Organisms: {df['organism'].nunique()}")
    """
    
    print("\n[DONE] Data cleaning framework ready.")
    print("=" * 60)


if __name__ == '__main__':
    main()
