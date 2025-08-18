# MassFunc

A Python package for cosmological mass function calculations, including Press-Schechter, Sheth-Tormen mass functions, star formation rate density calculations, and more.

## Features

- **Cosmological calculations**: Support for various cosmological parameters and models
- **Mass function calculations**: Implements Press-Schechter and Sheth-Tormen mass functions
- **Star formation rate density**: Calculate SFRD with customizable parameters
- **Collapse fraction**: Tools for calculating collapse fractions
- **Efficient interpolation**: Built-in interpolation for fast calculations

## Installation

### From PyPI (recommended)

```bash
pip install massfunc
```

### From source

```bash
git clone https://github.com/SOYONAOC/MassFunction.git
cd massfunc
pip install -e .
```

## Quick Start

```python
import massfunc

# Create a mass function calculator with default cosmology
mf = massfunc.Mass_func(ns=0.965, sigma8=0.811, h=0.674, omegam=0.315)

# Setup interpolation for faster calculations
mf.sigma2_interpolation_set()
mf.dsig2dm_interpolation_set()

# Calculate mass function at z=0 for a range of masses
import numpy as np
masses = np.logspace(10, 15, 100)  # 10^10 to 10^15 solar masses
z = 0.0

# Press-Schechter mass function
dndm_ps = mf.dndmps(masses, z)

# Sheth-Tormen mass function
dndm_st = mf.dndmst(masses, z)

# Star formation rate density
sfrd = massfunc.SFRD(ns=0.965, sigma8=0.811)
rho_sfr = sfrd.rhosfr(1e4, 1e8, z)
```

## Classes and Methods

### CosmologySet
Base class for cosmological parameters:
- `h`: Dimensionless Hubble parameter
- `omegam`: Matter density parameter
- `omegab`: Baryon density parameter
- `omegalam`: Dark energy density parameter

### Mass_func
Main class for mass function calculations:
- `sigma2()`: Variance of density field
- `dndmps()`: Press-Schechter mass function
- `dndmst()`: Sheth-Tormen mass function
- `dndmeps()`: Extended PS mass function

### Collapse_fraction
Calculate collapse fractions:
- `fcoll()`: Collapse fraction
- `dfcolldz()`: Derivative of collapse fraction with redshift

### SFRD
Star formation rate density calculations:
- `rhosfr()`: Star formation rate density
- `fstar()`: Star formation efficiency
- `fduty()`: Duty cycle

## Dependencies

- numpy >= 1.18.0
- scipy >= 1.5.0
- astropy >= 4.0
- matplotlib >= 3.0.0
- sympy >= 1.6.0
- joblib >= 1.0.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{massfunc,
  author = {Your Name},
  title = {MassFunc: A Python package for cosmological mass function calculations},
  url = {https://github.com/yourusername/massfunc},
  version = {0.1.0},
  year = {2025}
}
```

## Support

If you encounter any issues or have questions, please file an issue on the [GitHub repository](https://github.com/yourusername/massfunc/issues).


## Update log

### Version 0.1.1
- Added EPS (Extended Press-Schechter) collapse fraction calculation
- New method `fcolleps()` in Collapse_fraction class
- Enhanced collapse fraction functionality



