import nbformat as nbf
import shutil
from pathlib import Path

notebook_file = Path('EIS_analysis.ipynb')
backup_file = Path('EIS_analysis_backup_left_drt.ipynb')

# Step 1: Backup notebook before changes if not already backed up
if not backup_file.exists():
    shutil.copyfile(notebook_file, backup_file)
    print(f"Created backup notebook: {backup_file}")
else:
    print(f"Backup already exists: {backup_file}")

# Step 2: Update EIS_analysis.ipynb
with open(notebook_file, 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

target_code = "ax2.set_xlim(left=tau_min, right=0.5)"
replacement_code = "ax2.set_xlim(left=tau_min, right=tau_max)"

updated_cells = 0
for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'def update_drt_multi' in cell.source and target_code in cell.source:
            cell.source = cell.source.replace(target_code, replacement_code)
            updated_cells += 1

if updated_cells > 0:
    with open(notebook_file, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Updated {updated_cells} cell(s) in {notebook_file}: set right=tau_max for ax2 contour plot.")
else:
    print(f"No cells needed updating in {notebook_file} (or target pattern not found).")

# Step 3: Update create_notebook.py
create_script = Path('create_notebook.py')
if create_script.exists():
    with open(create_script, 'r', encoding='utf-8') as f:
        content = f.read()
    if target_code in content:
        content = content.replace(target_code, replacement_code)
        with open(create_script, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {create_script} with {replacement_code}.")
    else:
        print(f"{create_script} is already up-to-date.")
