import os, pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from pathlib import Path

def plot_sweep(df, rxn_id, display_name, wt_mu, outdir, ylabel=None):

    ylabel = ylabel if ylabel else 'Normalized growth rate (µ / µ_WT)'
    
    optimal = df[df['status'] == 'optimal']
    infeasible = df[df['status'] != 'optimal']

    fig, ax = plt.subplots(figsize=(8, 5))

    # Main curve
    ax.plot(
        optimal['step_ub'], optimal['normalized_mu'], linewidth=2, 
        # marker='o-',
        # markersize=5,
        # markerfacecolor='#fdae61',
        color='#2166ac',
        label='Predicted µ (normalized)'
    )

    # Mark infeasible steps
    if not infeasible.empty:
        ax.scatter(
            infeasible['step_ub'], [0] * len(infeasible),
            marker='x', color='red', s=60, zorder=5,
            label='Infeasible'
        )

    # WT baseline
    ax.axhline(y=1.0, linestyle='--', color='gray', linewidth=1.2, label='WT baseline')

    ax.set_xlabel(f'{display_name} uptake upper bound (mmol/gDW/h)', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(f'Nutrient Sensitivity: {display_name}', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    png_path = os.path.join(outdir, f'sweep_{rxn_id}.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Plot saved: {png_path}")

def plot_sweep_combined(
        sweeps: dict[str, pd.DataFrame], outdir: str, 
        nutrient_meta: dict[str, dict[str, str]],
        category_label: dict[str, str],
        category_linestyle: dict[str, str]
) -> None:
    """
    Read all sweep_<rxn_id>.csv files from sweep_dir and overlay them
    on a single panel, x-axis normalized to [0, 1] (fraction of max flux).

    Parameters
    ----------
    sweep_dir : directory containing sweep_*.csv files
    outdir    : directory to save combined PNG
    """

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    plotted = []

    for rxn_id, meta in nutrient_meta.items():

        if rxn_id not in sweeps:
            continue

        df = sweeps[rxn_id]

        # Keep only optimal rows
        df = df[df['status'] == 'optimal'].copy()
        if df.empty:
            continue

        # Normalise x to [0, 1]
        x_max = df['step_ub'].max()
        if x_max == 0:
            continue
        df['x_norm'] = df['step_ub'] / x_max

        # y is already normalized_mu
        y = df['normalized_mu']
        x = df['x_norm']

        ax.plot(
            x, y,
            color=meta['color'],
            linestyle=category_linestyle[meta['category']],
            linewidth=2.0,
            # marker='o',
            # markersize=3.5,
            # markerfacecolor=meta['color'],
            # markeredgewidth=0,
            label=meta['display'],
            zorder=3,
        )
        plotted.append(meta)

    # WT baseline
    ax.axhline(1.0, color='#444444', linewidth=1.0, linestyle=':', zorder=2,
               label='WT baseline')

    # ── Axes ─────────────────────────────────────────────────────────────────
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.05, 1.25)
    ax.set_xlabel('Nutrient uptake (fraction of maximal flux)', fontsize=10)
    ax.set_ylabel('Normalized growth rate (µ / µ_WT)', fontsize=10)
    ax.set_title('Nutrient Sensitivity Analysis', fontsize=12,
                 fontweight='bold', loc='left')
    ax.tick_params(labelsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color='#dddddd', linewidth=0.6, zorder=1)

    # ── Legend — split by category ───────────────────────────────────────────
    nutrient_handles = [
        mlines.Line2D([], [],
                      color=nutrient_meta[rxn]['color'],
                      linestyle=category_linestyle[nutrient_meta[rxn]['category']],
                      linewidth=2, marker='o', markersize=4,
                      label=nutrient_meta[rxn]['display'])
        for rxn in nutrient_meta if nutrient_meta[rxn] in plotted
    ]

    category_handles = [
        mlines.Line2D([], [], color='#555555', linestyle=ls,
                      linewidth=1.8, label=category_label[cat])
        for cat, ls in category_linestyle.items()
    ]

    wt_handle = mlines.Line2D([], [], color='#444444', linestyle=':',
                               linewidth=1.2, label='WT baseline')

    legend1 = ax.legend(
        handles=nutrient_handles,
        title='Nutrient', title_fontsize=8,
        fontsize=8, loc='upper right',
        framealpha=0.85, edgecolor='#cccccc',
    )
    ax.add_artist(legend1)

    ax.legend(
        handles=category_handles + [wt_handle],
        title='Category', title_fontsize=8,
        fontsize=8, loc='lower right',
        framealpha=0.85, edgecolor='#cccccc',
    )

    # ── Save ─────────────────────────────────────────────────────────────────
    out_path = os.path.join(outdir, 'sweep_combined.png')
    fig.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {out_path}")