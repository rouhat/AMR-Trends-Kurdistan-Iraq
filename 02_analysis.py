#!/usr/bin/env python3
"""
02_analysis.py
AMR Statistical Analysis

This script performs statistical analysis on the cleaned AMR data
including resistance rate calculations, trend analysis, and MDR prevalence.
"""

import pandas as pd
import numpy as np
from scipy import stats
from collections import defaultdict
import warnings
import os

warnings.filterwarnings('ignore')

# Configuration
PROCESSED_DATA_PATH = '../data/processed/'
RESULTS_PATH = '../results/tables/'


def calculate_resistance_rates(df, antibiotic_cols, organism=None, year=None):
    """
    Calculate resistance rates for specified antibiotics.
    
    Parameters:
    -----------
    df : DataFrame
        Cleaned AMR data
    antibiotic_cols : list
        List of antibiotic column names
    organism : str, optional
        Filter by specific organism
    year : int, optional
        Filter by specific year
    
    Returns:
    --------
    dict : Resistance rates for each antibiotic
    """
    data = df.copy()
    
    if organism:
        data = data[data['organism'] == organism]
    if year:
        data = data[data['year'] == year]
    
    results = {}
    
    for abx in antibiotic_cols:
        if abx not in data.columns:
            continue
            
        # Filter out missing values
        valid = data[abx].dropna()
        total = len(valid)
        
        if total == 0:
            results[abx] = {'rate': np.nan, 'n_tested': 0, 'n_resistant': 0}
            continue
        
        n_resistant = (valid == 'Resistant').sum()
        n_intermediate = (valid == 'Intermediate').sum()
        n_sensitive = (valid == 'Sensitive').sum()
        
        resistance_rate = (n_resistant / total) * 100
        
        results[abx] = {
            'rate': round(resistance_rate, 1),
            'n_tested': total,
            'n_resistant': n_resistant,
            'n_intermediate': n_intermediate,
            'n_sensitive': n_sensitive,
            '95_ci_lower': round(proportion_ci(n_resistant, total)[0] * 100, 1),
            '95_ci_upper': round(proportion_ci(n_resistant, total)[1] * 100, 1)
        }
    
    return results


def proportion_ci(successes, total, confidence=0.95):
    """Calculate confidence interval for a proportion using Wilson score."""
    if total == 0:
        return (0, 0)
    
    p = successes / total
    z = stats.norm.ppf((1 + confidence) / 2)
    
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    spread = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2)) / denominator
    
    return (max(0, center - spread), min(1, center + spread))


def temporal_trend_analysis(df, antibiotic, organism=None):
    """
    Analyze temporal trends in resistance rates.
    
    Returns yearly resistance rates and trend statistics.
    """
    data = df.copy()
    
    if organism:
        data = data[data['organism'] == organism]
    
    if antibiotic not in data.columns:
        return None
    
    yearly_rates = []
    
    for year in sorted(data['year'].dropna().unique()):
        year_data = data[data['year'] == year][antibiotic].dropna()
        
        if len(year_data) == 0:
            continue
        
        n_resistant = (year_data == 'Resistant').sum()
        rate = (n_resistant / len(year_data)) * 100
        
        yearly_rates.append({
            'year': int(year),
            'rate': round(rate, 1),
            'n_tested': len(year_data),
            'n_resistant': n_resistant
        })
    
    if len(yearly_rates) < 3:
        return {'yearly_rates': yearly_rates, 'trend': None}
    
    # Calculate trend (linear regression)
    years = [r['year'] for r in yearly_rates]
    rates = [r['rate'] for r in yearly_rates]
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, rates)
    
    return {
        'yearly_rates': yearly_rates,
        'trend': {
            'slope': round(slope, 3),  # Change per year
            'r_squared': round(r_value**2, 3),
            'p_value': round(p_value, 4),
            'direction': 'increasing' if slope > 0 else 'decreasing',
            'significant': p_value < 0.05
        }
    }


def organism_distribution(df):
    """Calculate distribution of organisms in the dataset."""
    counts = df['organism'].value_counts()
    total = len(df)
    
    distribution = []
    for org, count in counts.items():
        if pd.isna(org):
            continue
        distribution.append({
            'organism': org,
            'count': count,
            'percentage': round((count / total) * 100, 1)
        })
    
    return distribution


def sample_type_distribution(df):
    """Calculate distribution of sample types."""
    counts = df['sample_type'].value_counts()
    total = len(df)
    
    distribution = []
    for sample, count in counts.items():
        if pd.isna(sample):
            continue
        distribution.append({
            'sample_type': sample,
            'count': count,
            'percentage': round((count / total) * 100, 1)
        })
    
    return distribution


def demographic_summary(df):
    """Generate demographic summary statistics."""
    summary = {
        'total_records': len(df),
        'unique_patients': df['record_id'].nunique() if 'record_id' in df.columns else len(df),
        'date_range': {
            'start': df['sample_date'].min(),
            'end': df['sample_date'].max()
        },
        'gender': {
            'female': (df['gender'] == 'Female').sum(),
            'male': (df['gender'] == 'Male').sum(),
            'unknown': df['gender'].isna().sum()
        },
        'age': {
            'mean': round(df['age'].mean(), 1),
            'median': df['age'].median(),
            'min': df['age'].min(),
            'max': df['age'].max()
        }
    }
    
    return summary


def calculate_mdr_prevalence(df):
    """Calculate MDR prevalence by organism and year."""
    if 'mdr_status' not in df.columns:
        return None
    
    # Overall MDR
    total = len(df)
    mdr_count = (df['mdr_status'] == 'MDR').sum()
    
    results = {
        'overall': {
            'mdr_count': mdr_count,
            'total': total,
            'rate': round((mdr_count / total) * 100, 1) if total > 0 else 0
        },
        'by_organism': [],
        'by_year': []
    }
    
    # By organism
    for org in df['organism'].dropna().unique():
        org_data = df[df['organism'] == org]
        org_total = len(org_data)
        org_mdr = (org_data['mdr_status'] == 'MDR').sum()
        
        if org_total > 0:
            results['by_organism'].append({
                'organism': org,
                'mdr_count': org_mdr,
                'total': org_total,
                'rate': round((org_mdr / org_total) * 100, 1)
            })
    
    # By year
    for year in sorted(df['year'].dropna().unique()):
        year_data = df[df['year'] == year]
        year_total = len(year_data)
        year_mdr = (year_data['mdr_status'] == 'MDR').sum()
        
        if year_total > 0:
            results['by_year'].append({
                'year': int(year),
                'mdr_count': year_mdr,
                'total': year_total,
                'rate': round((year_mdr / year_total) * 100, 1)
            })
    
    return results


def critical_resistance_alert(df, antibiotic_cols):
    """
    Identify critical resistance patterns requiring attention.
    
    Focus on:
    - Carbapenem resistance (CRE)
    - MRSA patterns
    - ESBL indicators
    - High fluoroquinolone resistance
    """
    alerts = []
    
    # Carbapenem resistance
    carbapenems = ['Imipenem', 'Meropenem']
    for carb in carbapenems:
        if carb in df.columns:
            valid = df[carb].dropna()
            if len(valid) > 0:
                rate = ((valid == 'Resistant').sum() / len(valid)) * 100
                if rate > 10:  # WHO threshold for concern
                    alerts.append({
                        'type': 'Carbapenem Resistance',
                        'antibiotic': carb,
                        'rate': round(rate, 1),
                        'severity': 'CRITICAL' if rate > 20 else 'HIGH'
                    })
    
    # Third-generation cephalosporin resistance (ESBL indicator)
    ceph3 = ['Ceftriaxone', 'Cefotaxime', 'Ceftazidime']
    for ceph in ceph3:
        if ceph in df.columns:
            # Focus on Enterobacteriaceae
            enterobact = df[df['organism'].isin(['Escherichia coli', 'Klebsiella spp.'])]
            valid = enterobact[ceph].dropna()
            if len(valid) > 0:
                rate = ((valid == 'Resistant').sum() / len(valid)) * 100
                if rate > 30:
                    alerts.append({
                        'type': 'ESBL Indicator',
                        'antibiotic': ceph,
                        'rate': round(rate, 1),
                        'severity': 'HIGH'
                    })
    
    # Fluoroquinolone resistance
    fq = ['Ciprofloxacin', 'Levofloxacin']
    for abx in fq:
        if abx in df.columns:
            valid = df[abx].dropna()
            if len(valid) > 0:
                rate = ((valid == 'Resistant').sum() / len(valid)) * 100
                if rate > 50:
                    alerts.append({
                        'type': 'High Fluoroquinolone Resistance',
                        'antibiotic': abx,
                        'rate': round(rate, 1),
                        'severity': 'MODERATE' if rate < 70 else 'HIGH'
                    })
    
    return alerts


def compare_with_global_data(resistance_rates):
    """
    Compare local rates with global/regional benchmarks.
    
    Benchmarks from WHO GLASS 2022 (approximate values).
    """
    global_benchmarks = {
        'Escherichia coli': {
            'Ciprofloxacin': {'global_median': 45, 'emro_median': 55},
            'Ceftriaxone': {'global_median': 30, 'emro_median': 40},
            'Amikacin': {'global_median': 5, 'emro_median': 10}
        },
        'Klebsiella spp.': {
            'Ciprofloxacin': {'global_median': 50, 'emro_median': 60},
            'Ceftriaxone': {'global_median': 45, 'emro_median': 55},
            'Meropenem': {'global_median': 10, 'emro_median': 20}
        },
        'Staphylococcus aureus': {
            'Oxacillin': {'global_median': 35, 'emro_median': 45},  # MRSA
            'Vancomycin': {'global_median': 0.5, 'emro_median': 1}
        }
    }
    
    comparisons = []
    
    for organism, benchmarks in global_benchmarks.items():
        if organism not in resistance_rates:
            continue
        
        for abx, bench in benchmarks.items():
            if abx in resistance_rates[organism]:
                local_rate = resistance_rates[organism][abx]['rate']
                global_med = bench['global_median']
                emro_med = bench['emro_median']
                
                comparisons.append({
                    'organism': organism,
                    'antibiotic': abx,
                    'local_rate': local_rate,
                    'global_median': global_med,
                    'emro_median': emro_med,
                    'vs_global': 'Higher' if local_rate > global_med else 'Lower',
                    'vs_emro': 'Higher' if local_rate > emro_med else 'Lower'
                })
    
    return comparisons


def generate_analysis_report(df, antibiotic_cols):
    """Generate comprehensive analysis report."""
    
    print("=" * 60)
    print("AMR ANALYSIS REPORT")
    print("Zakho General Emergency Hospital")
    print("=" * 60)
    
    # Demographics
    demo = demographic_summary(df)
    print(f"\n📊 DATASET OVERVIEW")
    print(f"   Total records: {demo['total_records']}")
    print(f"   Date range: {demo['date_range']['start']} to {demo['date_range']['end']}")
    print(f"   Female: {demo['gender']['female']} | Male: {demo['gender']['male']}")
    print(f"   Mean age: {demo['age']['mean']} years")
    
    # Organism distribution
    org_dist = organism_distribution(df)
    print(f"\n🦠 ORGANISM DISTRIBUTION")
    for item in org_dist[:5]:
        print(f"   {item['organism']}: {item['count']} ({item['percentage']}%)")
    
    # Sample types
    sample_dist = sample_type_distribution(df)
    print(f"\n🧪 SAMPLE TYPES")
    for item in sample_dist:
        print(f"   {item['sample_type']}: {item['count']} ({item['percentage']}%)")
    
    # Critical alerts
    alerts = critical_resistance_alert(df, antibiotic_cols)
    if alerts:
        print(f"\n⚠️  CRITICAL RESISTANCE ALERTS")
        for alert in alerts:
            print(f"   [{alert['severity']}] {alert['type']}: {alert['antibiotic']} = {alert['rate']}%")
    
    # MDR prevalence
    mdr = calculate_mdr_prevalence(df)
    if mdr:
        print(f"\n💊 MDR PREVALENCE")
        print(f"   Overall: {mdr['overall']['rate']}% ({mdr['overall']['mdr_count']}/{mdr['overall']['total']})")
    
    print("\n" + "=" * 60)
    print("Analysis complete. See results/tables/ for detailed data.")
    print("=" * 60)


def main():
    """Main analysis pipeline."""
    
    os.makedirs(RESULTS_PATH, exist_ok=True)
    
    print("=" * 60)
    print("AMR Statistical Analysis")
    print("=" * 60)
    
    print("\n[INFO] This script provides the analysis framework.")
    print("[INFO] Load your cleaned data and run the analysis functions.")
    
    # Example workflow (uncomment and modify for your data):
    """
    # 1. Load cleaned data
    df = pd.read_csv(f'{PROCESSED_DATA_PATH}amr_combined_clean.csv')
    
    # 2. Define antibiotic columns
    antibiotic_cols = ['Amikacin', 'Ampicillin', 'Ciprofloxacin', ...]
    
    # 3. Calculate overall resistance rates
    overall_rates = calculate_resistance_rates(df, antibiotic_cols)
    
    # 4. Calculate organism-specific rates
    ecoli_rates = calculate_resistance_rates(df, antibiotic_cols, organism='Escherichia coli')
    kleb_rates = calculate_resistance_rates(df, antibiotic_cols, organism='Klebsiella spp.')
    
    # 5. Temporal trend analysis
    cip_trend = temporal_trend_analysis(df, 'Ciprofloxacin')
    
    # 6. Generate report
    generate_analysis_report(df, antibiotic_cols)
    
    # 7. Save results
    pd.DataFrame(overall_rates).T.to_csv(f'{RESULTS_PATH}overall_resistance_rates.csv')
    """
    
    print("\n[DONE] Analysis framework ready.")


if __name__ == '__main__':
    main()
