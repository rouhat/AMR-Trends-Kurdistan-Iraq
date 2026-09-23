#!/usr/bin/env python3
"""
03_visualizations.py
AMR Data Visualization

This script creates publication-quality visualizations for the AMR data
including trend plots, heatmaps, and organism distributions.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch
import warnings
import os

warnings.filterwarnings('ignore')

# Configuration
PROCESSED_DATA_PATH = '../data/processed/'
FIGURES_PATH = '../results/figures/'

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'Resistant': '#e74c3c',
    'Intermediate': '#f39c12',
    'Sensitive': '#27ae60',
    'primary': '#3498db',
    'secondary': '#9b59b6'
}

# Custom color palette for organisms
ORGANISM_COLORS = {
    'Escherichia coli': '#e74c3c',
    'Klebsiella spp.': '#3498db',
    'Staphylococcus aureus': '#f39c12',
    'Staphylococcus spp.': '#e67e22',
    'Streptococcus spp.': '#9b59b6',
    'Pseudomonas aeruginosa': '#1abc9c',
    'Proteus spp.': '#34495e',
    'Other': '#95a5a6'
}


def plot_resistance_trends(df, antibiotics, organism=None, save_path=None):
    """
    Plot resistance trends over time for specified antibiotics.
    
    Parameters:
    -----------
    df : DataFrame
        Cleaned AMR data with 'year' column
    antibiotics : list
        List of antibiotic column names to plot
    organism : str, optional
        Filter by specific organism
    save_path : str, optional
        Path to save the figure
    """
    data = df.copy()
    
    if organism:
        data = data[data['organism'] == organism]
        title_suffix = f' - {organism}'
    else:
        title_suffix = ' - All Organisms'
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    years = sorted(data['year'].dropna().unique())
    
    for abx in antibiotics:
        if abx not in data.columns:
            continue
        
        rates = []
        for year in years:
            year_data = data[data['year'] == year][abx].dropna()
            if len(year_data) > 0:
                rate = ((year_data == 'Resistant').sum() / len(year_data)) * 100
                rates.append(rate)
            else:
                rates.append(np.nan)
        
        ax.plot(years, rates, marker='o', linewidth=2, markersize=6, label=abx)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Resistance Rate (%)', fontsize=12)
    ax.set_title(f'Antimicrobial Resistance Trends (2013-2025){title_suffix}', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def plot_resistance_heatmap(df, antibiotics, organisms, save_path=None):
    """
    Create a heatmap showing resistance rates by organism and antibiotic.
    """
    # Calculate resistance rates
    heatmap_data = []
    
    for org in organisms:
        org_data = df[df['organism'] == org]
        row = {'Organism': org}
        
        for abx in antibiotics:
            if abx in org_data.columns:
                valid = org_data[abx].dropna()
                if len(valid) > 0:
                    rate = ((valid == 'Resistant').sum() / len(valid)) * 100
                    row[abx] = round(rate, 1)
                else:
                    row[abx] = np.nan
            else:
                row[abx] = np.nan
        
        heatmap_data.append(row)
    
    heatmap_df = pd.DataFrame(heatmap_data)
    heatmap_df.set_index('Organism', inplace=True)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(
        heatmap_df,
        annot=True,
        fmt='.0f',
        cmap='RdYlGn_r',
        center=50,
        vmin=0,
        vmax=100,
        linewidths=0.5,
        cbar_kws={'label': 'Resistance Rate (%)'},
        ax=ax
    )
    
    ax.set_title('Antimicrobial Resistance Rates by Organism', fontsize=14, fontweight='bold')
    ax.set_xlabel('Antibiotic', fontsize=12)
    ax.set_ylabel('Organism', fontsize=12)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def plot_organism_distribution(df, save_path=None):
    """
    Create pie chart showing organism distribution.
    """
    org_counts = df['organism'].value_counts()
    
    # Group small categories into 'Other'
    threshold = 0.03 * len(df)  # 3% threshold
    major = org_counts[org_counts >= threshold]
    other = org_counts[org_counts < threshold].sum()
    
    if other > 0:
        major['Other'] = other
    
    # Colors
    colors = [ORGANISM_COLORS.get(org, '#95a5a6') for org in major.index]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    wedges, texts, autotexts = ax.pie(
        major.values,
        labels=major.index,
        autopct='%1.1f%%',
        colors=colors,
        explode=[0.02] * len(major),
        shadow=False,
        startangle=90
    )
    
    ax.set_title('Distribution of Bacterial Isolates', fontsize=14, fontweight='bold')
    
    # Add legend
    ax.legend(
        wedges, 
        [f'{org} (n={count})' for org, count in zip(major.index, major.values)],
        title='Organisms',
        loc='center left',
        bbox_to_anchor=(1, 0.5)
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def plot_yearly_isolates(df, save_path=None):
    """
    Bar plot showing number of isolates per year.
    """
    yearly_counts = df.groupby('year').size()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(yearly_counts.index, yearly_counts.values, color=COLORS['primary'], edgecolor='white')
    
    # Add value labels on bars
    for bar, val in zip(bars, yearly_counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            str(int(val)),
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Isolates', fontsize=12)
    ax.set_title('Bacterial Isolates by Year', fontsize=14, fontweight='bold')
    ax.set_xticks(yearly_counts.index)
    ax.set_xticklabels([str(int(y)) for y in yearly_counts.index], rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def plot_critical_resistance_bar(df, antibiotics, save_path=None):
    """
    Horizontal bar chart for critical antibiotic resistance rates.
    """
    rates = []
    
    for abx in antibiotics:
        if abx in df.columns:
            valid = df[abx].dropna()
            if len(valid) > 0:
                rate = ((valid == 'Resistant').sum() / len(valid)) * 100
                rates.append({'antibiotic': abx, 'rate': rate})
    
    rates_df = pd.DataFrame(rates).sort_values('rate', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Color based on resistance level
    colors = []
    for rate in rates_df['rate']:
        if rate >= 50:
            colors.append('#e74c3c')  # High - red
        elif rate >= 25:
            colors.append('#f39c12')  # Medium - orange
        else:
            colors.append('#27ae60')  # Low - green
    
    bars = ax.barh(rates_df['antibiotic'], rates_df['rate'], color=colors, edgecolor='white')
    
    # Add value labels
    for bar, val in zip(bars, rates_df['rate']):
        ax.text(
            val + 1,
            bar.get_y() + bar.get_height() / 2,
            f'{val:.1f}%',
            ha='left',
            va='center',
            fontsize=10
        )
    
    ax.set_xlabel('Resistance Rate (%)', fontsize=12)
    ax.set_title('Overall Antimicrobial Resistance Rates', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 110)
    
    # Add legend
    legend_elements = [
        Patch(facecolor='#e74c3c', label='High (≥50%)'),
        Patch(facecolor='#f39c12', label='Medium (25-49%)'),
        Patch(facecolor='#27ae60', label='Low (<25%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def plot_sample_type_distribution(df, save_path=None):
    """
    Bar chart showing distribution of sample types.
    """
    sample_counts = df['sample_type'].value_counts()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(sample_counts.index, sample_counts.values, color=COLORS['secondary'], edgecolor='white')
    
    # Add value labels
    for bar, val in zip(bars, sample_counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(int(val)),
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    ax.set_xlabel('Sample Type', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Clinical Specimens', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def plot_mdr_trends(df, save_path=None):
    """
    Plot MDR prevalence trends over time.
    """
    if 'mdr_status' not in df.columns:
        print("MDR status not calculated. Run data cleaning first.")
        return
    
    yearly_mdr = []
    
    for year in sorted(df['year'].dropna().unique()):
        year_data = df[df['year'] == year]
        total = len(year_data)
        mdr_count = (year_data['mdr_status'] == 'MDR').sum()
        
        if total > 0:
            yearly_mdr.append({
                'year': int(year),
                'rate': (mdr_count / total) * 100,
                'count': mdr_count,
                'total': total
            })
    
    mdr_df = pd.DataFrame(yearly_mdr)
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Bar chart for counts
    bars = ax1.bar(mdr_df['year'], mdr_df['count'], color=COLORS['Resistant'], alpha=0.7, label='MDR Count')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('MDR Isolate Count', fontsize=12, color=COLORS['Resistant'])
    ax1.tick_params(axis='y', labelcolor=COLORS['Resistant'])
    
    # Line chart for percentage
    ax2 = ax1.twinx()
    ax2.plot(mdr_df['year'], mdr_df['rate'], 'o-', color=COLORS['primary'], linewidth=2, markersize=8, label='MDR Rate')
    ax2.set_ylabel('MDR Rate (%)', fontsize=12, color=COLORS['primary'])
    ax2.tick_params(axis='y', labelcolor=COLORS['primary'])
    ax2.set_ylim(0, 100)
    
    ax1.set_title('Multi-Drug Resistant (MDR) Isolates Over Time', fontsize=14, fontweight='bold')
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.close()


def create_all_visualizations(df, antibiotic_cols):
    """Generate all standard visualizations."""
    
    os.makedirs(FIGURES_PATH, exist_ok=True)
    
    print("=" * 60)
    print("Generating Visualizations")
    print("=" * 60)
    
    # 1. Organism distribution
    print("\n📊 Creating organism distribution chart...")
    plot_organism_distribution(df, f'{FIGURES_PATH}organism_distribution.png')
    
    # 2. Yearly isolates
    print("📊 Creating yearly isolates chart...")
    plot_yearly_isolates(df, f'{FIGURES_PATH}yearly_isolates.png')
    
    # 3. Sample type distribution
    print("📊 Creating sample type distribution...")
    plot_sample_type_distribution(df, f'{FIGURES_PATH}sample_type_distribution.png')
    
    # 4. Overall resistance rates
    print("📊 Creating resistance rates bar chart...")
    plot_critical_resistance_bar(df, antibiotic_cols, f'{FIGURES_PATH}resistance_rates_overall.png')
    
    # 5. Resistance heatmap
    print("📊 Creating resistance heatmap...")
    organisms = ['Escherichia coli', 'Klebsiella spp.', 'Staphylococcus aureus', 
                 'Staphylococcus spp.', 'Streptococcus spp.', 'Pseudomonas aeruginosa']
    plot_resistance_heatmap(df, antibiotic_cols[:15], organisms, f'{FIGURES_PATH}resistance_heatmap.png')
    
    # 6. Resistance trends
    print("📊 Creating resistance trend plots...")
    key_antibiotics = ['Ciprofloxacin', 'Amikacin', 'Ceftriaxone', 'Meropenem', 'Vancomycin']
    key_abx_in_data = [a for a in key_antibiotics if a in antibiotic_cols]
    if key_abx_in_data:
        plot_resistance_trends(df, key_abx_in_data, save_path=f'{FIGURES_PATH}resistance_trends.png')
    
    # 7. MDR trends
    print("📊 Creating MDR trend plot...")
    plot_mdr_trends(df, f'{FIGURES_PATH}mdr_trends.png')
    
    print("\n" + "=" * 60)
    print(f"All visualizations saved to {FIGURES_PATH}")
    print("=" * 60)


def main():
    """Main visualization pipeline."""
    
    os.makedirs(FIGURES_PATH, exist_ok=True)
    
    print("=" * 60)
    print("AMR Visualization Pipeline")
    print("=" * 60)
    
    print("\n[INFO] This script provides the visualization framework.")
    print("[INFO] Load your cleaned data and run the visualization functions.")
    
    # Example workflow (uncomment and modify for your data):
    """
    # 1. Load cleaned data
    df = pd.read_csv(f'{PROCESSED_DATA_PATH}amr_combined_clean.csv')
    df['sample_date'] = pd.to_datetime(df['sample_date'])
    
    # 2. Define antibiotic columns
    antibiotic_cols = ['Amikacin', 'Ampicillin', 'Ciprofloxacin', 
                       'Gentamicin', 'Ceftriaxone', 'Meropenem', ...]
    
    # 3. Generate all visualizations
    create_all_visualizations(df, antibiotic_cols)
    """
    
    print("\n[DONE] Visualization framework ready.")


if __name__ == '__main__':
    main()
