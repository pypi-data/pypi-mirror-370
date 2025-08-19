# BubbleBarrier

[![PyPI version](https://badge.fury.io/py/bubblebarrier.svg)](https://badge.fury.io/py/bubblebarrier)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A Python package for calculating bubble barriers in cosmic reionization models. This package provides tools for modeling barrier functions used in studies of the epoch of reionization.

## Features

- **Barrier Functions**: Calculate δ_v barriers for reionization modeling
- **Mass Function Integration**: Efficient numerical integration for halo mass functions
- **Parallel Processing**: Built-in support for parallel computation using joblib
- **Astrophysical Parameters**: Configurable escape fraction, ionizing photon production, and other physical parameters
- **Minihalo Effects**: Include X-ray heating effects from minihalos

## Installation

### From PyPI (recommended)

```bash
pip install bubblebarrier
```

### From Source

```bash
git clone https://github.com/SOYONAOC/BubbleBarrier.git
cd BubbleBarrier
pip install -e .
```

## Quick Start

```python
import numpy as np
from bubblebarrier import Barrier

# Initialize barrier model
barrier = Barrier(
    fesc=0.2,      # Escape fraction
    qion=20000.0,  # Ionizing photons per baryon
    z_v=12.0,      # Redshift
    nrec=3,        # Recombination parameter
    xi=100.0       # X-ray heating efficiency
)

# Calculate ionizing photon number
Mv = 1e15
delta_R = 0.1
N_ion = barrier.Nion(Mv, delta_R)

# Calculate barrier height
delta_v = barrier.Calcul_deltaVM(Mv)

print(f"Ionizing photon number: {N_ion:.3e}")
print(f"Barrier height δ_v: {delta_v:.3f}")
```

## Core Classes

### Barrier Class

The `Barrier` class computes barrier heights for ionization balance.

**Parameters:**
- `fesc` (float): Escape fraction of ionizing photons (default: 0.2)
- `qion` (float): Ionizing photons per stellar baryon (default: 20000.0)
- `z_v` (float): Redshift of interest (default: 12.0)
- `nrec` (int): Recombination clumping factor (default: 3)
- `xi` (float): X-ray heating efficiency (default: 100.0)

**Key Methods:**
- `Nion(Mv, delta_R)`: Calculate ionizing photon production
- `Calcul_deltaVM(Mv)`: Compute barrier height δ_v
- `Calcul_deltaVM_Minihalo(Mv)`: Barrier calculation including minihalos
- `Calcul_deltaVM_Parallel(Mv_array)`: Parallel computation for multiple masses
- `Calcul_deltaVM_Minihalo_Parallel(Mv_array)`: Parallel computation with minihalo effects

## Advanced Usage

### Parallel Computation

```python
# Calculate barriers for multiple halo masses in parallel
Mv_array = np.logspace(14, 17, 50)  # Range of halo masses
delta_v_results = barrier.Calcul_deltaVM_Parallel(Mv_array)
```

### Including Minihalo Effects

```python
# Calculate barriers including X-ray heating from minihalos
delta_v_minihalos = barrier.Calcul_deltaVM_Minihalo_Parallel(Mv_array)
```

### Parameter Studies

```python
# Study the effect of different escape fractions
fesc_values = [0.1, 0.2, 0.3]
barriers = [Barrier(fesc=f, z_v=12.0) for f in fesc_values]
results = [b.Calcul_deltaVM(1e15) for b in barriers]

print("Escape fraction vs Barrier height:")
for fesc, delta_v in zip(fesc_values, results):
    print(f"fesc = {fesc:.1f}: δ_v = {delta_v:.3f}")
```

## Physical Background

This package implements models for:

1. **Barrier Method**: Calculates the density threshold required for halo formation in ionized regions
2. **Ionization Balance**: Self-consistent treatment of ionization and recombination
3. **Mass Functions**: Modified halo mass functions accounting for ionization feedback
4. **X-ray Heating**: Effects of X-ray sources from minihalos on reionization

The models are particularly useful for:
- 21cm signal predictions
- Reionization simulations
- Studying the connection between galaxies and ionized bubbles
- Modeling the impact of X-ray sources on reionization

## Dependencies

- `numpy >= 1.18.0`
- `scipy >= 1.5.0`
- `astropy >= 4.0`
- `matplotlib >= 3.0.0`
- `pandas >= 1.0.0`
- `joblib >= 1.0.0`
- `massfunc` (custom cosmology package - includes SFRD and other cosmological functions)

## Examples

See the `examples/` directory for Jupyter notebooks demonstrating:
- Basic barrier calculations
- Parameter sensitivity studies
- Parallel computation examples
- Minihalo effects analysis

## Citation

If you use this package in your research, please cite:

```bibtex
@misc{bubblebarrier2025,
  author = {Hajime Hinata},
  title = {BubbleBarrier: A Python package for reionization bubble modeling},
  year = {2025},
  url = {https://github.com/SOYONAOC/BubbleBarrier}
}
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Author**: Hajime Hinata
- **Email**: onmyojiflow@gmail.com
- **GitHub**: [SOYONAOC](https://github.com/SOYONAOC)

## Acknowledgments

- Based on the barrier method for reionization modeling
- Implements algorithms from modern reionization literature
- Thanks to the astrophysics community for theoretical foundations
