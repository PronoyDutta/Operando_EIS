import nbformat as nbf

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'ax.semilogx(r[\'tau\']' in cell.source:
            # Remove the bad AutoMinorLocator for X axis which is a log axis
            cell.source = cell.source.replace('    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))\\n', '')

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
