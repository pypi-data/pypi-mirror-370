#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Program Note**

- This program is an application of the functions from the `data_manipulation` module
  within the `xarray_utils` sub-package.
- It extracts geographical bounds (latitude and longitude), time bounds, 
  and time formats from netCDF (`.nc`) files found in the directory where 
  the program is executed.
- The functions scan directories recursively and are designed to search for
  netCDF files without needing to specify a path argument.

**Redistribution Notice**  
- You may redistribute this program and place it in any directory of your choice.
- However, please note that the program will operate based on the directory where
  it is executed (using the current working directory) and will recursively search 
  for `.nc` files within that directory.

**Main Functions and sub-packages Used**
- `extract_latlon_bounds` (from `data_manipulation`, part of the `xarray_utils` sub-package):
   Extracts latitude and longitude bounds from netCDF files with specified rounding 
   precision for coordinate deltas and values. Generates a 'latlon_bounds.txt' report
   containing coordinate arrays, dimensions, and deltas for each file.
- `extract_time_bounds` (from `data_manipulation`, part of the `xarray_utils` sub-package):
   Extracts the start and end times from netCDF files and generates a 'period_bounds.txt'
   report containing the time range and total number of time records.
- `extract_time_formats` (from `data_manipulation`, part of the `xarray_utils` sub-package):
   Extracts the time formats from netCDF files and documents them in a 'time_formats.txt' 
   report showing time arrays and their lengths.

**File Integrity and Error Handling**
- All functions automatically perform integrity checking on netCDF files before processing.
- Faulty or corrupted files are identified and their error information is recorded in 
  the respective output reports rather than causing program termination.

**Execution Timing**
- Execution timing is handled using the `program_exec_timer` function from the
  `time_handling` sub-package, which measures and returns the total program execution time.
  The timer is initialised at the start and returns a formatted elapsed time string when stopped.
"""

#------------------------#
# Import project modules #
#------------------------#

from filewise.xarray_utils.data_manipulation import (
    extract_latlon_bounds,
    extract_time_bounds,
    extract_time_formats
)
from pygenutils.time_handling.program_snippet_exec_timers import program_exec_timer

#------------#
# Parameters #
#------------#

# Delta and value roundoffs for coordinate values #
DELTA_ROUNDOFF = 3
VALUE_ROUNDOFF = 5

#---------------------#
# Program progression #
#---------------------#

# Initialise stopwatch #
program_exec_timer("start")

# Extract every netCDF file's basic information present in this project #
extract_latlon_bounds(DELTA_ROUNDOFF, VALUE_ROUNDOFF)
extract_time_bounds()
extract_time_formats()

# Stop the stopwatch and calculate full program execution time #
program_exec_timer("stop")
