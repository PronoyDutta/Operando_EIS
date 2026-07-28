import pandas as pd
import numpy as np
from scipy.optimize import nnls
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

filepath = r'data\20260722_C23_SMSP20_operando_EIS_C01.mpt'
skip_rows = 0
for i, line in enumerate(open(filepath, 'r', encoding='latin-1')):
    if line.startswith('mode'): skip_rows=i; break;
df = pd.read_csv(filepath, sep='\t', skiprows=skip_rows, encoding='latin-1')

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
        L[i, i] = 1; L[i, i+1] = -2; L[i, i+2] = 1
    A_aug = np.vstack([A, np.sqrt(lam) * L])
    b_aug = np.hstack([Z_imag, np.zeros(n-2)])
    gamma_opt, _ = nnls(A_aug, b_aug)
    return tau, gamma_opt

eis_dict = {}
for cycle, group in df.groupby('z cycle'):
    group = group.dropna(subset=['freq/Hz'])
    group = group[(group['freq/Hz'] != 0.0) & (group['Re(Z)/Ohm'] != 0.0)]
    group = group[group['freq/Hz'] >= 0.09]
    freq = group['freq/Hz'].values
    Z = group['Re(Z)/Ohm'].values + 1j * group['-Im(Z)/Ohm'].values * -1
    eis_dict[cycle] = (freq, Z)

cycle_ids = sorted(list(eis_dict.keys()))
lam = 10**-2.0
master_freq, _ = eis_dict[cycle_ids[-1]]
tau_ref = 1 / (2 * np.pi * master_freq)

gamma_matrix = []
for c in cycle_ids:
    freq, Z = eis_dict[c]
    tau, gamma = compute_drt(freq, -Z.imag, lam)
    f_interp = interp1d(np.log10(tau), gamma, bounds_error=False, fill_value=0.0)
    gamma_matrix.append(f_interp(np.log10(tau_ref)))

gamma_matrix = np.array(gamma_matrix)
print("Gamma matrix shape:", gamma_matrix.shape)
