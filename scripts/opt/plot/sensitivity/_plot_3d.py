import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm


def plot_3d(df, rxn_a, rxn_b, display_a, display_b, wt_mu, outdir):
    """
    Plot normalized growth rate as a 3D surface over a 2D nutrient grid.

    Parameters
    ----------
    df          : DataFrame with columns [step_a, step_b, normalized_mu, status]
                  Output of nutrient_uptake_sweep_3d()
    r_a       : reaction ID for x-axis nutrient  (e.g. 'CO2t')
    rxn_b       : reaction ID for y-axis nutrient  (e.g. 'PRISM_design_growth')
    display_a   : human-readable name for x-axis   (e.g. 'CO2')
    display_b   : human-readable name for y-axis   (e.g. 'Light')
    wt_mu       : wildtype growth rate for reference plane
    outdir      : directory to save PNG
    """

    # ── Pivot to grid ────────────────────────────────────────────────────────
    optimal = df[df['status'] == 'optimal'].copy()
    pivot   = optimal.pivot_table(
        index='step_b', columns='step_a', values='normalized_mu'
    )

    X = pivot.columns.values.astype(float)
    Y = pivot.index.values.astype(float)
    Z = pivot.values  # shape (n_y, n_x)

    X_grid, Y_grid = np.meshgrid(X, Y)

    # ── Figure ───────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(10, 7))
    ax  = fig.add_subplot(111, projection='3d')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Surface
    surf = ax.plot_surface(
        X_grid, Y_grid, Z,
        cmap=cm.RdYlBu,
        edgecolor='none',
        alpha=0.92,
        vmin=0, vmax=1.2
    )

    # WT reference plane at z = 1.0
    ax.plot_surface(
        X_grid, Y_grid,
        np.ones_like(Z),
        alpha=0.15,
        color='gray',
        edgecolor='none'
    )

    # Colorbar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, pad=0.1)
    cbar.set_label('Normalized growth rate (µ / µ_WT)', fontsize=9)

    # Labels
    ax.set_xlabel(f'{display_a} uptake ub\n(mmol/gDW/h)', fontsize=9, labelpad=8)
    ax.set_ylabel(f'{display_b} uptake ub\n(mmol/gDW/h)', fontsize=9, labelpad=8)
    ax.set_zlabel('µ / µ_WT', fontsize=9, labelpad=6)
    ax.set_title(
        f'Nutrient Sensitivity: {display_a} × {display_b}',
        fontsize=12, fontweight='bold', pad=14
    )

    ax.tick_params(axis='both', labelsize=7)
    ax.view_init(elev=28, azim=-142)

    plt.tight_layout()
    out_path = os.path.join(outdir, f'sweep_3d_{rxn_a}_x_{rxn_b}.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  3D plot saved: {out_path}")