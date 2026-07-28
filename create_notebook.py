import nbformat as nbf

nb = nbf.v4.new_notebook()

# Cell 1: Intro
intro_md = """# Electrochemical Impedance Spectroscopy (EIS) Analysis
This notebook is designed to process, visualize, and fit EIS data from Biologic (.mpt) files.
It uses `impedance.py` for equivalent circuit fitting and `ipympl` for interactive Matplotlib plots."""

# Cell 2: Imports
imports_code = """%pip install pandas numpy matplotlib impedance ipympl
%matplotlib widget
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from impedance.models.circuits import CustomCircuit
from impedance.visualization import plot_nyquist, plot_bode"""

# Cell 3: Data Loader
data_loader_md = """## 1. Data Loading
Robustly read Biologic `.mpt` files. The function skips the metadata headers automatically."""
data_loader_code = """def load_biologic_mpt(filepath):
    # Find the header row
    skip_rows = 0
    with open(filepath, 'r', encoding='latin-1') as f:
        for i, line in enumerate(f):
            if line.startswith('mode'):
                skip_rows = i
                break
                
    # Read the data
    df = pd.read_csv(filepath, sep='\\t', skiprows=skip_rows, encoding='latin-1')
    
    # Identify the column to segregate by
    if 'z cycle' in df.columns:
        segregation_col = 'z cycle'
    elif 'cycle number' in df.columns and df['cycle number'].nunique() > 1:
        segregation_col = 'cycle number'
    elif 'loop number' in df.columns:
        segregation_col = 'loop number'
    else:
        segregation_col = None
    
    eis_measurements = {}
    
    if segregation_col and segregation_col in df.columns:
        for cycle_id, group in df.groupby(segregation_col):
            # Only keep rows where frequency is measured (to filter out GCPL rest/charge steps if they are in the same file)
            group = group.dropna(subset=['freq/Hz'])
            if len(group) == 0:
                continue
                
            freq = group['freq/Hz'].values
            Z_real = group['Re(Z)/Ohm'].values
            Z_imag = group['-Im(Z)/Ohm'].values
            Z = Z_real - 1j * Z_imag
            eis_measurements[cycle_id] = (freq, Z)
    else:
        # Fallback if no cycle column exists
        freq = df['freq/Hz'].values
        Z_real = df['Re(Z)/Ohm'].values
        Z_imag = df['-Im(Z)/Ohm'].values
        Z = Z_real - 1j * Z_imag
        eis_measurements[1] = (freq, Z)
        
    return eis_measurements

# Example usage:
# data_path = Path("data/your_file.mpt")
data_path = Path("data/20260722_C23_SMSP20_operando_EIS_C01.mpt")
eis_dict = load_biologic_mpt(data_path)
print(f"Found {len(eis_dict)} EIS measurements.")"""

# Cell 4: Visualization
viz_md = """## 2. Interactive Visualization
Interactive Nyquist and Bode plots. Since `%matplotlib widget` is enabled, you can zoom, pan, and hover over data points."""
viz_code = """import ipywidgets as widgets
from IPython.display import display

# Create the figure once
fig, (ax_nyq, ax_bode) = plt.subplots(1, 2, figsize=(12, 5))

def update_plot(cycle_id):
    # Get the data for the selected cycle
    freq, Z = eis_dict[cycle_id]
    
    # Clear the previous plot lines
    ax_nyq.clear()
    ax_bode[0].clear()
    ax_bode[1].clear()
    
    # Plot the new data
    plot_nyquist(Z, ax=ax_nyq)
    plot_bode(freq, Z, axes=ax_bode)
    
    # Update titles
    ax_nyq.set_title(f"Nyquist Plot - Cycle {cycle_id}")
    ax_bode[0].set_title(f"Bode Plot - Cycle {cycle_id}")
    
    # Force the interactive canvas to redraw
    fig.canvas.draw_idle()

# Extract all the cycle numbers from the dictionary
cycle_ids = sorted(list(eis_dict.keys()))

# Create an interactive slider
cycle_slider = widgets.SelectionSlider(
    options=cycle_ids,
    value=cycle_ids[0],
    description='Cycle:',
    continuous_update=False,
    orientation='horizontal'
)

# Link the slider to the plot updater
widgets.interact(update_plot, cycle_id=cycle_slider);"""

# Cell 5: Modeling
model_md = """## 3. Equivalent Circuit Modeling & Fitting
Define your equivalent circuit here. 
Since you are working with a LiS battery in a 3-electrode setup, you might start with a Modified Randles circuit, or use multiple RC/RQ elements for the different interfaces (e.g., SEI, charge transfer).

**Common Elements in impedance.py:**
- `R`: Resistor
- `C`: Capacitor
- `CPE`: Constant Phase Element
- `W`: Warburg Element
- `p(R1, C1)`: Parallel elements
- `-`: Series elements"""
model_code = """# Define your circuit model
# Example: R0 + p(R1, CPE1) + p(R2, CPE2) + W1
# circuit_string = 'R0-p(R1,CPE1)-p(R2,CPE2)-W1'
# initial_guess = [10, 50, 1e-4, 0.8, 20, 1e-3, 0.8, 100]

circuit_string = 'R0-p(R1,C1)-W1'
initial_guess = [10, 50, 1e-4, 100] # Provide an initial guess for the parameters

circuit = CustomCircuit(circuit_string, initial_guess=initial_guess)

# To fit the data from the selected cycle:
# circuit.fit(freq, Z)
# print(circuit)

# To plot the fit against the data:
# Z_fit = circuit.predict(freq)
# fig, (ax_nyq, ax_bode) = plt.subplots(1, 2, figsize=(12, 5))
# plot_nyquist(Z, ax=ax_nyq, fmt='o')
# plot_nyquist(Z_fit, ax=ax_nyq, fmt='-')
# plt.legend(['Data', 'Fit'])
# plt.show()"""

nb.cells = [
    nbf.v4.new_markdown_cell(intro_md),
    nbf.v4.new_code_cell(imports_code),
    nbf.v4.new_markdown_cell(data_loader_md),
    nbf.v4.new_code_cell(data_loader_code),
    nbf.v4.new_markdown_cell(viz_md),
    nbf.v4.new_code_cell(viz_code),
    nbf.v4.new_markdown_cell(model_md),
    nbf.v4.new_code_cell(model_code)
]

with open('EIS_analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook created successfully.")
