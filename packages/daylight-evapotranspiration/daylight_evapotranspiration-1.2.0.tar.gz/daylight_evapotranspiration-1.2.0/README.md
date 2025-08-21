# `daylight-evapotranspiration` Python Package

This package provides a set of functions for upscaling instantaneous or daily energy balance and meteorological data to daily evapotranspiration (ET) estimates. Below is a summary of each function and its usage:

[![CI](https://github.com/gregory-halverson-jpl/daily-evapotranspiration-upscaling/actions/workflows/ci.yml/badge.svg)](https://github.com/gregory-halverson-jpl/daily-evapotranspiration-upscaling/actions/workflows/ci.yml)


The `daylight-evapotranspiration` Python package provides utilities for upscaling energy balance and meteorological data to daily ET, supporting raster, numpy array, and scalar inputs. It is designed for remote sensing, land surface modeling, and geospatial analysis.

[Gregory H. Halverson](https://github.com/gregory-halverson-jpl) (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G

## Installation


This package is available on PyPI as `daylight-evapotranspiration`:

```bash
pip install daylight-evapotranspiration
```

## Usage


Import this package as `daylight_evapotranspiration`:

```python
import daylight_evapotranspiration
```

### 1. `celcius_to_kelvin(T_C)`
- **Description:** Convert Celsius to Kelvin. Implements $T_K = T_C + 273.15$ (IUPAC Green Book).
- **Parameters:** `T_C` (float, array, or raster): Temperature in Celsius.
- **Returns:** Temperature in Kelvin.

### 2. `lambda_Jkg_from_Ta_K(Ta_K)`
- **Description:** Calculate latent heat of vaporization from air temperature (Kelvin) using Henderson-Sellers (1984): $(2.501 - 0.002361 \times (T_a - 273.15)) \times 10^6$ J/kg.
- **Parameters:** `Ta_K` (float, array, or raster): Air temperature in Kelvin.
- **Returns:** Latent heat of vaporization (J/kg).

### 3. `lambda_Jkg_from_Ta_C(Ta_C)`
- **Description:** Calculate latent heat of vaporization from air temperature (Celsius). Converts to Kelvin, then applies Henderson-Sellers (1984).
- **Parameters:** `Ta_C` (float, array, or raster): Air temperature in Celsius.
- **Returns:** Latent heat of vaporization (J/kg).

### 4. `calculate_evaporative_fraction(LE, Rn, G)`
- **Description:** Compute evaporative fraction (EF) from latent heat flux, net radiation, and soil heat flux: $EF = LE / (Rn - G)$ (Shuttleworth, 1993).
- **Parameters:**
    - `LE` (float, array, or raster): Latent heat flux (W/m²)
    - `Rn` (float, array, or raster): Net radiation (W/m²)
    - `G` (float, array, or raster): Soil heat flux (W/m²)
- **Returns:** Evaporative fraction (unitless).

### 5. `daylight_ET_from_daylight_LE(LE_daylight_Wm2, daylight_hours=None, DOY=None, lat=None, datetime_UTC=None, geometry=None, lambda_Jkg=2450000.0)`
- **Description:** Estimate daylight ET (kg) from daylight latent heat flux (LE) and supporting parameters. Uses $ET = (LE_{daylight} \times \text{daylight seconds}) / \lambda$ (Monteith, 1965).
- **Parameters:** See function docstring for details.
- **Returns:** Daylight evapotranspiration (kg).

### 6. `daylight_ET_from_instantaneous_LE(LE_instantaneous_Wm2, Rn_instantaneous_Wm2, G_instantaneous_Wm2, day_of_year=None, lat=None, hour_of_day=None, sunrise_hour=None, daylight_hours=None, time_UTC=None, geometry=None, lambda_Jkg=2450000.0)`
- **Description:** Upscale instantaneous latent heat flux to daylight ET using EF and integrated net radiation (Verma et al., 1982; Anderson et al., 2007).
- **Parameters:**
    - `LE_instantaneous_Wm2` (float, array, or raster): Instantaneous latent heat flux (W/m²)
    - `Rn_instantaneous_Wm2` (float, array, or raster): Instantaneous net radiation (W/m²)
    - `G_instantaneous_Wm2` (float, array, or raster): Instantaneous soil heat flux (W/m²)
    - `day_of_year` (int): Day of year
    - `lat` (float): Latitude in degrees
    - `hour_of_day` (float): Local solar time (hours)
    - Additional parameters: see function docstring
- **Returns:** Daylight evapotranspiration (kg).

# References

- Henderson-Sellers, B. (1984). A new formula for latent heat of vaporization of water as a function of temperature. QJRMS, 110(466), 1186-1190.
- Shuttleworth, W.J. (1993). Evaporation models: A review. Agricultural and Forest Meteorology, 61(1-2), 13-35.
- Monteith, J.L. (1965). Evaporation and environment. Symposia of the Society for Experimental Biology, 19, 205-234.
- Verma, S.B., et al. (1982). Remote sensing of evapotranspiration for Nebraska Sandhills. Agricultural Meteorology, 26, 1-10.
- Anderson, M.C., et al. (2007). A two-source time-integrated model for estimating surface energy fluxes using thermal infrared remote sensing. Remote Sensing of Environment, 112(1), 213-229.
- Allen, R.G., Pereira, L.S., Raes, D., Smith, M., 1998. Crop evapotranspiration-Guidelines for computing crop water requirements-FAO Irrigation and drainage paper 56. FAO, Rome, 300(9).
- Bastiaanssen, W.G.M., Menenti, M., Feddes, R.A., Holtslag, A.A.M., 1998. A remote sensing surface energy balance algorithm for land (SEBAL): 1. Formulation. Journal of hydrology, 212, 198-212.
- Duffie, J. A., & Beckman, W. A. (2013). Solar Engineering of Thermal Processes (4th ed.). Wiley.

## License

See [LICENSE](LICENSE) for details.
