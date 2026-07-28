import pandas as pd
import numpy as np
from scipy.optimize import nnls
import matplotlib.pyplot as plt

filepath = r'data\20260722_C23_SMSP20_operando_EIS_C01.mpt'
skip_rows = 0
for i, line in enumerate(open(filepath, 'r', encoding='latin-1')):
    if line.startswith('mode'): skip_rows=i; break;
df = pd.read_csv(filepath, sep='\t', skiprows=skip_rows, encoding='latin-1')

g = df[df['z cycle']==1].dropna(subset=['freq/Hz'])
g = g[(g['freq/Hz'] >= 0.09) & (g['Re(Z)/Ohm'] != 0.0)]

freq = g['freq/Hz'].values
Z_imag = g['-Im(Z)/Ohm'].values * -1  # Negative imaginary part
Z_imag_data = -Z_imag # The formula typically fits against the negative imaginary part (which is usually positive in Nyquist)

# Time constants based on frequencies
omega = 2 * np.pi * freq
tau = 1 / omega

# Construct A matrix for Z_imag
# Z_imag(omega) = sum_k gamma_k * [ (-omega * tau_k) / (1 + (omega*tau_k)^2) ]
A = np.zeros((len(omega), len(tau)))
for i, w in enumerate(omega):
    for j, t in enumerate(tau):
        # We model the positive "Negative Imaginary part" (which is commonly plotted on Y-axis)
        # -Z_imag = sum (gamma * w * t) / (1 + (w*t)^2)
        A[i, j] = (w * t) / (1 + (w * t)**2)

# Tikhonov regularization (2nd derivative is standard)
# L matrix for 2nd derivative (discrete)
n = len(tau)
L = np.zeros((n-2, n))
for i in range(n-2):
    L[i, i] = 1
    L[i, i+1] = -2
    L[i, i+2] = 1

lam = 0.01  # Regularization parameter
A_aug = np.vstack([A, np.sqrt(lam) * L])
b_aug = np.hstack([Z_imag_data, np.zeros(n-2)])

# Solve using Non-Negative Least Squares
gamma_opt, residual = nnls(A_aug, b_aug)

print("NNLS Residual:", residual)
print("Gamma max:", np.max(gamma_opt))
print("Number of peaks:", np.sum(gamma_opt > 0.05 * np.max(gamma_opt)))
