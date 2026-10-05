import nbformat as nbf
import json

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

rc_params_block = """    # Nature Energy / Publication Quality Settings
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 12,
        'axes.labelsize': 14,
        'axes.titlesize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 11,
        'axes.linewidth': 1.5,
        'lines.linewidth': 2,
        'lines.markersize': 6,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.top': True,
        'ytick.right': True,
        'xtick.minor.visible': True,
        'ytick.minor.visible': True,
        'xtick.major.width': 1.5,
        'ytick.major.width': 1.5,
        'xtick.minor.width': 1.0,
        'ytick.minor.width': 1.0,
        'xtick.major.size': 5,
        'ytick.major.size': 5,
        'xtick.minor.size': 3,
        'ytick.minor.size': 3,
        'legend.frameon': False,
    })
    
    fig, ax = plt.subplots(figsize=(8, 5))"""

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'def update_drt(cycle_id, log_lam, use_gcv, selected_datasets' in cell.source:
            # 1. Inject rcParams
            cell.source = cell.source.replace('    fig, ax = plt.subplots(figsize=(8, 5))', rc_params_block)
            # 2. Turn off grid
            cell.source = cell.source.replace('    ax.grid(True, alpha=0.4)', '    ax.grid(False)\n    import matplotlib.ticker as ticker\n    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))\n    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))')
            # 3. Fix legend frameon (though rcParams should handle it, explicit is better)
            # 4. Add transparency to marker plots (wait, how are they plotted?)
            # Let's replace '.plot(' with '.plot(' and add alpha=0.5. Wait, we don't know the exact plot command.
            # Usually pyDRTtools outputs arrays and we plot them. 
            pass

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
