"""
Provides a function to calculate outgoing longwave radiation from land surface temperature and emissivity using the Stefan-Boltzmann Law.

References:
    Liou, K. N. (2002). An Introduction to Atmospheric Radiation (2nd ed.). Academic Press. (Eq. 2.3.1)
    Stefan, J. (1879). Über die Beziehung zwischen der Wärmestrahlung und der Temperatur. Sitzungsberichte der mathematisch-naturwissenschaftlichen Classe der kaiserlichen Akademie der Wissenschaften, 79, 391–428.
"""

from typing import Union
import numpy as np
from rasters import Raster

STEFAN_BOLTZMAN_CONSTANT = 5.67036713e-8  # W·m⁻²·K⁻⁴

def outgoing_longwave_radiation(
    emissivity: Union[Raster, np.ndarray, float],
    surface_temperature_K: Union[Raster, np.ndarray, float]
    ) -> Union[Raster, np.ndarray, float]:
    """
    Calculate outgoing longwave radiation from land surface temperature and emissivity.

    Uses the Stefan-Boltzmann Law:
        LWout = emissivity × σ × (T_surface in Kelvin)^4
    where σ is the Stefan-Boltzmann constant (5.67036713e-8 W·m⁻²·K⁻⁴).

    References:
        Liou, K. N. (2002). An Introduction to Atmospheric Radiation (2nd ed.). Academic Press. (Eq. 2.3.1)
        Stefan, J. (1879). Über die Beziehung zwischen der Wärmestrahlung und der Temperatur. Sitzungsberichte der mathematisch-naturwissenschaftlichen Classe der kaiserlichen Akademie der Wissenschaften, 79, 391–428.

    Parameters:
        emissivity: Surface emissivity (unitless, 0–1)
        surface_temperature_K: Land surface temperature in Kelvin

    Returns:
        Outgoing longwave radiation (W/m²)
    """
    emissivity = np.clip(emissivity, 0, 1)
    return emissivity * STEFAN_BOLTZMAN_CONSTANT * surface_temperature_K ** 4
