import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
import os

# ==============================================================================
# Standalone, Presentation-Ready Plotting Functions
# ==============================================================================

def _create_mismatch_barcharts(df: pd.DataFrame, filepath: str, save_kwds: dict):
    """Generates and saves the side-by-side mismatch counts and rates."""
    mismatches = df[df['Discrepancy'] == 'Yes']
    total = df['file_type'].value_counts()
    mismatch_counts = mismatches['file_type'].value_counts().reindex(total.index, fill_value=0)
    rate = (mismatch_counts / total) * 100
    
    palette = "viridis"
    
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    fig.suptitle('Discrepancy Analysis by File Type', fontsize=22, fontweight='bold')
    
    sns.barplot(ax=axes[0], x=mismatch_counts.index, y=mismatch_counts.values, palette=palette, hue=mismatch_counts.index, legend=False)
    axes[0].set_title('Absolute Mismatch Counts', fontsize=16)
    axes[0].set_xlabel('File Type', fontsize=12)
    axes[0].set_ylabel('Number of Mismatches', fontsize=12)
    axes[0].tick_params(axis='x', rotation=45)
    
    sns.barplot(ax=axes[1], x=rate.index, y=rate.values, palette=palette, hue=rate.index, legend=False)
    axes[1].set_title('Mismatch Rate', fontsize=16)
    axes[1].set_xlabel('File Type', fontsize=12)
    axes[1].set_ylabel('Mismatch Rate (%)', fontsize=12)
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(filepath, **save_kwds)
    plt.close()

def _create_stacked_heuristic_barchart(df: pd.DataFrame, filepath: str, save_kwds: dict):
    """Generates and saves the 100% stacked bar chart for heuristic breakdown."""
    mismatches = df[df['Discrepancy'] == 'Yes']
    total_counts = df['file_type'].value_counts()
    # Define a specific color for 'Tie' to make it visually distinct
    colors = [sns.color_palette("viridis")[0], sns.color_palette("viridis")[2], sns.color_palette("viridis")[4]]
    
    cross_tab = pd.crosstab(mismatches['file_type'], mismatches['preferred_algorithm'], normalize='index') * 100
    # Ensure a consistent order for the algorithm preference
    cross_tab = cross_tab[['Histogram', 'Myers', 'Tie']].reindex(total_counts.index).dropna()
    
    cross_tab.plot(kind='bar', stacked=True, figsize=(14, 8), color=colors, width=0.8)
    plt.title('Preferred Algorithm Breakdown by File Type', fontsize=18, fontweight='bold')
    plt.ylabel('Percentage of Mismatches (%)', fontsize=12)
    plt.xlabel('File Type', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Preferred Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filepath, **save_kwds)
    plt.close()

def _create_heuristic_impact_violinplot(df: pd.DataFrame, filepath: str, save_kwds: dict):
    """Generates and saves the violin plot showing heuristic impact, with annotations."""
    mismatches = df[df['Discrepancy'] == 'Yes'].dropna(subset=['hunks_myers', 'hunks_hist']).copy()
    mismatches['hunks_saved'] = mismatches['hunks_myers'] - mismatches['hunks_hist']
    
    hist_better_code = mismatches[
        (mismatches['file_type'].isin(['Source Code', 'Test Code'])) &
        (mismatches['preferred_algorithm'] == 'Histogram') &
        (mismatches['hunks_saved'] > 0)
    ]

    median_hunks_saved = hist_better_code['hunks_saved'].median()

    plt.figure(figsize=(14, 8))
    ax = sns.violinplot(data=hist_better_code, x='hunks_saved', color=sns.color_palette('viridis')[3], cut=0)
    plt.title('Impact of Histogram on Cohesion in Code Files', fontsize=18, fontweight='bold')
    plt.xlabel('Number of Hunks Reduced (Myers vs. Histogram)', fontsize=12)
    plt.ylabel('Density of Occurrences', fontsize=12)

    # --- Annotation Enhancement ---
    plt.axvline(x=median_hunks_saved, color='white', linestyle='--', linewidth=2)
    ax.text(median_hunks_saved + 0.5, ax.get_ylim()[1] * 0.9, f'Median = {median_hunks_saved:.0f} hunks saved', 
            color='white', fontweight='bold', ha='left', backgroundcolor='black')

    plt.savefig(filepath, **save_kwds)
    plt.close()

# ==============================================================================
# Plotter Class
# ==============================================================================

class Plotter:
    """Orchestrates the generation of all visualizations for the report."""
    def __init__(self, df: pd.DataFrame, results_dir: str):
        self.df = df
        self.results_dir = results_dir
        self.logger = logging.getLogger(__name__)
        self.save_kwds = {"dpi": 300, "bbox_inches": "tight"}
        sns.set_theme(style="whitegrid", palette="viridis")

    def generate_all_plots(self):
        """Generates and saves the final, polished set of plots."""
        # The new, streamlined list of plots
        plot_map = {
            "figure1_mismatch_analysis.png": _create_mismatch_barcharts,
            "figure2_heuristic_breakdown.png": _create_stacked_heuristic_barchart,
            "figure3_heuristic_impact.png": _create_heuristic_impact_violinplot,
        }
        
        for filename, function in plot_map.items():
            filepath = os.path.join(self.results_dir, filename)
            self.logger.info(f"Generating final plot: {filename}")
            function(self.df, filepath, self.save_kwds)