# XXIOP: Cosmological 21cm Signal Toolkit

[![PyPI version](https://badge.fury.io/py/xxiop.svg)](https://badge.fury.io/py/xxiop)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`xxiop` is a Python package designed for researchers in cosmology to perform calculations related to the 21cm signal from the Epoch of Reionization. It provides tools to compute the Thomson scattering optical depth and to calculate, analyze, and visualize the 21cm brightness temperature power spectrum from given cosmological fields.

## Features

- **Thomson Optical Depth**: Calculate the optical depth from a given reionization history (ionization fraction vs. redshift).
- **21cm Brightness Temperature**: Compute the 21cm brightness temperature ($\delta T_b$) field from matter density and ionization fraction fields.
- **Power Spectrum Analysis**: Calculate the dimensionless power spectrum $\Delta^2(k)$ of the 21cm signal or any other 3D field.
- **Visualization**: Integrated plotting functions to visualize 2D slices of ionization and 21cm fields, and to plot the resulting power spectrum with error bars.
- **Customizable Cosmology**: Easily set custom cosmological parameters (`h`, `omegam`, `ns`, `sigma8`) for all calculations.

## Installation

You can install `xxiop` directly from PyPI:

```bash
pip install xxiop
```

## Core Dependencies

The package relies on the following scientific libraries:
- `numpy`
- `scipy`
- `astropy`
- `matplotlib`
- `massfunc`

All dependencies will be automatically installed via pip.

## Usage Examples

Here are some basic examples of how to use the core functionalities of the `xxiop` package.

### 1. Calculate Thomson Optical Depth

You can calculate the integrated optical depth up to a certain redshift given a reionization history.

```python
import numpy as np
from xxiop.op import OpticalDepth

# 1. Define a sample reionization history (ionization fraction vs. redshift)
z_history = np.linspace(5, 15, 100)
# Mock ionization fraction: starts near 0, ends near 1
ionf_history = 1.0 / (1.0 + np.exp((z_history - 10) / 1.0))

# 2. Initialize the calculator with this history
# You can also provide custom cosmological parameters, e.g., h=0.67, omegam=0.32
tau_calculator = OpticalDepth(z=z_history, ionf=ionf_history)

# 3. Calculate the optical depth up to z=7.5
z_target = 7.5
tau = tau_calculator.OpticalDepth(z=z_target)

print(f"Thomson Optical Depth (τ) at z={z_target}: {tau:.4f}")
```

### 2. Calculate 21cm Power Spectrum

Given 3D cubes of the matter density field and ionization fraction, you can compute and plot the 21cm power spectrum.

```python
import numpy as np
from xxiop.op import XXIPowerSpectrum

# 1. Generate mock 3D cosmological fields
box_dim = 128  # Grid dimension
box_length_mpc = 200.0  # Box size in Mpc/h

# Mock matter density contrast field: delta_R = (rho / rho_bar) - 1
delta_r_field = np.random.randn(box_dim, box_dim, box_dim)

# Mock ionization fraction field (0=neutral, 1=ionized)
# Create a simple ionized bubble in the center
ion_fraction_field = np.zeros((box_dim, box_dim, box_dim))
center, radius = box_dim // 2, 30
x, y, z = np.ogrid[:box_dim, :box_dim, :box_dim]
mask = (x - center)**2 + (y - center)**2 + (z - center)**2 < radius**2
ion_fraction_field[mask] = 1.0

# 2. Initialize the power spectrum calculator
ps_calculator = XXIPowerSpectrum(h=0.674, omegam=0.315)

# 3. Calculate the 21cm brightness temperature field
# This is an intermediate step, but useful for visualization
z_snapshot = 8.0
delta_tb_field = ps_calculator.XXI_Field(
    z=z_snapshot,
    deltaR=delta_r_field,
    ionf=ion_fraction_field
)

# 4. Calculate the power spectrum from the 21cm field
# The PowerSpectrum method takes the 3D field and box length as input
k, delta_sq, error = ps_calculator.PowerSpectrum(
    field=delta_tb_field,
    box_length=box_length_mpc,
    num_bins=30  # Optional: number of bins for k
)

print("Power spectrum calculation complete.")
print(f"k (h/Mpc):\n{k[:5]}")
print(f"Δ^2(k) (mK^2):\n{delta_sq[:5]}")

# 5. Use the built-in plotting function to visualize the result
# This will also save a plot to the 'figure_deltaTb/' directory
ps_calculator.PowerSpectrumPlot(
    field=delta_tb_field,
    box_length=box_length_mpc,
    label=f'Power Spectrum at z={z_snapshot}'
)

print("Plot saved to figure_deltaTb/PowerSpectrum_...png")
```
## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
