import nbformat as nbf

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

old_png = """    def save_png(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Saved {filename}!")"""

new_png = """    def save_png(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.png"
            extent = ax_nyq.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted())
            fig.savefig(filename, dpi=300, bbox_inches=extent)
            print(f"Saved {filename} (left graph only)!")"""

old_svg = """    def save_svg(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.svg"
            fig.savefig(filename, bbox_inches='tight')
            print(f"Saved {filename}!")"""

new_svg = """    def save_svg(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.svg"
            extent = ax_nyq.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted())
            fig.savefig(filename, bbox_inches=extent)
            print(f"Saved {filename} (left graph only)!")"""

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'def update_plot(cycle_id, selected_datasets):' in cell.source:
            cell.source = cell.source.replace(old_png, new_png)
            cell.source = cell.source.replace(old_svg, new_svg)

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
