#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------#
# Import project modules #
#------------------------#

from filewise.file_operations.ops_handler import rename_objects
from filewise.xarray_utils.patterns import get_file_variables, get_times
from paramlib.global_parameters import (
    BASIC_ARITHMETIC_OPERATORS, 
    COMMON_DELIMITER_LIST, 
    TIME_FREQUENCIES_BRIEF,
    TIME_FREQUENCIES_ABBREVIATED
)
from pygenutils.arrays_and_lists.data_manipulation import flatten_to_string, flatten_list
from pygenutils.operative_systems.os_operations import exit_info, run_system_command
from pygenutils.strings.text_formatters import format_string
from pygenutils.strings.string_handler import (
    add_to_path, 
    find_substring_index, 
    obj_path_specs, 
    modify_obj_specs
)
from pygenutils.time_handling.date_and_time_utils import find_dt_key

#-------------------------#
# Define custom functions #
#-------------------------#

# Internal Helper Functions #
#---------------------------#

def _get_varname_in_filename(
        file: str, 
        return_std: bool = False, 
        varlist_orig: list[str] | None = None, 
        varlist_std: list[str] | None = None) -> str:
    """
    Extract the variable name from a file name or return its standardised name.
    
    This function parses the filename to extract the variable name from the first
    part (before the first delimiter) and optionally converts it to a standardised
    name using provided mapping lists.

    Parameters
    ----------
    file : str
        The file path or file name to extract the variable name from.
    return_std : bool, optional
        If True, returns the standardised variable name using the mapping lists.
        Default is False.
    varlist_orig : list[str] | None, optional
        List of original variable names for standardisation mapping. Required if
        `return_std` is True. Default is None.
    varlist_std : list[str] | None, optional
        List of standardised variable names corresponding to `varlist_orig`.
        Required if `return_std` is True. Default is None.

    Returns
    -------
    str
        The variable name extracted from the file name, or its standardised
        counterpart if `return_std` is True.

    Raises
    ------
    ValueError
        If the variable is not found in the original variable list when
        `return_std` is True, or if required parameters are missing.
        
    Examples
    --------
    >>> _get_varname_in_filename('temperature_daily_model_exp.nc')
    'temperature'
    
    >>> _get_varname_in_filename('temp_daily_model_exp.nc', return_std=True,
    ...                         varlist_orig=['temp'], varlist_std=['temperature'])
    'temperature'
    """
    file_name_parts = obj_path_specs(file, file_spec_key="name_noext_parts", SPLIT_DELIM=SPLIT_DELIM1)
    var_file = file_name_parts[0]

    if return_std:
        if varlist_orig is None or varlist_std is None:
            raise ValueError("Both varlist_orig and varlist_std must be provided when return_std=True")
            
        var_pos = find_substring_index(varlist_orig, var_file)
        if var_pos != -1:
            return varlist_std[var_pos]
        else:
            raise ValueError(f"Variable '{var_file}' in '{file}' not found in original list {varlist_orig}.")
    return var_file


def _standardise_filename(
        variable: str, 
        freq: str, 
        model: str, 
        experiment: str, 
        calc_proc: str, 
        period: str, 
        region: str, 
        ext: str) -> str:
    """
    Create a standardised filename based on climate data components.
    
    This function generates a consistent filename following the pattern:
    {variable}_{freq}_{model}_{experiment}_{calc_proc}_{region}_{period}.{ext}

    Parameters
    ----------
    variable : str
        Variable name (e.g., 'temperature', 'precipitation').
    freq : str
        Frequency of the data (e.g., 'daily', 'monthly', 'yearly').
    model : str
        Climate model name (e.g., 'HadGEM3', 'ECMWF').
    experiment : str
        Experiment name or type (e.g., 'historical', 'rcp85').
    calc_proc : str
        Calculation procedure applied (e.g., 'mean', 'sum', 'anomaly').
    period : str
        Time period string (e.g., '2000-2020', '1981-2010').
    region : str
        Region or geographic area (e.g., 'europe', 'global').
    ext : str
        File extension without dot (e.g., 'nc', 'grib').

    Returns
    -------
    str
        Standardised filename following the consistent naming convention.
        
    Examples
    --------
    >>> _standardise_filename('temperature', 'daily', 'HadGEM3', 'historical',
    ...                      'mean', '2000-2020', 'europe', 'nc')
    'temperature_daily_HadGEM3_historical_mean_europe_2000-2020.nc'
    """
    return f"{variable}_{freq}_{model}_{experiment}_{calc_proc}_{region}_{period}.{ext}"


# Main functions #
#----------------#

# Core Data Processing Functions #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def cdo_mergetime(
        file_list: str | list[str], 
        variable: str, 
        freq: str, 
        model: str, 
        experiment: str, 
        calc_proc: str, 
        period: str, 
        region: str, 
        ext: str,
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Merge time steps of multiple files into one using CDO's mergetime operator.
    
    This function combines multiple NetCDF files with different time steps into
    a single file, filtering files by the specified period and using CDO's
    mergetime operator for the actual merging process.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to merge.
    variable : str
        Variable name for the output file naming.
    freq : str
        Frequency of the data (e.g., 'daily', 'monthly').
    model : str
        Model name for the output file naming.
    experiment : str
        Experiment name or type for the output file naming.
    calc_proc : str
        Calculation procedure for the output file naming.
    period : str
        Time period string (e.g., '2000-2020') for filtering and naming.
    region : str
        Region or geographic area for the output file naming.
    ext : str
        File extension for the output file (e.g., 'nc').
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function creates a merged NetCDF file as output.
        
    Notes
    -----
    This function filters input files by the specified period, extracting
    the year from the filename and only including files within the period range.
    
    Examples
    --------
    >>> # Merge daily temperature files for 2000-2010
    >>> cdo_mergetime(['temp_2000.nc', 'temp_2005.nc', 'temp_2010.nc'],
    ...               'temperature', 'daily', 'HadGEM3', 'historical',
    ...               'mean', '2000-2010', 'europe', 'nc')
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = flatten_list(file_list)
    
    output_name = _standardise_filename(variable, freq, model, experiment, calc_proc, period, region, ext)
    start_year, end_year = period.split(SPLIT_DELIM2)
    file_list_selyear = [f for f in file_list if (year := obj_path_specs(f, "name_noext_parts", SPLIT_DELIM1)[-1]) >= start_year and year <= end_year]

    allfiles_string = flatten_to_string(file_list_selyear)
    cmd = f"cdo -b F64 -f nc4 mergetime '{allfiles_string}' {output_name}"

    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )
    
    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )


def cdo_selyear(
        file_list: str | list[str], 
        selyear_str: str, 
        freq: str, 
        model: str, 
        experiment: str, 
        calc_proc: str, 
        region: str, 
        ext: str, 
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Select data for specific years from files using CDO's selyear operator.
    
    This function applies CDO's selyear operator to extract data for specific
    years from NetCDF files, creating new files with the filtered data.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to select years from.
    selyear_str : str
        Start and end years separated by '/' (e.g., '2000/2010').
    freq : str
        Frequency of the data (e.g., 'daily', 'monthly').
    model : str
        Model name for the output file naming.
    experiment : str
        Experiment name or type for the output file naming.
    calc_proc : str
        Calculation procedure for the output file naming.
    region : str
        Region or geographic area for the output file naming.
    ext : str
        File extension for the output files (e.g., 'nc').
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function creates new NetCDF files with selected years as output.
        
    Examples
    --------
    >>> # Select years 2000-2010 from temperature files
    >>> cdo_selyear(['temp_full.nc'], '2000/2010', 'daily', 'HadGEM3',
    ...             'historical', 'mean', 'europe', 'nc')
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    selyear_split = obj_path_specs(selyear_str, file_spec_key="name_noext_parts", SPLIT_DELIM=SPLIT_DELIM2)
    start_year = f"{selyear_split[0]}"
    end_year = f"{selyear_split[-1]}"
    
    selyear_cdo = f"{start_year}/{end_year}"
    period = f"{start_year}-{end_year}"
    
    for file in file_list:
        var = _get_varname_in_filename(file)
        output_name = _standardise_filename(var, freq, model, experiment, calc_proc, period, region, ext)
        cmd = f"cdo selyear,{selyear_cdo} '{file}' {output_name}"

        # Run the command and capture the output
        process_exit_info = run_system_command(
            cmd, 
            capture_output=capture_output,
            return_output_name=return_output_name,
            encoding=encoding,
            shell=shell
        )

        # Call exit_info with parameters based on capture_output
        exit_info(process_exit_info,
            check_stdout=capture_output,
            check_stderr=capture_output,
            check_return_code=True
        )


def cdo_sellonlatbox(
        file_list: str | list[str], 
        coords: str, 
        freq: str, 
        model: str, 
        experiment: str, 
        calc_proc: str, 
        region: str, 
        ext: str, 
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Apply CDO's sellonlatbox operator to select a geographical box from input files.
    
    This function extracts a specific geographical region from NetCDF files using
    longitude-latitude box coordinates. It processes multiple files and creates
    new files containing only the selected geographic area.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to process.
    coords : str
        Coordinates for the longitude-latitude box in the format
        'lonwest,loneast,latsouth,latnorth' (e.g., '-10,40,30,70').
    freq : str
        Frequency of the data (e.g., 'daily', 'monthly').
    model : str
        Model name for the output file naming.
    experiment : str
        Experiment name or type for the output file naming.
    calc_proc : str
        Calculation procedure for the output file naming.
    region : str
        Region or geographic area for the output file naming.
    ext : str
        File extension for the output files (e.g., 'nc').
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function creates new NetCDF files with the selected geographic region.
        
    Examples
    --------
    >>> # Extract European region from global temperature files
    >>> cdo_sellonlatbox(['global_temp.nc'], '-10,40,35,70', 'daily',
    ...                  'HadGEM3', 'historical', 'mean', 'europe', 'nc')
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    for file in file_list:
        var = _get_varname_in_filename(file)
        time_var = find_dt_key(file)
        times = get_times(file, time_var)
        period = f"{times.dt.year.values[0]}-{times.dt.year.values[-1]}"
        output_name = _standardise_filename(var, freq, model, experiment, calc_proc, period, region, ext)
        cmd = f"cdo sellonlatbox,{coords} '{file}' {output_name}"

        # Run the command and capture the output
        process_exit_info = run_system_command(
            cmd, 
            capture_output=capture_output,
            return_output_name=return_output_name,
            encoding=encoding,
            shell=shell
        )

        # Call exit_info with parameters based on capture_output
        exit_info(process_exit_info,
            check_stdout=capture_output,
            check_stderr=capture_output,
            check_return_code=True
        )
        

def cdo_remap(
        file_list: str | list[str], 
        remap_str: str, 
        var: str, 
        freq: str, 
        model: str, 
        experiment: str, 
        calc_proc: str, 
        period: str, 
        region: str, 
        ext: str, 
        remap_proc: str = "bilinear",
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8", 
        shell: bool = True) -> None:
    """
    Apply remapping to files using CDO's remap procedures.
    
    This function remaps NetCDF files to a different grid using various 
    interpolation methods available in CDO. The remapping can be done using
    different procedures like bilinear, nearest neighbor, conservative, etc.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to remap.
    remap_str : str
        Target grid specification or grid description file path.
    var : str
        Variable name for the output file naming.
    freq : str
        Frequency of the data (e.g., 'daily', 'monthly').
    model : str
        Model name for the output file naming.
    experiment : str
        Experiment name or type for the output file naming.
    calc_proc : str
        Calculation procedure for the output file naming.
    period : str
        Time period string (e.g., '2000-2020') for the output file naming.
    region : str
        Region or geographic area for the output file naming.
    ext : str
        File extension for the output files (e.g., 'nc').
    remap_proc : str, optional
        Remapping procedure to use. Must be one of the supported CDO remap
        options. Default is 'bilinear'.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function creates remapped NetCDF files as output.
        
    Raises
    ------
    ValueError
        If `remap_proc` is not one of the supported CDO remap options.
        
    Examples
    --------
    >>> # Remap temperature data to a regular 1x1 degree grid
    >>> cdo_remap(['temp_irregular.nc'], 'r360x180', 'temperature', 
    ...           'daily', 'HadGEM3', 'historical', 'regridded', 
    ...           '2000-2010', 'global', 'nc')
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    output_name = _standardise_filename(var, freq, model, experiment, calc_proc, period, region, ext)
    
    if remap_proc not in CDO_REMAP_OPTIONS:
        raise ValueError(f"Unsupported remap procedure. Options are {CDO_REMAP_OPTIONS}")
    
    remap_cdo = CDO_REMAP_OPTION_DICT[remap_str]
    
    for file in file_list:
        cmd = f"cdo {remap_cdo},{remap_str} '{file}' {output_name}"

        # Run the command and capture the output
        process_exit_info = run_system_command(
            cmd, 
            capture_output=capture_output,
            return_output_name=return_output_name,
            encoding=encoding,
            shell=shell
        )
        
        # Call exit_info with parameters based on capture_output
        exit_info(process_exit_info,
            check_stdout=capture_output,
            check_stderr=capture_output,
            check_return_code=True
        )


# Statistical and Analytical Functions #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def cdo_time_mean(
        input_file, 
        var, 
        freq, 
        model, 
        experiment, 
        calc_proc, 
        period, 
        region, 
        ext,
        capture_output=False,
        return_output_name=False,
        encoding="utf-8", 
        shell=True
        ):
    """
    Calculates the time mean for a specific variable using CDO.

    Parameters
    ----------
    input_file : str
        Path to the netCDF file.
    var : str
        Variable name.
    freq : str
        Frequency of the data (e.g., daily, monthly).
    model : str
        Model name.
    experiment : str
        Experiment name or type.
    calc_proc : str
        Calculation procedure (e.g., 'mean', 'sum').
    period : str
        Time period string (e.g., '2000-2020').
    region : str
        Region or geographic area.
    ext : str
        File extension (e.g., 'nc').
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
    """
    output_name = _standardise_filename(var, freq, model, experiment, calc_proc, period, region, ext)
    cmd = f"cdo -{calc_proc} '{input_file}' {output_name}"

    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )

    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )
        

def cdo_periodic_statistics(
        nc_file, 
        statistic, 
        is_climatic, 
        freq, 
        season_str=None,
        capture_output=False,
        return_output_name=False,
        encoding="utf-8", shell=True
        ):
    """
    Calculates basic periodic statistics on a netCDF file using CDO.

    Parameters
    ----------
    nc_file : str
        Path to the netCDF file.
    statistic : str
        Statistic to calculate (e.g., 'mean', 'sum').
    is_climatic : bool
        Whether to calculate climatic statkit.
    freq : str
        Time frequency (e.g., 'monthly', 'yearly').
    season_str : str, optional
        Season to calculate if applicable, by default None.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
    """
    if statistic not in STATKIT:
        raise ValueError(f"Unsupported statistic {statistic}. Options are {STATKIT}")
    
    period_abbr = TIME_FREQUENCIES_BRIEF[find_substring_index(TIME_FREQUENCIES_ABBREVIATED, freq)]

    statname = f"y{period_abbr}{statistic}" if is_climatic else f"{period_abbr}{statistic}"
    
    if period_abbr == TIME_FREQUENCIES_BRIEF[3] and season_str:
        statname += f" -select,season={season_str}"

    file_name_noext = add_to_path(nc_file, return_file_name_noext=True)
    string2add = f"{SPLIT_DELIM1}{statname}" if not season_str else f"{SPLIT_DELIM1}{statname}_{statname[-3:]}"
    output_name = modify_obj_specs(nc_file, "name_noext", add_to_path(file_name_noext, string2add))

    cmd = f"cdo {statname} {nc_file} {output_name}"

    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )

    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )
    

def cdo_anomalies(
        input_file_full, 
        input_file_avg,
        var,
        freq,
        model, 
        experiment, 
        calc_proc,
        period,
        region,
        ext,
        capture_output=False,
        return_output_name=False,
        encoding="utf-8", shell=True
        ):
    """
    Calculates anomalies by subtracting the average from the full time series using CDO's sub operator.

    Parameters
    ----------
    input_file_full : str
        File path of the full time series data.
    input_file_avg : str
        File path of the average data (e.g., climatology).
    var : str
        Variable name.
    freq : str
        Frequency of the data (e.g., daily, monthly).
    model : str
        Model name.
    experiment : str
        Experiment name or type.
    calc_proc : str
        Calculation procedure
    period : str
        Time period string (e.g., '2000-2020').
    region : str
        Region or geographic area.
    ext : str
        File extension (e.g., 'nc').
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
    """
    output_name = _standardise_filename(var, freq, model, experiment, calc_proc, period, region, ext)
    cmd = f"cdo sub '{input_file_avg}' '{input_file_full}' {output_name}"

    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )

    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )


def calculate_periodic_deltas(
        proj_file, 
        hist_file, 
        operator="+", 
        delta_period="monthly", 
        model=None,
        capture_output=False,
        return_output_name=False,
        encoding="utf-8", shell=True
        ):
    """
    Calculates periodic deltas between projected and historical data using CDO.

    Parameters
    ----------
    proj_file : str
        Path to the projected netCDF file.
    hist_file : str
        Path to the historical netCDF file.
    operator : str, optional
        Operation to apply between files ('+', '-', '*', '/'). Default is '+'.
    delta_period : str, optional
        Period for delta calculation (e.g., 'monthly', 'yearly'). Default is 'monthly'.
    model : str, optional
        Model name, required if not inferred from the file name.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
    """
    period_idx = find_substring_index(TIME_FREQS_DELTA, delta_period)
    if period_idx == -1:
        raise ValueError(f"Unsupported delta period. Options are {TIME_FREQS_DELTA}")

    if model is None:
        raise ValueError("Model must be provided to calculate deltas.")
    
    period_abbr = TIME_FREQS_DELTA[period_idx]
    hist_mean_cmd = f"-y{period_abbr}mean {hist_file}"
    proj_mean_cmd = f"-y{period_abbr}mean {proj_file}"
    
    delta_filename = add_to_path(hist_file, return_file_name_noext=True)
    string2add = f"{period_abbr}Deltas_{model}.nc"
    delta_output = add_to_path(delta_filename, string2add)
    
    if operator not in BASIC_ARITHMETIC_OPERATORS:
        raise ValueError(f"Unsupported operator. Options are {BASIC_ARITHMETIC_OPERATORS}")
    
    operator_str = CDO_OPERATOR_STR_DICT[operator]
    cmd = f"cdo {operator_str} {hist_mean_cmd} {proj_mean_cmd} {delta_output}"

    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )

    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )


def apply_periodic_deltas(
        proj_file,
        hist_file, 
        operator="+",
        delta_period="monthly",
        model=None,
        capture_output=False,
        return_output_name=False,
        encoding="utf-8", shell=True
        ):
    """
    Applies periodic deltas between projected and historical data using CDO.

    Parameters
    ----------
    proj_file : str
        Path to the projected netCDF file.
    hist_file : str
        Path to the historical netCDF file.
    operator : str, optional
        Operation to apply between files ('+', '-', '*', '/'). Default is '+'.
    delta_period : str, optional
        Period for delta application (e.g., 'monthly', 'yearly'). Default is 'monthly'.
    model : str, optional
        Model name, required if not inferred from the file name.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
    """
    period_idx = find_substring_index(TIME_FREQS_DELTA, delta_period)
    if period_idx == -1:
        raise ValueError(f"Unsupported delta period. Options are {TIME_FREQS_DELTA}")

    if model is None:
        raise ValueError("Model must be provided to apply deltas.")
    
    period_abbr = TIME_FREQS_DELTA[period_idx]
    delta_output = add_to_path(hist_file, return_file_name_noext=True)
    string2add = f"{period_abbr}DeltaApplied_{model}.nc"
    delta_applied_output = add_to_path(delta_output, string2add)
    
    hist_mean_cmd = f"-y{period_abbr}mean {hist_file}"
    
    if operator not in BASIC_ARITHMETIC_OPERATORS:
        raise ValueError(f"Unsupported operator. Options are {BASIC_ARITHMETIC_OPERATORS}")
    
    operator_str = CDO_OPERATOR_STR_DICT[operator]
    cmd = f"cdo {operator_str} {proj_file} {hist_mean_cmd} {delta_applied_output}"

    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )

    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )


# File Renaming and Organisational Functions #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    
def cdo_rename(
        file_list: str | list[str], 
        varlist_orig: list[str], 
        varlist_std: list[str],
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8", 
        shell: bool = True) -> None:
    """
    Rename variables in files using a standardised variable list via CDO's chname operator.
    
    This function systematically renames variables within NetCDF files using CDO's
    chname operator. It maps original variable names to standardised names and
    creates new files with the updated variable names.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to process.
    varlist_orig : list[str]
        List of original variable names to be renamed.
    varlist_std : list[str]
        List of standardised variable names corresponding to `varlist_orig`.
        Must have the same length as `varlist_orig`.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function modifies the files in-place by renaming variables.
        
    Notes
    -----
    This function creates temporary files during processing and renames them
    back to the original filenames after successful variable renaming.
    
    Examples
    --------
    >>> # Rename temperature variables in multiple files
    >>> cdo_rename(['file1.nc', 'file2.nc'], ['temp', 'tmp'], 
    ...            ['temperature', 'temperature'])
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    for i, file in enumerate(file_list, start=1):
        var_file = get_file_variables(file)
        var_std = _get_varname_in_filename(file, True, varlist_orig, varlist_std)
        
        print(f"Renaming variable '{var_file}' to '{var_std}' in file {i}/{len(file_list)}...")
        
        temp_file = add_to_path(file)
        cmd = f"cdo chname,{var_file},{var_std} '{file}' '{temp_file}'"

        # Run the command and capture the output
        process_exit_info = run_system_command(
            cmd, 
            capture_output=capture_output,
            return_output_name=return_output_name,
            encoding=encoding,
            shell=shell
        )

        # Call exit_info with parameters based on capture_output
        exit_info(process_exit_info,
            check_stdout=capture_output,
            check_stderr=capture_output,
            check_return_code=True
        )
        
        # Rename the temporary file to the given file
        rename_objects(temp_file, file)
        
    
def change_filenames_by_var(
        file_list: str | list[str], 
        varlist_orig: list[str], 
        varlist_std: list[str]) -> None:
    """
    Rename files by updating the variable name in their filenames using a standardised variable list.
    
    This function systematically renames files by extracting the variable name from
    the filename, finding its standardised equivalent, and updating the filename
    accordingly. This is useful for standardising file naming conventions across
    different datasets.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of file paths to rename.
    varlist_orig : list[str]
        List of original variable names to be replaced.
    varlist_std : list[str]
        List of standardised variable names corresponding to `varlist_orig`.
        Must have the same length as `varlist_orig`.
    
    Returns
    -------
    None
        The function renames files in-place.
        
    Raises
    ------
    ValueError
        If a variable name in the filename is not found in `varlist_orig`.
        
    Notes
    -----
    This function modifies the actual filenames on the filesystem. Ensure you
    have backups if the original filenames are important.
    
    Examples
    --------
    >>> # Standardise temperature variable names in filenames
    >>> change_filenames_by_var(['temp_daily.nc', 'tmp_monthly.nc'],
    ...                        ['temp', 'tmp'], ['temperature', 'temperature'])
    # Results in files renamed to: ['temperature_daily.nc', 'temperature_monthly.nc']
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    for file in file_list:
        std_var = _get_varname_in_filename(file, True, varlist_orig, varlist_std)
        file_name_parts = obj_path_specs(file, file_spec_key="name_noext_parts", SPLIT_DELIM=SPLIT_DELIM1)
        new_filename = modify_obj_specs(file, "name_noext_parts", (file_name_parts[0], std_var))
        rename_objects(file, new_filename)

        

# Time and Date Adjustment Functions #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def cdo_inttime(
        file_list: str | list[str], 
        year0: int, 
        month0: int, 
        day0: int, 
        hour0: int, 
        minute0: int, 
        second0: int, 
        time_step: str,
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8", 
        shell: bool = True) -> None:
    """
    Initialise time steps in files with a specific starting date and step using CDO's inttime operator.
    
    This function sets up time coordinates in NetCDF files by defining a starting
    date/time and a time step interval. It's useful for files that lack proper
    time coordinates or need time coordinate correction.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to process.
    year0 : int
        Starting year for the time coordinate.
    month0 : int
        Starting month for the time coordinate (1-12).
    day0 : int
        Starting day for the time coordinate (1-31).
    hour0 : int
        Starting hour for the time coordinate (0-23).
    minute0 : int
        Starting minute for the time coordinate (0-59).
    second0 : int
        Starting second for the time coordinate (0-59).
    time_step : str
        Time step size and unit (e.g., '6hour', '1day', '1month').
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function modifies the files in-place by updating time coordinates.
        
    Examples
    --------
    >>> # Set time coordinates starting from 2000-01-01 00:00:00 with daily steps
    >>> cdo_inttime(['data.nc'], 2000, 1, 1, 0, 0, 0, '1day')
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    for file in file_list:
        temp_file = add_to_path(file)
        start_date = f"{year0}-{month0:02d}-{day0:02d} {hour0:02d}:{minute0:02d}:{second0:02d}"
        cmd = f"cdo inttime,{start_date},{time_step} '{file}' '{temp_file}'"

        # Run the command and capture the output
        process_exit_info = run_system_command(
            cmd, 
            capture_output=capture_output,
            return_output_name=return_output_name,
            encoding=encoding,
            shell=shell
        )

        # Call exit_info with parameters based on capture_output    
        exit_info(process_exit_info,
            check_stdout=capture_output,
            check_stderr=capture_output,
            check_return_code=True
        )

        # Rename the temporary file to the given file
        rename_objects(temp_file, file)
        

def cdo_shifttime(
        file_list: str | list[str], 
        shift_val: str,
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Shift time steps in files by a specified value using CDO's shifttime operator.
    
    This function adjusts time coordinates in NetCDF files by adding or subtracting
    a specified time amount. This is useful for correcting time zones, adjusting
    time references, or synchronising datasets.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to process.
    shift_val : str
        Time shift value with sign and unit (e.g., '+1day', '-6hours', '+3months').
        Positive values shift time forward, negative values shift backward.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.
        
    Returns
    -------
    None
        The function modifies the files in-place by shifting time coordinates.
        
    Examples
    --------
    >>> # Shift time forward by one day
    >>> cdo_shifttime(['data.nc'], '+1day')
    
    >>> # Shift time backward by 6 hours
    >>> cdo_shifttime(['hourly_data.nc'], '-6hours')
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    for file in file_list:
        temp_file = add_to_path(file)
        cmd = f"cdo shifttime,{shift_val} '{file}' '{temp_file}'"

        # Run the command and capture the output
        process_exit_info = run_system_command(
            cmd, 
            capture_output=capture_output,
            return_output_name=return_output_name,
            encoding=encoding,
            shell=shell
        )   

        # Call exit_info with parameters based on capture_output
        exit_info(process_exit_info,
            check_stdout=capture_output,
            check_stderr=capture_output,
            check_return_code=True
        )   

        # Rename the temporary file to the given file
        rename_objects(temp_file, file)


# Miscellaneous Functions #
#~~~~~~~~~~~~~~~~~~~~~~~~~#

def create_grid_header_file(output_file, **kwargs):
    """
    Create a grid header file.

    Parameters
    ----------
    output_file : str | Path
        Path to the txt file where the reference grid will be stored.
    kwargs : dict
        Parameters that define the grid (e.g., xmin, ymax, total lines, total columns, etc.).

    Returns
    -------
    None
    """
    kwargs_values = list(kwargs.values())
    kwargs_keys = list(kwargs.keys())
    kwargs_keys.sort()

    if kwargs_keys != KEYLIST:
        kwargs = {key: val for key, val in zip(KEYLIST, kwargs_values)}

    grid_template = """gridtype  = lonlat
xsize     = {0:d}
ysize     = {1:d}
xname     = longitude
xlongname = "Longitude values"
xunits    = "degrees_east"
yname     = latitude
ylongname = "Latitude values"
yunits    = "degrees_north"
xfirst    = {2:.20f}
xinc      = {3:.20f}
yfirst    = {4:.20f}
"""
    grid_str = format_string(grid_template, tuple([kwargs[key] for key in KEYLIST[:6]]))
    
    with open(output_file, 'w') as output_f:
        output_f.write(grid_str)        
        

def custom_cdo_mergetime(
        file_list: str | list[str], 
        custom_output_name: str, 
        create_temp_file: bool = False,
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Custom CDO mergetime operation that optionally uses a temporary file.
    
    This function provides a flexible version of CDO's mergetime operation,
    allowing for custom output naming and optional temporary file creation
    for intermediate processing steps.

    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to merge.
    custom_output_name : str
        Custom name for the output merged file.
    create_temp_file : bool, optional
        Whether to use a temporary file for intermediate steps. If True,
        creates a temporary file first. Default is False.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Returns
    -------
    None
        The function creates a merged NetCDF file with the specified name.
        
    Notes
    -----
    This function uses 64-bit floating point precision (-b F64) and NetCDF4
    format (-f nc4) for the output file.
    
    Examples
    --------
    >>> # Merge files with custom output name
    >>> custom_cdo_mergetime(['file1.nc', 'file2.nc'], 'merged_data.nc')
    
    >>> # Merge with temporary file creation
    >>> custom_cdo_mergetime(['file1.nc', 'file2.nc'], 'output.nc', 
    ...                      create_temp_file=True)
    """
    # Defensive programming: handle nested lists
    if not isinstance(file_list, list):
        file_list = [file_list]
    else:
        file_list = list(flatten_list(file_list))
    
    allfiles_string = flatten_to_string(file_list)
    
    if not create_temp_file:
        cmd = f"cdo -b F64 -f nc4 mergetime '{allfiles_string}' {custom_output_name}"
    else:
        temp_file = add_to_path(file_list[0])
        cmd = f"cdo -b F64 -f nc4 mergetime '{allfiles_string}' {temp_file}"
                     
    # Run the command and capture the output
    process_exit_info = run_system_command(
        cmd, 
        capture_output=capture_output,
        return_output_name=return_output_name,
        encoding=encoding,
        shell=shell
    )

    # Call exit_info with parameters based on capture_output
    exit_info(process_exit_info,
        check_stdout=capture_output,
        check_stderr=capture_output,
        check_return_code=True
    )


#--------------------------#
# Parameters and constants #
#--------------------------#

# Strings #
#---------#

# String-splitting delimiters #
SPLIT_DELIM1 = COMMON_DELIMITER_LIST[0]
SPLIT_DELIM2 = COMMON_DELIMITER_LIST[1]

# Grid header file function key list #
KEYLIST = ['total_columns', 'total_lines', 'xmin', 'xres', 'ymin', 'yres']

# Calendar and date-time parameters #
TIME_FREQS_DELTA = [TIME_FREQUENCIES_ABBREVIATED[0]] + TIME_FREQUENCIES_ABBREVIATED[2:4]
FREQ_ABBRS_DELTA = [TIME_FREQUENCIES_BRIEF[0]] + TIME_FREQUENCIES_BRIEF[2:4]

# Statistics and operators #
#--------------------------#

# Basic statistics #
STATKIT = [
    "max", "min", "sum", 
    "mean", "avg", 
    "var", "var1",
    "std", "std1"
]
  
# CDO remapping options #
CDO_REMAP_OPTION_DICT = {
    "ordinary" : "remap",
    "bilinear" : "remapbil",
    "nearest_neighbour" : "remapnn",
    "bicubic" : "remapbic",
    "conservative1" : "remapcon",
    "conservative2" : "remapcon2",
    "conservative1_y" : "remapycon",
    "distance_weighted_average" : "remapdis",
    "vertical_hybrid" : "remapeta",
    "vertical_hybrid_sigma" : "remapeta_s",
    "vertical_hybrid_z" : "remapeta_z",
    "largest_area_fraction" : "remaplaf",
    "sum" : "remapsum",
}

CDO_REMAP_OPTIONS = list(CDO_REMAP_OPTION_DICT.keys())

# Basic operator switch case dictionary #
CDO_OPERATOR_STR_DICT = {
    BASIC_ARITHMETIC_OPERATORS[0] : "add",
    BASIC_ARITHMETIC_OPERATORS[1] : "sub",
    BASIC_ARITHMETIC_OPERATORS[2] : "mul",
    BASIC_ARITHMETIC_OPERATORS[3] : "div"
}
