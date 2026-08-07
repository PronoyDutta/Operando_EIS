import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

# Cell 0: Intro
cells.append(nbf.v4.new_markdown_cell("""# Electrochemical Impedance Spectroscopy (EIS) Analysis
This notebook is designed to process, visualize, and fit EIS data from Biologic (.mpt) files.
It uses `impedance.py` for equivalent circuit fitting and `ipympl` for interactive Matplotlib plots."""))

# Cell 1: Imports
cells.append(nbf.v4.new_code_cell("""%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from impedance.models.circuits import CustomCircuit
from impedance.visualization import plot_nyquist, plot_bode"""))

# Cell 2: Data Loader Markdown
cells.append(nbf.v4.new_markdown_cell("""## 1. Data Loading
Robustly read Biologic `.mpt` files. The function skips the metadata headers automatically."""))

# Cell 3: Data Loader Code
cells.append(nbf.v4.new_code_cell("""def load_biologic_mpt(filepath):
    # Find the header row
    skip_rows = 0
    with open(filepath, 'r', encoding='latin-1') as f:
        for i, line in enumerate(f):
            if line.startswith('mode'):
                skip_rows = i
                break
                
    # Read the data
    df = pd.read_csv(filepath, sep='\\t', skiprows=skip_rows, encoding='latin-1')
    
    if 'time/s' in df.columns:
        # Convert time/s to numeric if possible, otherwise it might be datetime strings
        time_numeric = pd.to_numeric(df['time/s'], errors='coerce')
        if time_numeric.isna().all() and not df['time/s'].isna().all():
            time_dt = pd.to_datetime(df['time/s'], errors='coerce')
            df['time/h'] = (time_dt - time_dt.iloc[0]) / pd.Timedelta(hours=1)
        else:
            df['time/h'] = (time_numeric - time_numeric.iloc[0]) / 3600
    
    if 'z cycle' in df.columns:
        segregation_col = 'z cycle'
    elif 'cycle number' in df.columns and df['cycle number'].nunique() > 1:
        segregation_col = 'cycle number'
    elif 'loop number' in df.columns:
        segregation_col = 'loop number'
    else:
        segregation_col = None
    
    eis_measurements = {}
    metadata = {}
    
    if segregation_col and segregation_col in df.columns:
        for cycle_id, group in df.groupby(segregation_col):
            # Extract state and voltage before EIS
            first_idx = group.index[0]
            if first_idx > 0:
                prev_rows = df.loc[:first_idx-1]
                active_rows = prev_rows[np.abs(prev_rows.get('I/mA', 0)) > 1e-6]
                if not active_rows.empty:
                    last_i = active_rows.iloc[-1]['I/mA']
                    state = "CHARGE" if last_i > 0 else "DISCHARGE"
                else:
                    state = "REST"
                last_ewe = prev_rows.iloc[-1]['Ewe/V'] if 'Ewe/V' in prev_rows.columns else 0.0
            else:
                state = "START"
                last_ewe = group.iloc[0]['Ewe/V'] if 'Ewe/V' in group.columns else 0.0
                
            start_time = group.iloc[0].get('time/h', 0.0)
            start_ewe = group.iloc[0].get('Ewe/V', 0.0)
            
            metadata[int(cycle_id)] = {'state': state, 'voltage': f"{last_ewe:.2f}", 'time': start_time, 'ewe': start_ewe}
            
            # Bulletproof filter: drop empty rows, 0Hz freq, and 0 Ohm impedance points
            group = group.dropna(subset=['freq/Hz'])
            group = group[(group['freq/Hz'] != 0.0) & (group['Re(Z)/Ohm'] != 0.0)] 
            group = group[group['freq/Hz'] >= 0.09]

            if len(group) == 0:
                continue
                
            freq = group['freq/Hz'].values
            Z_real = group['Re(Z)/Ohm'].values
            Z_imag = group['-Im(Z)/Ohm'].values
            Z = Z_real - 1j * Z_imag
            eis_measurements[int(cycle_id)] = (freq, Z)
    else:
        # Fallback if no cycle column exists
        group = df.dropna(subset=['freq/Hz'])
        group = group[(group['freq/Hz'] != 0.0) & (group['Re(Z)/Ohm'] != 0.0)]
        
        freq = group['freq/Hz'].values
        Z_real = group['Re(Z)/Ohm'].values
        Z_imag = group['-Im(Z)/Ohm'].values
        Z = Z_real - 1j * Z_imag
        eis_measurements[1] = (freq, Z)
        metadata[1] = {'state': 'UNKNOWN', 'voltage': 'N/A', 'time': 0, 'ewe': 0}
        
    return eis_measurements, metadata, df

# Provide a dictionary of datasets to load
data_paths = {
    "Sample 1": Path("data/20260722_C23_SMSP20_operando_EIS_C01.mpt"),
    "Sample 2": Path("data/20260803_3004SI20_C36_1pt19mg_SD3_operandoEIS_C01.mpt") # Add or remove paths as needed
}

eis_dicts = {}
metadata_dicts = {}
raw_dfs = {}
for name, path in data_paths.items():
    if path.exists():
        eis, meta, df = load_biologic_mpt(path)
        eis_dicts[name] = eis
        metadata_dicts[name] = meta
        raw_dfs[name] = df
        print(f"Loaded {name}: Found {len(eis_dicts[name])} EIS measurements.")
    else:
        print(f"Warning: {path} not found.")"""))

# Cell 4: Markdown
cells.append(nbf.v4.new_markdown_cell("""# Plot the individual EIS curves"""))

# Cell 5: Code
cells.append(nbf.v4.new_code_cell("""import ipywidgets as widgets
import matplotlib.pyplot as plt
from impedance.visualization import plot_nyquist
from IPython.display import display, clear_output

dataset_names = list(eis_dicts.keys())

# Find all common cycle IDs across datasets
all_cycles = set()
for d in eis_dicts.values():
    all_cycles.update(d.keys())
cycle_ids = sorted(list(all_cycles))

def update_plot(cycle_id, selected_datasets):
    fig, (ax_nyq, ax_ec) = plt.subplots(1, 2, figsize=(14, 6))
    
    for ds_name in selected_datasets:
        if cycle_id in eis_dicts[ds_name]:
            freq, Z = eis_dicts[ds_name][cycle_id]
            meta = metadata_dicts[ds_name][cycle_id]
            state = meta['state']
            voltage = meta['voltage']
            
            # Use exact legend format requested by the user
            label = f"{ds_name.upper()}-CYCLE {cycle_id} {state} {voltage}V"
            plot_nyquist(Z, ax=ax_nyq, label=label)
            
            # Plot EC curve
            df_raw = raw_dfs[ds_name]
            if 'time/h' in df_raw.columns and 'Ewe/V' in df_raw.columns:
                p = ax_ec.plot(df_raw['time/h'], df_raw['Ewe/V'], label=f"{ds_name} EC Curve", alpha=0.6)
                color = p[0].get_color()
                # Red dot highlighting this cycle's location
                ax_ec.plot(meta['time'], meta['ewe'], marker='o', markersize=8, color='red', markeredgecolor='black', zorder=5)
            
    ax_nyq.set_title(f"Operando Nyquist Plot - Cycle {cycle_id}", fontsize=14)
    ax_ec.set_title("Electrochemical Profile", fontsize=14)
    ax_ec.set_xlabel("Time (Hours)", fontsize=12)
    ax_ec.set_ylabel("Ewe (V)", fontsize=12)
    ax_ec.grid(True, alpha=0.5)
    
    ax_nyq.set_xlim(0, 100)
    ax_nyq.set_ylim(0, 100)
    
    if selected_datasets:
        ax_nyq.legend(loc='best')
        ax_ec.legend(loc='best')
    plt.tight_layout()
    plt.show()

if not cycle_ids:
    print("No data loaded!")
else:
    cycle_slider = widgets.SelectionSlider(
        options=cycle_ids, value=cycle_ids[0], description='Cycle:', continuous_update=False, orientation='horizontal'
    )
    dataset_selector = widgets.SelectMultiple(
        options=dataset_names, value=[dataset_names[0]], description='Datasets:', disabled=False
    )
    widgets.interact(update_plot, cycle_id=cycle_slider, selected_datasets=dataset_selector);"""))

# Cell 6: Waterfall Plot Markdown
cells.append(nbf.v4.new_markdown_cell("""# Waterfall plot"""))

# Cell 7: Waterfall Plot Code
cells.append(nbf.v4.new_code_cell("""import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import ipywidgets as widgets

def plot_waterfall(selected_datasets):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    colors = ['plasma', 'viridis', 'cividis', 'magma'] 
    
    for i, ds_name in enumerate(selected_datasets):
        ds_cycles = sorted(list(eis_dicts[ds_name].keys()))
        cmap = plt.colormaps.get_cmap(colors[i % len(colors)])
        
        for cycle in ds_cycles:
            freq, Z = eis_dicts[ds_name][cycle]
            Z_re = Z.real
            Z_im_neg = -Z.imag
            y_val = np.full_like(Z_re, cycle)
            
            # Gradient based on cycle number for this specific dataset
            color = cmap(cycle / max(ds_cycles)) if max(ds_cycles) > 0 else 'blue'
            
            # Plot the 3D line
            ax.plot(Z_re, y_val, Z_im_neg, marker='.', markersize=4, linestyle='-', linewidth=1.5, color=color)

    ax.set_xlabel(r"Z' ($\Omega$)", fontsize=12, labelpad=10)
    ax.set_ylabel("Cycle Number", fontsize=12, labelpad=10)
    ax.set_zlabel(r"-Z'' ($\Omega$)", fontsize=12, labelpad=10)
    
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.xaxis._axinfo["grid"]['color'] = (0.9, 0.9, 0.9, 1)
    ax.yaxis._axinfo["grid"]['color'] = (0.9, 0.9, 0.9, 1)
    ax.zaxis._axinfo["grid"]['color'] = (0.9, 0.9, 0.9, 1)
    
    ax.view_init(elev=25, azim=-55)
    ax.set_title(f"Operando 3D Waterfall Nyquist Plot ({', '.join(selected_datasets)})", fontsize=14)
    plt.show()

if cycle_ids:
    waterfall_dataset_selector = widgets.SelectMultiple(
        options=dataset_names, value=[dataset_names[0]], description='Datasets:', disabled=False
    )
    widgets.interact(plot_waterfall, selected_datasets=waterfall_dataset_selector);"""))

# Cell 8: 2D plot Markdown
cells.append(nbf.v4.new_markdown_cell("""# 2D plot"""))

# Cell 9: 2D plot Code
cells.append(nbf.v4.new_code_cell("""import ipywidgets as widgets
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from impedance.visualization import plot_nyquist

def update_multi_plot(cycle_range, selected_datasets):
    start, end = cycle_range
    fig, ax_nyq = plt.subplots(figsize=(8, 8))
    
    linestyles = ['-', '--', ':', '-.']
    
    for idx, ds_name in enumerate(selected_datasets):
        ds_cycles = sorted(list(eis_dicts[ds_name].keys()))
        selected_cycles = [c for c in ds_cycles if start <= c <= end]
        ls = linestyles[idx % len(linestyles)]
        
        for c in selected_cycles:
            freq, Z = eis_dicts[ds_name][c]
            color = cm.plasma(c / max(ds_cycles)) if max(ds_cycles) > 0 else 'blue'
            
            # Plot the actual data
            plot_nyquist(Z, ax=ax_nyq, fmt=f'.{ls}', color=color)
            
            # Add dummy line to generate a nice legend label
            ax_nyq.plot([], [], f'.{ls}', color=color, label=f'{ds_name} - Cycle {c}')
            
    ax_nyq.set_title(f"Operando Nyquist Plot (Cycles {start} to {end})")
    ax_nyq.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=max(1, len(selected_datasets)//2))
    plt.tight_layout()
    plt.show()

if cycle_ids:
    cycle_range_slider = widgets.IntRangeSlider(
        value=[cycle_ids[0], cycle_ids[-1]],
        min=min(cycle_ids), max=max(cycle_ids), step=1,
        description='Cycles:', continuous_update=False, orientation='horizontal'
    )
    multi_dataset_selector = widgets.SelectMultiple(
        options=dataset_names, value=[dataset_names[0]], description='Datasets:', disabled=False
    )
    widgets.interact(update_multi_plot, cycle_range=cycle_range_slider, selected_datasets=multi_dataset_selector);"""))

# Cell 10: Interactive Visualization Markdown
cells.append(nbf.v4.new_markdown_cell("""## 2. Interactive Visualization
Interactive Nyquist and Bode plots. Since `%matplotlib widget` is enabled, you can zoom, pan, and hover over data points."""))

# Cell 11: Interactive Visualization Code
cells.append(nbf.v4.new_code_cell("""def plot_eis_data(freq, Z, title="EIS Measurement"):
    fig, (ax_nyq, ax_bode) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Nyquist Plot
    plot_nyquist(Z, ax=ax_nyq)
    ax_nyq.set_title(f"Nyquist Plot - {title}")
    
    # Bode Plot
    plot_bode(freq, Z, axes=ax_bode)
    ax_bode[0].set_title(f"Bode Plot - {title}")
    
    plt.tight_layout()
    plt.show()

# Example usage (plotting the first loop):
# ds_name = list(eis_dicts.keys())[0]
# cycle_id = list(eis_dicts[ds_name].keys())[0]
# freq, Z = eis_dicts[ds_name][cycle_id]
# plot_eis_data(freq, Z, title=f"Operando LiS - {ds_name} Cycle {cycle_id}")"""))

# Cell 12: Modeling Markdown
cells.append(nbf.v4.new_markdown_cell("""## 3. Equivalent Circuit Modeling & Fitting
Define your equivalent circuit here. 
Since you are working with a LiS battery in a 3-electrode setup, you might start with a Modified Randles circuit, or use multiple RC/RQ elements for the different interfaces (e.g., SEI, charge transfer).

**Common Elements in impedance.py:**
- `R`: Resistor
- `C`: Capacitor
- `CPE`: Constant Phase Element
- `W`: Warburg Element
- `p(R1, C1)`: Parallel elements
- `-`: Series elements"""))

# Cell 13: Modeling Code
cells.append(nbf.v4.new_code_cell("""# Define your circuit model
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
# plt.show()"""))

# Cell 14: Electrode Stability Markdown (Extracted from cell 14, now put into its own cell)
cells.append(nbf.v4.new_markdown_cell("""# Overall Electrode Stability (Single file preview)"""))

cells.append(nbf.v4.new_code_cell("""import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display

def plot_electrode_stability(ds_name):
    if ds_name in raw_dfs:
        df_raw = raw_dfs[ds_name]
        if 'time/h' in df_raw.columns and 'Ece/V' in df_raw.columns:
            fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 7), sharex=True, 
                                           gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.1})
            
            # TOP PLOT
            ax1.plot(df_raw['time/h'], df_raw['Ece/V'], label='Anode vs Ref (Ece)', color='red', linewidth=1.5)
            if 'Ewe/V' in df_raw.columns:
                ax1.plot(df_raw['time/h'], df_raw['Ewe/V'], label='Cathode vs Ref (Ewe)', color='blue', linewidth=1.5)
            ax1.set_ylabel('Potential (V)', fontsize=12)
            ax1.set_title(f'Overall Electrode Stability - {ds_name}', fontsize=14)
            ax1.legend(loc='best')
            ax1.grid(True, alpha=0.5)
            
            # BOTTOM PLOT
            ax2.plot(df_raw['time/h'], df_raw['Ece/V'], label='Anode vs Ref (Ece)', color='red', linewidth=1.5)
            ax2.set_xlabel('Time (Hours)', fontsize=12)
            ax2.set_ylabel('Anode (V)', fontsize=12)
            ax2.legend(loc='best')
            ax2.grid(True, alpha=0.5)
            
            plt.tight_layout()
            plt.show()
        else:
            print(f"Data for {ds_name} does not contain 'time/h' or 'Ece/V'.")
    else:
        print(f"Dataset {ds_name} not found.")

if dataset_names:
    stability_ds_selector = widgets.Dropdown(
        options=dataset_names, value=dataset_names[0], description='Dataset:', disabled=False
    )
    widgets.interact(plot_electrode_stability, ds_name=stability_ds_selector);"""))

# Cell 15: DRT analysis Markdown
cells.append(nbf.v4.new_markdown_cell("""# DRT analysis"""))

# Cell 16: DRT analysis Code (Modified for multi dataset)
cells.append(nbf.v4.new_code_cell("""import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
from scipy.optimize import nnls

def compute_drt(freq, Z_imag, lam):
    omega = 2 * np.pi * freq
    tau = 1 / omega
    
    A = np.zeros((len(omega), len(tau)))
    for i, w in enumerate(omega):
        for j, t in enumerate(tau):
            A[i, j] = (w * t) / (1 + (w * t)**2)
            
    n = len(tau)
    L = np.zeros((n-2, n))
    for i in range(n-2):
        L[i, i] = 1
        L[i, i+1] = -2
        L[i, i+2] = 1
        
    A_aug = np.vstack([A, np.sqrt(lam) * L])
    b_aug = np.hstack([Z_imag, np.zeros(n-2)])
    gamma_opt, _ = nnls(A_aug, b_aug)
    return tau, gamma_opt

def update_drt(cycle_id, log_lam, selected_datasets):
    lam = 10**log_lam
    fig, ax_drt = plt.subplots(figsize=(8, 5))
    
    linestyles = ['-', '--', ':', '-.']
    
    for idx, ds_name in enumerate(selected_datasets):
        if cycle_id in eis_dicts[ds_name]:
            freq, Z = eis_dicts[ds_name][cycle_id]
            Z_imag_data = -Z.imag
            tau, gamma = compute_drt(freq, Z_imag_data, lam)
            
            ls = linestyles[idx % len(linestyles)]
            ax_drt.semilogx(tau, gamma, marker='o', markersize=4, linestyle=ls, label=f'{ds_name}')
    
    ax_drt.set_xlabel('Relaxation Time $\\tau$ (s)', fontsize=12)
    ax_drt.set_ylabel(r'$\gamma(\tau)$ ($\Omega$)', fontsize=12)
    ax_drt.set_title(f"DRT Analysis - Cycle {cycle_id} ($\\lambda$ = {lam:.1e})", fontsize=14)
    ax_drt.grid(True, alpha=0.5)
    
    if selected_datasets:
        ax_drt.legend(loc='best')
        
    plt.tight_layout()
    plt.show()

if cycle_ids:
    cycle_slider_drt = widgets.SelectionSlider(
        options=cycle_ids, value=cycle_ids[0], description='Cycle:', continuous_update=False
    )
    lam_slider = widgets.FloatSlider(
        value=-2.0, min=-5.0, max=1.0, step=0.5, 
        description='log($\\lambda$):', continuous_update=False,
        tooltip="Lower = fits noise (spiky). Higher = over-smoothed."
    )
    drt_dataset_selector = widgets.SelectMultiple(
        options=dataset_names, value=[dataset_names[0]], description='Datasets:', disabled=False
    )
    widgets.interact(update_drt, cycle_id=cycle_slider_drt, log_lam=lam_slider, selected_datasets=drt_dataset_selector);"""))

# Cell 17: DRT Interactive Contour Markdown
cells.append(nbf.v4.new_markdown_cell("""# DRT Multi-Cycle Contour"""))

cells.append(nbf.v4.new_code_cell("""import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.interpolate import interp1d
from IPython.display import display

# We will apply this globally to all datasets
lam = 10**-2.0 

# Pre-compute the DRT curves for all datasets to make the slider fast!
gamma_dict = {}
tau_ref = None

# We use the first dataset to determine tau_ref
if data_paths:
    first_ds = list(data_paths.keys())[0]
    all_cycle_ids = sorted(list(eis_dicts[first_ds].keys()))
    if all_cycle_ids:
        master_freq, _ = eis_dicts[first_ds][all_cycle_ids[-1]]
        tau_ref = 1 / (2 * np.pi * master_freq)

if tau_ref is not None:
    for ds_name in dataset_names:
        gamma_dict[ds_name] = {}
        for c in eis_dicts[ds_name].keys():
            freq, Z = eis_dicts[ds_name][c]
            tau, gamma = compute_drt(freq, -Z.imag, lam)
            f_interp = interp1d(np.log10(tau), gamma, bounds_error=False, fill_value=0.0)
            gamma_dict[ds_name][c] = f_interp(np.log10(tau_ref))
            
    # Find global max for sliders
    global_gamma_max = max([np.max(g) for ds in gamma_dict.values() for g in ds.values()])

    def update_drt_multi(cycle_range, intensity_max, log_tau_max, selected_ds):
        start, end = cycle_range
        # For simplicity, we only contour the FIRST selected dataset
        # Overlapping contours are too confusing.
        ds_name = selected_ds
        ds_cycles = sorted(list(eis_dicts[ds_name].keys()))
        selected_cycles = [c for c in ds_cycles if start <= c <= end]
        
        if len(selected_cycles) < 2:
            print(f"Please select a range of at least 2 cycles for {ds_name} to generate the Contour Map.")
            return
            
        gamma_matrix = np.array([gamma_dict[ds_name][c] for c in selected_cycles])
        
        tau_max = 10**log_tau_max
        tau_min = np.min(tau_ref)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # --- PLOT 1: 2D Overlapping Curves ---
        for i, c in enumerate(selected_cycles):
            color = cm.plasma(c / max(ds_cycles)) if max(ds_cycles) > 0 else 'blue'
            ax1.semilogx(tau_ref, gamma_matrix[i], color=color, linewidth=1.5)

        ax1.set_xlim(left=tau_min, right=tau_max)
        ax1.set_ylim(bottom=0, top=intensity_max)
        ax1.set_xlabel('Relaxation Time $\\tau$ (s)', fontsize=12)
        ax1.set_ylabel(r'$\gamma(\tau)$ ($\Omega$)', fontsize=12)
        ax1.set_title(f'Overlapping DRT ({ds_name} Cycles {start}-{end})', fontsize=14)
        ax1.grid(True, alpha=0.5)

        sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=plt.Normalize(vmin=min(ds_cycles), vmax=max(ds_cycles)))
        cbar1 = fig.colorbar(sm, ax=ax1)
        cbar1.set_label('Cycle Number')

        # --- PLOT 2: 2D Contour Map (Heatmap) ---
        X, Y = np.meshgrid(tau_ref, selected_cycles)
        contour = ax2.contourf(X, Y, gamma_matrix, levels=np.linspace(0, intensity_max, 30), cmap='viridis', extend='max')

        ax2.set_xscale('log') 
        ax2.set_xlim(left=tau_min, right=tau_max)
        ax2.set_xlabel('Relaxation Time $\\tau$ (s)', fontsize=12)
        ax2.set_ylabel('Cycle Number', fontsize=12)
        ax2.set_title(f'DRT Contour Map ({ds_name} Cycles {start}-{end})', fontsize=14)

        cbar2 = fig.colorbar(contour, ax=ax2)
        cbar2.set_label(r'$\gamma(\tau)$ Intensity ($\Omega$)')

        plt.tight_layout()
        plt.show()

    cycle_range_slider = widgets.IntRangeSlider(
        value=[cycle_ids[0] if cycle_ids else 0, cycle_ids[-1] if cycle_ids else 1],
        min=min(cycle_ids) if cycle_ids else 0, max=max(cycle_ids) if cycle_ids else 1, step=1,
        description='Cycles:', continuous_update=False, orientation='horizontal'
    )

    intensity_slider = widgets.FloatSlider(
        value=global_gamma_max, min=0.1, max=global_gamma_max*1.2, step=0.5,
        description='Intensity:', continuous_update=False, orientation='horizontal',
        tooltip="Lower this to artificially boost the brightness of tiny peaks."
    )

    tau_max_slider = widgets.FloatSlider(
        value=np.log10(np.max(tau_ref)), min=np.log10(np.min(tau_ref)), max=np.log10(np.max(tau_ref)), step=0.1,
        description='log(Max $\\tau$):', continuous_update=False, orientation='horizontal',
        tooltip="Slide left to zoom in and hide the high-tau (low frequency) noise."
    )
    
    drt_contour_ds_selector = widgets.Dropdown(
        options=dataset_names, value=dataset_names[0], description='Dataset:', disabled=False
    )

    widgets.interact(update_drt_multi, cycle_range=cycle_range_slider, intensity_max=intensity_slider, log_tau_max=tau_max_slider, selected_ds=drt_contour_ds_selector);"""))

nb.cells = cells

with open('EIS_analysis.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook created successfully.")
