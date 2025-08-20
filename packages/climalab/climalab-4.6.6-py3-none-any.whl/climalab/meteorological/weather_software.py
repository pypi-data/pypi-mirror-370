#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.arrays_and_lists.patterns import approach_value
from pygenutils.time_handling.calendar_utils import week_range

#-------------------------#
# Define custom functions #
#-------------------------#

def temperature_typical_extreme_period(hdy_df_t2m: pd.DataFrame) -> str:
    """
    Calculates typical and extreme temperature periods for EnergyPlus weather files.
    
    Function that calculates the typical and extreme periods concerning the 
    2 metre temperature, required for EnergyPlus software as the third part 
    of the header. The function identifies representative weeks for seasonal
    extremes and typical conditions based on temperature statistics.
    
    Parameters
    ----------
    hdy_df_t2m : pd.DataFrame
        DataFrame containing hourly temperature data with the following required columns:
        - 'date': datetime column with date and time information
        - 't2m': 2-metre temperature values in appropriate units
        The DataFrame should contain at least one full year of data for accurate
        seasonal analysis.
    
    Returns
    -------
    str
        Formatted header string for EnergyPlus weather file containing:
        - Summer week with maximum temperature (extreme)
        - Summer week with average temperature (typical)  
        - Winter week with minimum temperature (extreme)
        - Winter week with average temperature (typical)
        - Autumn week with average temperature (typical)
        - Spring week with average temperature (typical)
        
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> dates = pd.date_range('2020-01-01', '2020-12-31', freq='H')
    >>> temps = 15 + 10 * np.sin(2 * np.pi * np.arange(len(dates)) / (365.25 * 24))
    >>> df = pd.DataFrame({'date': dates, 't2m': temps})
    >>> header = temperature_typical_extreme_period(df)
    >>> print(type(header))
    <class 'str'>
    
    Notes
    -----
    The function defines seasons as:
    - Winter: December, January, February
    - Spring: March, April, May  
    - Summer: June, July, August
    - Autumn: September, October, November
    
    Week ranges are calculated using the approach_value function to find dates
    closest to statistical measures (min, max, average) for each season.
    Only temperature is required for the analysis, but a proper date column
    is essential for seasonal splitting and week range calculations.
    """
    
    # HDY winter #
    #------------#
    
    hdy_df_t2m_dec = hdy_df_t2m[(hdy_df_t2m.date.dt.month == 12)]
    hdy_df_t2m_jan_feb = hdy_df_t2m[(hdy_df_t2m.date.dt.month >= 1) & 
                                    (hdy_df_t2m.date.dt.month <= 2)]
    hdy_df_t2m_winter = pd.concat([hdy_df_t2m_dec,hdy_df_t2m_jan_feb], axis = 0).reset_index()
    
    # Mininum temperature #
    HDY_winter_min = np.min(hdy_df_t2m_winter.t2m)
    iaprox_winter_min = np.where(hdy_df_t2m_winter == HDY_winter_min)[0][0]
    
    winter_date_min = hdy_df_t2m_winter.date.loc[iaprox_winter_min]
    winter_week_range_min = week_range(winter_date_min)
    
    winter_start_month_week_range_min = winter_week_range_min[0].month
    winter_end_month_week_range_min = winter_week_range_min[1].month
    
    winter_start_day_week_range_min = winter_week_range_min[0].day
    winter_end_day_week_range_min = winter_week_range_min[1].day
    
    winter_week_range_min_epw\
    = f"{winter_start_month_week_range_min:d}/"\
      f"{winter_start_day_week_range_min:2d},"\
      f"{winter_end_month_week_range_min:d}/"\
      f"{winter_end_day_week_range_min:2d}"
    
    # Average temperature #
    HDY_winter_avg = np.mean(hdy_df_t2m_winter.t2m)
    iaprox_winter_avg = approach_value(hdy_df_t2m_winter.t2m, HDY_winter_avg)[1]
    
    winter_date_aprox_avg = hdy_df_t2m_winter.date.loc[iaprox_winter_avg]
    winter_week_range_avg = week_range(winter_date_aprox_avg)
    
    winter_start_month_week_range_avg = winter_week_range_avg[0].month
    winter_end_month_week_range_avg = winter_week_range_avg[1].month
    
    winter_start_day_week_range_avg = winter_week_range_avg[0].day
    winter_end_day_week_range_avg = winter_week_range_avg[1].day
    
    winter_week_range_avg_epw\
    = f"{winter_start_month_week_range_avg:d}/"\
      f"{winter_start_day_week_range_avg:2d},"\
      f"{winter_end_month_week_range_avg:d}/"\
      f"{winter_end_day_week_range_avg:2d}"
    
    # HDY spring #
    #------------#
    
    hdy_df_t2m_spring = hdy_df_t2m[(hdy_df_t2m.date.dt.month >= 3)
                             & (hdy_df_t2m.date.dt.month <= 5)].reset_index() 
    
    # Average temperature only #
    HDY_spring_avg = np.mean(hdy_df_t2m_spring.t2m)
    iaprox_spring_avg = approach_value(hdy_df_t2m_spring.t2m, HDY_spring_avg)[1]
    
    spring_date_aprox_avg = hdy_df_t2m_spring.date.loc[iaprox_spring_avg]
    spring_week_range_avg = week_range(spring_date_aprox_avg)
    
    spring_start_month_week_range_avg = spring_week_range_avg[0].month
    spring_end_month_week_range_avg = spring_week_range_avg[1].month
    
    spring_start_day_week_range_avg = spring_week_range_avg[0].day
    spring_end_day_week_range_avg = spring_week_range_avg[1].day
    
    spring_week_range_avg_epw\
    = f"{spring_start_month_week_range_avg:d}/"\
      f"{spring_start_day_week_range_avg:2d},"\
      f"{spring_end_month_week_range_avg:d}/"\
      f"{spring_end_day_week_range_avg:2d}"
    
    # HDY summer #
    #------------#
    
    hdy_df_t2m_summer = hdy_df_t2m[(hdy_df_t2m.date.dt.month >= 6)
                             &(hdy_df_t2m.date.dt.month <= 8)].reset_index() 
    
    # Maximum temperature #
    HDY_summer_max = np.max(hdy_df_t2m_summer.t2m)
    iaprox_summer_max = np.where(hdy_df_t2m_summer == HDY_summer_max)[0][0]
    
    summer_date_max = hdy_df_t2m_summer.date.loc[iaprox_summer_max]
    summer_week_range_max = week_range(summer_date_max)
    
    summer_start_month_week_range_max = summer_week_range_max[0].month
    summer_end_month_week_range_max = summer_week_range_max[1].month
    
    summer_start_day_week_range_max = summer_week_range_max[0].day
    summer_end_day_week_range_max = summer_week_range_max[1].day
    
    summer_week_range_max_epw\
    = f"{summer_start_month_week_range_max:d}/"\
      f"{summer_start_day_week_range_max:2d},"\
      f"{summer_end_month_week_range_max:d}/"\
      f"{summer_end_day_week_range_max:2d}"
    
    # Average temperature #
    HDY_summer_avg = np.mean(hdy_df_t2m_summer.t2m)
    iaprox_summer_avg = approach_value(hdy_df_t2m_summer.t2m, HDY_summer_avg)[1]
    
    summer_date_aprox_avg = hdy_df_t2m_summer.date.loc[iaprox_summer_avg]
    summer_week_range_avg = week_range(summer_date_aprox_avg)
    
    summer_start_month_week_range_avg = summer_week_range_avg[0].month
    summer_end_month_week_range_avg = summer_week_range_avg[1].month
    
    summer_start_day_week_range_avg = summer_week_range_avg[0].day
    summer_end_day_week_range_avg = summer_week_range_avg[1].day
    
    summer_week_range_avg_epw\
    = f"{summer_start_month_week_range_avg:d}/"\
      f"{summer_start_day_week_range_avg:2d},"\
      f"{summer_end_month_week_range_avg:d}/"\
      f"{summer_end_day_week_range_avg:2d}"
    
    # HDY fall #
    #----------#
    
    hdy_df_t2m_fall = hdy_df_t2m[(hdy_df_t2m.date.dt.month >= 9)
                           &(hdy_df_t2m.date.dt.month <= 11)].reset_index() 
      
    # Average temperature only #
    HDY_fall_avg = np.mean(hdy_df_t2m_fall.t2m)
    iaprox_fall_avg = approach_value(hdy_df_t2m_fall.t2m, HDY_fall_avg)[1]
    
    fall_date_aprox_avg = hdy_df_t2m_fall.date.loc[iaprox_fall_avg]
    fall_week_range_avg = week_range(fall_date_aprox_avg)
    
    fall_start_month_week_range_avg = fall_week_range_avg[0].month
    fall_end_month_week_range_avg = fall_week_range_avg[1].month
    
    fall_start_day_week_range_avg = fall_week_range_avg[0].day
    fall_end_day_week_range_avg = fall_week_range_avg[1].day
    
    fall_week_range_avg_epw\
    = f"{fall_start_month_week_range_avg:d}/"\
      f"{fall_start_day_week_range_avg:2d},"\
      f"{fall_end_month_week_range_avg:d}/"\
      f"{fall_end_day_week_range_avg:2d}"
    
    # Define the third header #
    #-------------------------#
    
    header_3 = "TYPICAL/EXTREME PERIODS,6,Summer - Week Nearest Max Temperature For Period,Extreme,"\
               f"{summer_week_range_max_epw},Summer - Week Nearest Average Temperature For Period,Typical,"\
               f"{summer_week_range_avg_epw},Winter - Week Nearest Min Temperature For Period,Extreme,"\
               f"{winter_week_range_min_epw},Winter - Week Nearest Average Temperature For Period,Typical,"\
               f"{winter_week_range_avg_epw},Autumn - Week Nearest Average Temperature For Period,Typical,"\
               f"{fall_week_range_avg_epw},Spring - Week Nearest Average Temperature For Period,Typical,"\
               f"{spring_week_range_avg_epw}"
               
    return header_3
    

def epw_creator(HDY_df_epw: pd.DataFrame,
                header_list: list[str],
                file_name_noext: str) -> None:
    """
    Creates an EnergyPlus Weather (EPW) file from hourly weather data and headers.
    
    This function generates a complete EPW file by combining header information
    with hourly weather data. It writes the headers first, followed by the
    formatted weather data in comma-separated format suitable for EnergyPlus
    building energy simulation software.
    
    Parameters
    ----------
    HDY_df_epw : pd.DataFrame
        DataFrame containing hourly weather data for a full year (8760 hours).
        Each row represents one hour of weather data with multiple meteorological
        variables as columns (temperature, humidity, wind, solar radiation, etc.).
    header_list : list[str]
        List of header strings to be written at the beginning of the EPW file.
        Typically contains 8 header lines including location information,
        design conditions, typical/extreme periods, ground temperatures,
        holidays/daylight saving, comments, and data periods.
    file_name_noext : str
        Base filename without extension for the output EPW file. The function
        will automatically append '.epw' extension.
    
    Returns
    -------
    None
        The function writes directly to disk and does not return any value.
        Creates a file named '{file_name_noext}.epw' in the current directory.
        
    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> 
    >>> # Create sample hourly data (8760 hours)
    >>> hours = 8760
    >>> data = np.random.randn(hours, 10)  # 10 weather variables
    >>> df = pd.DataFrame(data, columns=[f'var_{i}' for i in range(10)])
    >>> 
    >>> # Create sample headers
    >>> headers = [
    ...     "LOCATION,City,State,Country,Source,WMO,Lat,Lon,TZ,Elev",
    ...     "DESIGN CONDITIONS,0",
    ...     # ... other headers
    ... ]
    >>> 
    >>> # Create EPW file
    >>> epw_creator(df, headers, "my_weather_file")
    >>> # Creates 'my_weather_file.epw' in current directory
    
    Notes
    -----
    The EPW format is a standardised weather file format used by EnergyPlus
    and other building energy simulation programs. The file structure consists of:
    
    1. 8 header lines containing metadata
    2. 8760 lines of hourly weather data (one full year)
    
    Each data line contains comma-separated values representing various
    meteorological parameters. The function handles the formatting automatically
    and ensures proper line endings and structure.
    
    The function opens the file in write mode, so any existing file with the
    same name will be overwritten.
    """
        
    # Open the writable file #
    epw_file_name = f"{file_name_noext}.epw"
    epw_file_obj = open(epw_file_name, "w")
    
    # Write the hearders down #
    for header in header_list:
        epw_file_obj.write(f"{header} \n")
    
    # Append HDY values to the headers # 
    HDY_df_epw_vals = HDY_df_epw.values
    HDY_ncols = HDY_df_epw_vals.shape[1]
    
    lhdy = len(HDY_df_epw)
       
    for t in range(lhdy):
        for ivar in range(HDY_ncols):
            epw_file_obj.write(f"{HDY_df_epw_vals[t,ivar]},")
            
            if ivar == HDY_ncols-1:
                epw_file_obj.write(f"{HDY_df_epw_vals[t,ivar]}\n" )
    
    # Close the file #
    epw_file_obj.close()
