import nbformat as nbf

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

target_code = """    ax.set_ylim(bottom=None if y_min == -999 else y_min, top=None if y_max == -999 else y_max)
    plt.tight_layout()
    plt.show()"""

replacement_code = """    ax.set_ylim(bottom=None if y_min == -999 else y_min, top=None if y_max == -999 else y_max)
    plt.tight_layout()
    plt.show()
    
    import ipywidgets as widgets
    from IPython.display import display
    
    btn_png = widgets.Button(description='Save PNG (600dpi)')
    btn_svg = widgets.Button(description='Save SVG')
    out_msg = widgets.Output()
    
    def save_png(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"drt_cycle_{cycle_id}.png"
            fig.savefig(filename, dpi=600, bbox_inches='tight')
            print(f"Saved {filename} at 600 DPI!")
            
    def save_svg(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"drt_cycle_{cycle_id}.svg"
            fig.savefig(filename, bbox_inches='tight')
            print(f"Saved {filename}!")
            
    btn_png.on_click(save_png)
    btn_svg.on_click(save_svg)
    
    display(widgets.HBox([btn_png, btn_svg]))
    display(out_msg)"""

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'def update_drt(cycle_id, log_lam, use_gcv' in cell.source:
            cell.source = cell.source.replace(target_code, replacement_code)

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
