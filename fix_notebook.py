import nbformat as nbf
with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        # replace ax_nyq.set_xlabel("Z' ($\Omega$)")
        cell.source = cell.source.replace('ax_nyq.set_xlabel("Z\' ($\\Omega$)", fontsize=12, labelpad=10)', 'ax_nyq.set_xlabel(r"Z\' ($\\Omega$)", fontsize=12, labelpad=10)')
        cell.source = cell.source.replace('ax_nyq.set_xlabel("Z\' ($\\Omega$)")', 'ax_nyq.set_xlabel(r"Z\' ($\\Omega$)")')
        cell.source = cell.source.replace('ax_nyq.set_ylabel("-Z\'\' ($\\Omega$)")', 'ax_nyq.set_ylabel(r"-Z\'\' ($\\Omega$)")')

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
