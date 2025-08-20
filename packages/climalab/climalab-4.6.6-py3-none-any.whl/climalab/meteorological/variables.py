#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.strings.text_formatters import format_string

#-------------------------#
# Define custom functions #
#-------------------------#

# Angle converter #
def angle_converter(angle: float | np.ndarray, conversion: str) -> float | np.ndarray:
    """
    Converts angles between radians and degrees.
    
    This function provides bidirectional conversion between radians and degrees
    using predefined conversion options.
    
    Parameters
    ----------
    angle : float | np.ndarray
        The angle value(s) to convert.
    conversion : str
        The conversion type. Must be one of:
        - "deg2rad": Convert degrees to radians
        - "rad2deg": Convert radians to degrees
    
    Returns
    -------
    float | np.ndarray
        The converted angle value(s) in the target unit.
        
    Raises
    ------
    ValueError
        If the conversion type is not supported.
        
    Examples
    --------
    >>> angle_converter(180, "deg2rad")
    3.141592653589793
    >>> angle_converter(3.14159, "rad2deg")
    179.99949796472183
    """
    conv_options = UNIT_CONVERSIONS_LIST[:2]
    if conversion not in conv_options:
        raise ValueError(format_string(UNSUPPORTED_UNIT_CONVERSION_ERROR, conv_options))
    else:
        converted_angle = UNIT_CONVERTER_DICT[conversion](angle)
        return converted_angle

def ws_unit_converter(wind_speed: float | np.ndarray, conversion: str) -> float | np.ndarray:
    """
    Converts wind speed between metres per second and kilometres per hour.
    
    This function provides bidirectional conversion between m/s and km/h
    for wind speed measurements.
    
    Parameters
    ----------
    wind_speed : float | np.ndarray
        The wind speed value(s) to convert.
    conversion : str
        The conversion type. Must be one of:
        - "mps_to_kph": Convert metres per second to kilometres per hour
        - "kph_to_mps": Convert kilometres per hour to metres per second
    
    Returns
    -------
    float | np.ndarray
        The converted wind speed value(s) in the target unit.
        
    Raises
    ------
    ValueError
        If the conversion type is not supported.
        
    Examples
    --------
    >>> ws_unit_converter(10, "mps_to_kph")
    36.0
    >>> ws_unit_converter(36, "kph_to_mps")
    10.0
    """
    conv_options = UNIT_CONVERSIONS_LIST[2:]
    if conversion not in conv_options:
        raise ValueError(format_string(UNSUPPORTED_UNIT_CONVERSION_ERROR, conv_options))
    else:
        converted_speed = UNIT_CONVERTER_DICT[conversion](wind_speed)
        return converted_speed


# Wind direction calculator based on meteorological criteria #
def meteorological_wind_direction(u: int | float | np.ndarray, v: int | float | np.ndarray) -> np.ndarray:
    
    """
    Calculates the wind direction, as the opposite to
    where the wind is blowing to. The 0 angle is located
    at the middle top of the goniometric cyrcle.
    This means that if the direction is, for example, 225º,
    then that is where wind is blowing, thus coming from
    an angle of 45º, so the wind is blowing from the north-east.
    
    Parameters
    ----------
    u : int | float | np.ndarray
        Array containing the modulus and sense of the
        zonal component of the wind.
    v : int | float | np.ndarray
        Array containing the modulus and sense of the
        meridional component of the wind.
    
    Returns
    -------
    np.ndarray
        Array containing the directions of the wind, 
        described as in the first paragraph.
    """
    
    if (isinstance(u, int) or isinstance(v, int))\
        or (isinstance(u, float) or isinstance(v, float)):
        u = [u]
        v = [v]
            
    else:
        if u.dtype.str == 'O':
            u = u.astype('d')
        if v.dtype.str == 'O':
            v = v.astype('d')
    
    u_records = len(u)
    v_records = len(v)
    
    wind_dir_meteo_list = []
    
    if u_records == v_records:
        for t in range(u_records):  
            
            print(f"Calculating the wind direction for the time no. {t}...")
            
            if u[t] != 0 and v[t] != 0:
                wind_dir = angle_converter(np.arctan2(v[t],u[t]), "rad2deg")
                
                if u[t] > 0 and v[t] > 0:
                    wind_dir_meteo = 180 - (abs(wind_dir) - 90)
                    
                elif u[t] < 0 and v[t] > 0:
                    wind_dir_meteo = 180 - (wind_dir - 90)
                    
                elif u[t] > 0 and v[t] < 0:
                    wind_dir_meteo = 360 + wind_dir
                    
                elif u[t] < 0 and v[t] < 0:
                    wind_dir_meteo = 180 + wind_dir
                    
            elif u[t] == 0 and v[t] != 0:
                    
                if v[t] > 0:
                    wind_dir_meteo = 0
                elif v[t] < 0:
                    wind_dir_meteo = 180
                    
            elif u[t] != 0 and v[t] == 0:
    
                if u[t] > 0:
                    wind_dir_meteo = 270
                elif u[t] < 0:
                    wind_dir_meteo = 90     
                        
            wind_dir_meteo_list.append(wind_dir_meteo)   

    wind_dir_meteo_array = np.array(wind_dir_meteo_list).astype('d')
    
    return wind_dir_meteo_array


# Dewpoint temperature #
def dewpoint_temperature(T: np.ndarray | list[float] | float, rh: np.ndarray | list[float] | float) -> np.ndarray:
    """
    Calculates dewpoint temperature using Magnus' formula.
    
    Computes the dewpoint temperature from air temperature and relative humidity
    using the Magnus formula. The function handles both positive and negative
    temperatures with different constants for improved accuracy.
    
    References
    ----------
    Adapted from: https://content.meteoblue.com/es/especificaciones/variables-meteorologicas/humedad
    Uses Magnus' formula for dewpoint calculation.
    
    Parameters
    ----------
    T : np.ndarray | list[float] | float
        Air temperature values in degrees Celsius. Can be a single value,
        list, or numpy array.
    rh : np.ndarray | list[float] | float
        Relative humidity values as percentages (0-100). Must have the same
        shape as T.
    
    Returns
    -------
    np.ndarray
        Dewpoint temperature values in degrees Celsius, with the same shape as
        the input arrays.
        
    Raises
    ------
    ValueError
        If T and rh arrays do not have the same shape.
        
    Examples
    --------
    >>> import numpy as np
    >>> T = np.array([20, 25, 30])
    >>> rh = np.array([60, 70, 80])
    >>> dewpoint_temperature(T, rh)
    array([12.04, 19.11, 26.17])
    
    Notes
    -----
    The function uses different Magnus formula constants for positive and
    negative temperatures to improve accuracy across the full temperature range.
    """
    
    if not isinstance(T, list):
        T = np.array(T)
         
    if not isinstance(rh, list):
        rh = np.array(rh)

    if T.shape != rh.shape:
        raise ValueError("Temperature and relative humidity arrays"
                         "must have the same shape.")
        
    c2p, c2n, c3p, c3n = return_constants()

    Td = T.copy()
    
    T_pos_mask = T>0
    T_neg_mask = T<0
    
    T_pos_masked = T[T_pos_mask]
    T_neg_masked = T[T_neg_mask]
    
    rh_pos_masked = rh[T_pos_mask]
    rh_neg_masked = rh[T_neg_mask]
    
    Td[T_pos_mask]\
    = (np.log(rh_pos_masked/100) + (c2p*T_pos_masked) / (c3p+T_pos_masked))\
      / (c2p - np.log(rh_pos_masked/100) - (c2p*T_pos_masked) / (c3p+T_pos_masked))\
      * c3p
        
    Td[T_neg_mask]\
    = (np.log(rh_neg_masked/100) + (c2n*T_neg_masked) / (c3n+T_neg_masked))\
      / (c2n - np.log(rh_neg_masked/100) - (c2n*T_neg_masked) / (c3n+T_neg_masked))\
      * c3n

    return Td


# Relative humidity #
def relative_humidity(T: np.ndarray | list[float] | float, Td: np.ndarray | list[float] | float) -> np.ndarray:
    """
    Calculates relative humidity from temperature and dewpoint temperature using Magnus' formula.
    
    Computes the relative humidity from air temperature and dewpoint temperature
    using the Magnus formula. The function handles both positive and negative
    temperatures with different constants for improved accuracy.
    
    References
    ----------
    Adapted from: https://content.meteoblue.com/es/especificaciones/variables-meteorologicas/humedad
    Uses Magnus' formula for relative humidity calculation.
    
    Parameters
    ----------
    T : np.ndarray | list[float] | float
        Air temperature values in degrees Celsius. Can be a single value,
        list, or numpy array.
    Td : np.ndarray | list[float] | float
        Dewpoint temperature values in degrees Celsius. Must have the same
        shape as T.
    
    Returns
    -------
    np.ndarray
        Relative humidity values as percentages (0-100), with the same shape as
        the input arrays.
        
    Raises
    ------
    ValueError
        If T and Td arrays do not have the same shape.
        
    Examples
    --------
    >>> import numpy as np
    >>> T = np.array([20, 25, 30])
    >>> Td = np.array([12, 19, 26])
    >>> relative_humidity(T, Td)
    array([59.8, 70.2, 80.1])
    
    Notes
    -----
    The function uses different Magnus formula constants for positive and
    negative temperatures to improve accuracy across the full temperature range.
    The result is expressed as a percentage (0-100) rather than a fraction (0-1).
    """
    
    if not isinstance(T, list):
        T = np.array(T)
         
    if not isinstance(Td, list):
        Td = np.array(Td)
    
    if T.shape != Td.shape:
        raise ValueError("Temperature and dewpoint temperature arrays"
                         "must have the same shape.")

    rh = T.copy()
    
    c2p, c2n, c3p, c3n = return_constants()
    
    T_pos_mask = T>0
    T_neg_mask = T<0
    
    T_pos_masked = T[T_pos_mask]
    T_neg_masked = T[T_neg_mask]
    
    Td_pos_masked = Td[T_pos_mask]
    Td_neg_masked = Td[T_neg_mask]
    
    rh[T_pos_mask] = 100*np.exp(c2p * (T_pos_masked*(c3p - Td_pos_masked)\
                                       +  Td_pos_masked*(c3p+T_pos_masked))\
                                / ((c3p + T_pos_masked)*(c3p + Td_pos_masked)))
        
    rh[T_neg_mask] = 100*np.exp(c2n * (T_neg_masked*(c3n - Td_neg_masked)\
                                       +  Td_neg_masked*(c3n+T_neg_masked))\
                                / ((c3n + T_neg_masked)*(c3n + Td_neg_masked)))

    return rh

# Constant mini data base #
def return_constants() -> tuple[float, float, float, float]:
    """
    Returns Magnus formula constants for dewpoint and relative humidity calculations.
    
    Provides the constants used in Magnus' formula for calculating dewpoint temperature
    and relative humidity. Different constants are used for positive and negative
    temperatures to improve accuracy across the full temperature range.
    
    References
    ----------
    Adapted from: https://content.meteoblue.com/es/especificaciones/variables-meteorologicas/humedad
    
    Returns
    -------
    tuple[float, float, float, float]
        A tuple containing four constants in the following order:
        - c2p (float): Magnus constant for T > 0°C (17.08085)
        - c2n (float): Magnus constant for T < 0°C (17.84362)  
        - c3p (float): Magnus constant for T > 0°C (234.175)
        - c3n (float): Magnus constant for T < 0°C (245.425)
        
    Examples
    --------
    >>> c2p, c2n, c3p, c3n = return_constants()
    >>> print(f"Positive temp constants: c2p={c2p}, c3p={c3p}")
    Positive temp constants: c2p=17.08085, c3p=234.175
    >>> print(f"Negative temp constants: c2n={c2n}, c3n={c3n}")
    Negative temp constants: c2n=17.84362, c3n=245.425
    
    Notes
    -----
    These constants are specifically tuned for meteorological applications and
    provide improved accuracy when working with atmospheric temperature and
    humidity calculations across the typical range of Earth's surface conditions.
    """
    
    # Constants for T > 0:
    c2p = 17.08085
    c3p = 234.175 
 
    # Constants for T < 0:
    c2n = 17.84362
    c3n = 245.425  
    
    return c2p, c2n, c3p, c3n

#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported options #
#-------------------#

# Magnitude unit conversions #
UNIT_CONVERSIONS_LIST = ["deg2rad", "rad2deg", "mps_to_kph", "kph_to_mps"]

# Template strings #
#------------------#

# Error messages #
UNSUPPORTED_UNIT_CONVERSION_ERROR = "Unsupported unit converter. Choose one from {}."

# Switch case dictionaries #
#--------------------------#

# Magnitude unit conversions #
UNIT_CONVERTER_DICT = {
    UNIT_CONVERSIONS_LIST[0]: lambda angle: np.deg2rad(angle),
    UNIT_CONVERSIONS_LIST[1]: lambda angle: np.rad2deg(angle),
    UNIT_CONVERSIONS_LIST[2]: lambda wind_speed: wind_speed * 3.6,
    UNIT_CONVERSIONS_LIST[3]: lambda wind_speed: wind_speed / 3.6
}
