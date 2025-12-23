#!/usr/bin/env python3
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
