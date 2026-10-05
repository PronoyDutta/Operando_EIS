import nbformat as nbf

button_code = """    plt.show()
    
    import ipywidgets as widgets
    from IPython.display import display
    
    btn_png = widgets.Button(description='Save as PNG')
    btn_svg = widgets.Button(description='Save as SVG')
    out_msg = widgets.Output()
    
    def save_png(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Saved {filename}!")
            
    def save_svg(b):
        with out_msg:
            out_msg.clear_output()
            filename = f"operando_nyquist_cycle_{cycle_id}.svg"
            fig.savefig(filename, bbox_inches='tight')
            print(f"Saved {filename}!")
            
    btn_png.on_click(save_png)
    btn_svg.on_click(save_svg)
    
    display(widgets.HBox([btn_png, btn_svg]))
    display(out_msg)"""

with open('EIS_analysis.ipynb', 'r', encoding='utf-8', errors='ignore') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'def update_plot(cycle_id, selected_datasets):' in cell.source:
            cell.source = cell.source.replace('    plt.show()', button_code)

with open('EIS_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

# Also update create_notebook.py
with open('create_notebook.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
content = content.replace('    plt.show()\\n\\nif not cycle_ids:', button_code.replace('\\n', '\\n') + '\\n\\nif not cycle_ids:')
with open('create_notebook.py', 'w', encoding='utf-8') as f:
    f.write(content)
