"""
Incoming Longwave Radiation Calculation
======================================

This module provides a function to calculate incoming longwave radiation (LWin) at the Earth's surface, accounting for both clear and cloudy sky conditions.
It uses the Stefan-Boltzmann Law and allows for flexible input types (Raster, numpy array, or float).

Key Features:
-------------
- Computes LWin for clear-sky (using atmospheric emissivity) and cloudy-sky (blackbody) conditions.
- Supports geospatial and scientific workflows with Raster, numpy array, or float inputs.
- Compatible with empirical emissivity models (e.g., Brutsaert 1975).

References:
-----------
- Brutsaert, W. (1975). On a Derivable Formula for Long‐Wave Radiation from Clear Skies. Water Resources Research, 11(5), 742–744. https://doi.org/10.1029/WR011i005p00742
- Planck, M. (1901). On the Law of Distribution of Energy in the Normal Spectrum. Annalen der Physik, 4(553), 1.

Example Usage:
--------------
>>> from incoming_longwave_radiation import incoming_longwave_radiation
>>> LWin = incoming_longwave_radiation(atmospheric_emissivity=0.8, Ta_K=290)
"""

import numpy as np
from rasters import Raster
from typing import Union

STEFAN_BOLTZMAN_CONSTANT = 5.67036713e-8  # W/m^2/K^4

def incoming_longwave_radiation(
        atmospheric_emissivity: Union[Raster, np.ndarray, float],
        Ta_K: Union[Raster, np.ndarray, float],
        cloud_mask: Union[Raster, np.ndarray, None] = None
        ) -> Union[Raster, np.ndarray, float]:
    """
    Calculate incoming longwave radiation (LWin) at the surface.

    For clear sky, this uses the Stefan-Boltzmann Law with atmospheric emissivity:
        LWin = emissivity * sigma * Ta_K^4
    where sigma is the Stefan-Boltzmann constant and Ta_K is air temperature in Kelvin.
    For cloudy sky, incoming longwave is assumed to be blackbody emission:
        LWin = sigma * Ta_K^4
    If a cloud mask is provided, clear-sky and cloudy-sky values are combined.

    Physics:
        - The Stefan-Boltzmann Law describes blackbody emission of longwave radiation.
        - Atmospheric emissivity is typically estimated using an empirical model (e.g., Brutsaert 1975).
        - For cloudy sky, the atmosphere is assumed to emit as a blackbody (emissivity = 1).

    References:
        - Brutsaert, W. (1975). On a Derivable Formula for Long‐Wave Radiation from Clear Skies. Water Resources Research, 11(5), 742–744. https://doi.org/10.1029/WR011i005p00742
        - Planck, M. (1901). On the Law of Distribution of Energy in the Normal Spectrum. Annalen der Physik, 4(553), 1.

    Parameters
    ----------
    atmospheric_emissivity : np.ndarray or float
        Atmospheric emissivity (unitless, typically 0.7–0.9 for clear sky).
    Ta_K : np.ndarray or float
        Air temperature in Kelvin.
    cloud_mask : np.ndarray or None, optional
        Boolean mask (True for cloudy, False for clear). If None, all-sky is assumed clear.

    Returns
    -------
    LWin : np.ndarray or float
        Incoming longwave radiation (W/m^2).
    """
    if cloud_mask is None:
        # Clear sky: use atmospheric emissivity
        return atmospheric_emissivity * STEFAN_BOLTZMAN_CONSTANT * Ta_K ** 4
    else:
        # Cloudy sky: combine clear and cloudy using mask
        return np.where(
            ~cloud_mask,
            atmospheric_emissivity * STEFAN_BOLTZMAN_CONSTANT * Ta_K ** 4,
            STEFAN_BOLTZMAN_CONSTANT * Ta_K ** 4
        )
