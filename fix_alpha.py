import nbformat as nbf
import json

# Fix create_notebook.py
with open('create_notebook.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("plot_nyquist(Z, ax=ax_nyq, label=label)", "plot_nyquist(Z, ax=ax_nyq, label=label, alpha=0.5)")

with open('create_notebook.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix EIS_analysis.ipynb
with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        cell.source = cell.source.replace("plot_nyquist(Z, ax=ax_nyq, label=label)", "plot_nyquist(Z, ax=ax_nyq, label=label, alpha=0.5)")

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
