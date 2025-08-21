"""
Brutsaert (1975) Atmospheric Emissivity Model
=============================================

This module provides an implementation of the Brutsaert (1975) empirical model for clear-sky atmospheric emissivity.
The Brutsaert model is widely used in land surface energy balance and hydrometeorological studies to estimate the efficiency
of the atmosphere in emitting longwave radiation back to the Earth's surface, primarily as a function of air temperature and water vapor pressure.

Key Features:
-------------
- Implements the Brutsaert (1975) formula for clear-sky atmospheric emissivity.
- Accepts scalar, numpy array, or Raster inputs for flexible geospatial and scientific workflows.
- Returns emissivity values typically in the range 0.7–0.9 for clear-sky conditions.

Reference:
----------
Brutsaert, W. (1975). On a Derivable Formula for Long‐Wave Radiation from Clear Skies.
Water Resources Research, 11(5), 742–744. https://doi.org/10.1029/WR011i005p00742

Example Usage:
--------------
>>> from brutsaert_atmospheric_emissivity import brutsaert_atmospheric_emissivity
>>> emissivity = brutsaert_atmospheric_emissivity(Ea_Pa=1200, Ta_K=293.15)

"""

import numpy as np
from rasters import Raster
from typing import Union

from rasters import SpatialGeometry, RasterGeometry

def brutsaert_atmospheric_emissivity(
        Ea_Pa: Union[Raster, np.ndarray, float],
        Ta_K: Union[Raster, np.ndarray, float],
        geometry: SpatialGeometry = None,
        ) -> Union[Raster, np.ndarray, float]:
    """
    Calculate clear-sky atmospheric emissivity using the Brutsaert (1975) model.

    This function implements the Brutsaert (1975) empirical formula for clear-sky
    atmospheric emissivity as a function of air temperature and water vapor pressure.
    The model is widely used in land surface energy balance studies.

    Physics:
        - Atmospheric emissivity (ε_a) quantifies the efficiency of the atmosphere
          in emitting longwave radiation back to the surface.
        - Water vapor is the primary greenhouse gas affecting clear-sky emissivity.
        - Brutsaert's formula is based on radiative transfer theory and empirical
          calibration for clear-sky conditions.

    Formula:
        η₁ = 0.465 * eₐ / Tₐ
        ε_a = 1 - (1 + η₁) * exp(-sqrt(1.2 + 3η₁))
        where:
            eₐ  = actual vapor pressure (Pa)
            Tₐ  = air temperature (K)

    Reference:
        Brutsaert, W. (1975). On a Derivable Formula for Long‐Wave Radiation from Clear Skies.
        Water Resources Research, 11(5), 742–744. https://doi.org/10.1029/WR011i005p00742

    Parameters
    ----------
    Ea_Pa : np.ndarray
        Actual vapor pressure in Pascals.
    Ta_K : np.ndarray
        Air temperature in Kelvin.

    Returns
    -------
    np.ndarray
        Atmospheric emissivity (unitless, typically 0.7–0.9 for clear sky).
    """
    # check if inputs are scalars
    scalar_processing = np.isscalar(Ea_Pa) and np.isscalar(Ta_K)
    
    if geometry is None and isinstance(Ea_Pa, Raster):
        geometry = Ea_Pa.geometry
    elif geometry is None and isinstance(Ta_K, Raster):
        geometry = Ta_K.geometry

    raster_processing = isinstance(geometry, RasterGeometry)

    # Convert to numpy arrays for calculation and ensure float dtype
    Ea_Pa_arr = np.asarray(Ea_Pa, dtype=float)
    Ta_K_arr = np.asarray(Ta_K, dtype=float)

    # Calculate the dimensionless water vapor parameter (η₁)
    eta1 = 0.465 * Ea_Pa_arr / Ta_K_arr

    # Argument for the square root in the exponent; must be non-negative
    eta2_arg = np.clip(1.2 + 3 * eta1, 0, None)

    if np.isscalar(eta2_arg):
        sqrt_eta2_arg = np.sqrt(eta2_arg) if eta2_arg >= 0 else np.nan
    else:
        sqrt_eta2_arg = np.where(eta2_arg >= 0, np.sqrt(eta2_arg), np.nan)
    eta2 = -sqrt_eta2_arg

    # Exponential decay term representing atmospheric absorption
    eta3 = np.exp(eta2)

    # Brutsaert's formula for clear-sky atmospheric emissivity
    atmospheric_emissivity = np.where(
        eta2 != 0,
        (1 - (1 + eta1) * eta3),
        np.nan
    )

    # If both inputs were scalars, return a float, else return array
    if scalar_processing:
        return float(np.squeeze(atmospheric_emissivity))
    elif raster_processing:
        return Raster(atmospheric_emissivity, geometry=geometry)
    else:
        return atmospheric_emissivity
