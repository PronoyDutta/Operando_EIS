import nbformat as nbf

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

old_subplots = "    fig, (ax_nyq, ax_ec) = plt.subplots(1, 2, figsize=(12, 5))"
new_subplots = """    fig_nyq, ax_nyq = plt.subplots(figsize=(6, 5))
    fig_ec, ax_ec = plt.subplots(figsize=(6, 5))"""

old_tight = "    plt.tight_layout()"
new_tight = """    fig_nyq.tight_layout()
    fig_ec.tight_layout()"""

old_png = """    def save_png(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.png"
            extent = ax_nyq.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted())
            fig.savefig(filename, dpi=300, bbox_inches=extent)
            print(f"Saved {filename} (left graph only)!")"""
            
new_png = """    def save_png(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.png"
            fig_nyq.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Saved {filename} (Nyquist graph only)!")"""

old_svg = """    def save_svg(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.svg"
            extent = ax_nyq.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted())
            fig.savefig(filename, bbox_inches=extent)
            print(f"Saved {filename} (left graph only)!")"""
            
new_svg = """    def save_svg(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.svg"
            fig_nyq.savefig(filename, bbox_inches='tight')
            print(f"Saved {filename} (Nyquist graph only)!")"""


for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'def update_plot(cycle_id, selected_datasets):' in cell.source:
            cell.source = cell.source.replace(old_subplots, new_subplots)
            cell.source = cell.source.replace(old_tight, new_tight)
            cell.source = cell.source.replace(old_png, new_png)
            cell.source = cell.source.replace(old_svg, new_svg)

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

# Let's also do create_notebook.py just in case
with open('create_notebook.py', 'r', encoding='utf-8') as f:
    c = f.read()
    c = c.replace(old_subplots, new_subplots)
    c = c.replace(old_tight, new_tight)
    c = c.replace(old_png, new_png)
    c = c.replace(old_svg, new_svg)
with open('create_notebook.py', 'w', encoding='utf-8') as f:
    f.write(c)
