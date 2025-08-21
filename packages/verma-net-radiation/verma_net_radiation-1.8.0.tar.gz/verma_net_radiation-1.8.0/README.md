
# Net Radiation and Daylight Upscaling Remote Sensing in Python

This Python package implements the net radiation and daylight upscaling methods described in Verma et al 2016.

[Gregory H. Halverson](https://github.com/gregory-halverson-jpl) (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
Lead developer<br>
NASA Jet Propulsion Laboratory 329G

## Installation

This package is distributed using the pip package manager as `verma-net-radiation` with dashes.

```
pip install verma-net-radiation
```

## Usage

Import this package as `verma_net_radiation` with underscores.


This module provides functions to calculate instantaneous net radiation and its components, integrate daylight net radiation, and process radiation data from a DataFrame. Below is a detailed explanation of each function and how to use them.


### `verma_net_radiation`

**Description**:  
Calculates instantaneous net radiation and its components based on input parameters. Optionally upscales to daylight average net radiation if `upscale_to_daylight=True`.

**Parameters**:
- `ST_C` (Union[Raster, np.ndarray, float]): Surface temperature in Celsius.
- `emissivity` (Union[Raster, np.ndarray, float]): Surface emissivity (unitless, constrained between 0 and 1).
- `albedo` (Union[Raster, np.ndarray, float]): Surface albedo (unitless, constrained between 0 and 1).
- `SWin_Wm2` (Union[Raster, np.ndarray, float], optional): Incoming shortwave radiation (W/m²). If not provided, will be retrieved from GEOS-5 FP if geometry and time_UTC are given.
- `Ta_C` (Union[Raster, np.ndarray, float], optional): Air temperature in Celsius. If not provided, will be retrieved from GEOS-5 FP if geometry and time_UTC are given.
- `RH` (Union[Raster, np.ndarray, float], optional): Relative humidity (fractional, e.g., 0.5 for 50%). If not provided, will be retrieved from GEOS-5 FP if geometry and time_UTC are given.
- `geometry` (RasterGeometry, optional): Spatial geometry for GEOS-5 FP retrievals.
- `time_UTC` (datetime, optional): UTC time for GEOS-5 FP retrievals.
- `GEOS5FP_connection` (GEOS5FP, optional): Existing GEOS5FP connection to use for data retrievals.
- `resampling` (str, optional): Resampling method for GEOS-5 FP data retrievals.
- `cloud_mask` (Union[Raster, np.ndarray, float], optional): Boolean mask indicating cloudy areas (True for cloudy).
- `upscale_to_daylight` (bool, optional): If True, returns daylight average net radiation as well.

**Returns**:
A dictionary containing:
- `"SWout_Wm2"`: Outgoing shortwave radiation (W/m²).
- `"LWin_Wm2"`: Incoming longwave radiation (W/m²).
- `"LWout_Wm2"`: Outgoing longwave radiation (W/m²).
- `"Rn_Wm2"`: Instantaneous net radiation (W/m²).
- `"Rn_daylight_Wm2"`: Daylight average net radiation (W/m², only if `upscale_to_daylight=True`).

**Example**:
```python
results = verma_net_radiation(
  ST_C=surface_temp_array,
  emissivity=emissivity_array,
  albedo=albedo_array,
  SWin_Wm2=SWin_array,
  Ta_C=air_temp_array,
  RH=relative_humidity_array,
  cloud_mask=cloud_mask_array,
  upscale_to_daylight=True
)
```


### `daylight_Rn_integration_verma`

**Description**:  
Integrates instantaneous net radiation (Rn) to daylight average values using solar geometry parameters. Supports Raster, numpy array, or float inputs. If sunrise time or daylight hours are not provided, they are calculated from day of year and latitude.

**Parameters**:
- `Rn_Wm2` (Union[Raster, np.ndarray, float]): Instantaneous net radiation (W/m²).
- `hour_of_day` (Union[Raster, np.ndarray, float]): Hour of the day (0-24) when Rn is measured.
- `day_of_year` (Union[Raster, np.ndarray, float], optional): Day of the year (1-365).
- `lat` (Union[Raster, np.ndarray, float], optional): Latitude in degrees.
- `sunrise_hour` (Union[Raster, np.ndarray, float], optional): Hour of sunrise (local time).
- `daylight_hours` (Union[Raster, np.ndarray, float], optional): Total daylight hours.

**Returns**:
- `Union[Raster, np.ndarray, float]`: Daylight average net radiation (W/m²).

**Notes**:
- To obtain total daylight energy (J/m²), multiply the result by `(daylight_hours * 3600)`.
- If `sunrise_hour` or `daylight_hours` are not provided, they are computed from `day_of_year` and `lat` using solar geometry.

**Example**:
```python
Rn_daylight = daylight_Rn_integration_verma(
  Rn_Wm2=Rn_array,
  hour_of_day=hour_of_day_array,
  day_of_year=day_of_year_array,
  lat=latitude_array,
  sunrise_hour=sunrise_hour_array,
  daylight_hours=daylight_hours_array
)
```

---

### `verma_net_radiation_table`

**Description**:  
Processes a DataFrame containing inputs for Verma net radiation calculations and appends the results as new columns.

**Parameters**:
- `verma_net_radiation_inputs_df` (DataFrame): A DataFrame containing the following columns:
  - `Rg`: Incoming shortwave radiation (W/m²).
  - `albedo`: Surface albedo (unitless, constrained between 0 and 1).
  - `ST_C`: Surface temperature in Celsius.
  - `EmisWB` or `emissivity`: Surface emissivity (unitless, constrained between 0 and 1).
  - `Ta_C`: Air temperature in Celsius.
  - `RH`: Relative humidity (fractional, e.g., 0.5 for 50%).

**Returns**:
- `DataFrame`: A copy of the input DataFrame with additional columns for the calculated radiation components:
  - `SWout`: Outgoing shortwave radiation (W/m²).
  - `LWin`: Incoming longwave radiation (W/m²).
  - `LWout`: Outgoing longwave radiation (W/m²).
  - `Rn`: Instantaneous net radiation (W/m²).

**Example**:
```python
output_df = verma_net_radiation_table(input_df)
```

## References

**Brutsaert, W. (1975).** On a Derivable Formula for Long‐Wave Radiation from Clear Skies. *Water Resources Research, 11*(5), 742–744. https://doi.org/10.1029/WR011i005p00742  
*Empirical model for clear-sky atmospheric emissivity, used in the calculation of incoming longwave radiation.*

**Liou, K. N. (2002).** *An Introduction to Atmospheric Radiation* (2nd ed.). Academic Press. (See Eq. 2.3.1)  
*Textbook reference for the Stefan-Boltzmann Law and radiative transfer theory, used for outgoing longwave radiation calculations.*

**Stefan, J. (1879).** Über die Beziehung zwischen der Wärmestrahlung und der Temperatur. *Sitzungsberichte der mathematisch-naturwissenschaftlichen Classe der kaiserlichen Akademie der Wissenschaften*, 79, 391–428.  
*Original publication of the Stefan-Boltzmann Law, fundamental to blackbody radiation calculations.*

**Verma, M., Fisher, J. B., Mallick, K., Ryu, Y., Kobayashi, H., Guillaume, A., Moore, G., Ramakrishnan, L., Hendrix, V. C., Wolf, S., Sikka, M., Kiely, G., Wohlfahrt, G., Gielen, B., Roupsard, O., Toscano, P., Arain, A., & Cescatti, A. (2016).** Global surface net-radiation at 5 km from MODIS Terra. *Remote Sensing, 8*, 739. [Link](https://api.semanticscholar.org/CorpusID:1517647)  
*Primary methodology for net radiation and daylight upscaling as implemented in this package.*
