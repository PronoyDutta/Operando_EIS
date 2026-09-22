import json
import sys

file_path = 'e:/Github_repositories/EIS_analysis/EIS_analysis.ipynb'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
except Exception as e:
    print(f"Error reading notebook: {e}")
    sys.exit(1)

changed = False

replacement_code = """
    # Ensure equal scale and identical limits for Nyquist plots
    x_low, x_high = ax_nyq.get_xlim()
    y_low, y_high = ax_nyq.get_ylim()
    plot_max = max(x_high, y_high)
    plot_min = min(x_low, y_low)
    ax_nyq.set_xlim(plot_min, plot_max)
    ax_nyq.set_ylim(plot_min, plot_max)
    ax_nyq.set_aspect('equal', adjustable='box')
"""

for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        source = cell['source']
        
        # Remove previous 'ax_nyq.set_aspect('equal')' if present
        source = [line for line in source if 'ax_nyq.set_aspect(\'equal\')' not in line]
        
        insert_indices = []
        for i, line in enumerate(source):
            if 'ax_nyq.set_title' in line:
                insert_indices.append(i)
                
        # Insert in reverse order to not mess up indices
        for i in reversed(insert_indices):
            indent = len(source[i]) - len(source[i].lstrip())
            indent_str = source[i][:indent]
            
            # Prepare block
            block = []
            for rl in replacement_code.strip('\n').split('\n'):
                block.append(f"{indent_str}{rl.strip()}\n")
            
            # Check if block is already there
            if not any('plot_max = max(x_high, y_high)' in line for line in source):
                for b_line in reversed(block):
                    source.insert(i, b_line)
                changed = True

        cell['source'] = source

if changed:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1)
        print("Notebook updated successfully with identical X/Y limits.")
    except Exception as e:
        print(f"Error writing notebook: {e}")
        sys.exit(1)
else:
    print("No changes needed. Notebook is already up-to-date.")
