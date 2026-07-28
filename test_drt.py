import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

filepath = r'data\20260722_C23_SMSP20_operando_EIS_C01.mpt'
skip_rows = 0
for i, line in enumerate(open(filepath, 'r', encoding='latin-1')):
    if line.startswith('mode'): skip_rows=i; break;
df = pd.read_csv(filepath, sep='\t', skiprows=skip_rows, encoding='latin-1')

# Get cycle 1 data
g = df[df['z cycle']==1].dropna(subset=['freq/Hz'])
g = g[(g['freq/Hz'] >= 0.09) & (g['Re(Z)/Ohm'] != 0.0)]

freq = g['freq/Hz'].values
Z_imag = g['-Im(Z)/Ohm'].values * -1  # Actual imaginary part (negative)

omega = 2 * np.pi * freq
tau = 1 / omega  # Use reciprocal frequencies as time constants

# Construct A matrix for the imaginary part
# Z_imag = - sum ( gamma * omega * tau / (1 + (omega*tau)^2) )
A = np.zeros((len(omega), len(tau)))
for i, w in enumerate(omega):
    for j, t in enumerate(tau):
        A[i, j] = - (w * t) / (1 + (w * t)**2)

# We want to solve A * gamma = Z_imag
# Objective: || A*gamma - Z_imag ||^2 + lambda * || gamma ||^2
lam = 0.1  # Regularization parameter

def objective(gamma):
    return np.sum((np.dot(A, gamma) - Z_imag)**2) + lam * np.sum(np.diff(gamma)**2)

# Initial guess
gamma0 = np.ones_like(tau) * 0.1
bounds = [(0, None) for _ in tau]  # Non-negative constraint

res = minimize(objective, gamma0, bounds=bounds)
gamma_opt = res.x

print("Optimization success:", res.success)
print("Gamma array:", gamma_opt[:5], "...", gamma_opt[-5:])
