import nbformat as nbf

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'ax.semilogx(r[\'tau\'], r[\'gamma\'], _LS[i % len(_LS)], marker=\'o\',' in cell.source:
            cell.source = cell.source.replace(
                'ax.semilogx(r[\'tau\'], r[\'gamma\'], _LS[i % len(_LS)], marker=\'o\',\\n                    ms=3, label=f"{ds} (\lambda={r[\'lambda\']:.1e})")',
                'ax.semilogx(r[\'tau\'], r[\'gamma\'], _LS[i % len(_LS)], marker=\'o\',\\n                    ms=3, alpha=0.5, label=f"{ds} (\lambda={r[\'lambda\']:.1e})")'
            )
            # The lambda character was actually ׯ (or something weird) in the label?
            # Let's just do a simpler replace.
            cell.source = cell.source.replace(
                "ms=3, label=f\"{ds}",
                "ms=3, alpha=0.5, label=f\"{ds}"
            )

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
