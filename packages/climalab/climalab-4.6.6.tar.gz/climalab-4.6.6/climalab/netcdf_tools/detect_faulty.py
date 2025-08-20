#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Program Note**

- This program uses the `scan_ncfiles` function from the `file_utils` module
  within the `xarray_utils` sub-package to detect faulty NetCDF files.
- It scans specified directories for NetCDF (`.nc`) files, automatically
  checks the integrity of all found files, and generates a comprehensive
  report listing any faulty files organised by directory.
- The function automatically handles file discovery, integrity testing,
  and report generation without requiring additional configuration.

**Redistribution Notice**
- You may redistribute this program to any other directory as needed.
- The program operates on the directory paths specified in the `PATH_OBJ`
  variable, so ensure that any paths provided are properly configured to
  reflect your system's directory structure.

**Main Functions and Sub-packages Used**
- `scan_ncfiles` (from `file_utils`, part of the `xarray_utils` sub-package):
   Automatically scans directories for `.nc` files, checks their integrity
   using xarray, and generates a detailed report of faulty files.
- `program_exec_timer` (from `time_handling` sub-package):
   Measures and reports the total execution time of the scanning process
   for performance analysis.

**Output**
- Creates a text report file (`faulty_netcdf_file_report.txt`) in the
  current working directory with statistics and details of any faulty
  NetCDF files found during the scan.
"""

#------------------------#
# Import project modules #
#------------------------#

from filewise.xarray_utils.file_utils import scan_ncfiles
from pygenutils.time_handling.program_snippet_exec_timers import program_exec_timer

#-------------------#
# Define parameters #
#-------------------#

# Paths to be scanned #
PATH_OBJ = "/media/jonander/My_Basic/Dokumentuak"

# PATH_OBJ = [
#     "/media/jonander/My_Basic/Dokumentuak",
#     "/home/jonander/Documents/03-Ikasketak"
#     ]

#---------------------#
# Program progression #
#---------------------#

# Initialise stopwatch #
program_exec_timer('start')

# Run program #
scan_ncfiles(PATH_OBJ)

# Stop the stopwatch and calculate full program execution time #
program_exec_timer('stop')
