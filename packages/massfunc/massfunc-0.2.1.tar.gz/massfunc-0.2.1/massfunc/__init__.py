"""
MassFunc: A Python package for cosmological mass function calculations.

This package provides tools for calculating cosmological mass functions,
collapse fractions, and star formation rate densities.
"""

from .massfunc import CosmologySet, Mass_func, Collapse_fraction, SFRD

__version__ = "0.2.0"
__author__ = "SOYONAOC"
__email__ = "onmyojiflow@gmail.com"

__all__ = ['CosmologySet', 'Mass_func', 'Collapse_fraction', 'SFRD']
