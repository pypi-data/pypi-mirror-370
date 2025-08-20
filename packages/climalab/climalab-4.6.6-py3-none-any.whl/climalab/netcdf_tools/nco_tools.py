#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------#
# Import project modules #
#------------------------#

from filewise.file_operations.ops_handler import add_to_path, rename_objects
from paramlib.global_parameters import BASIC_ARITHMETIC_OPERATORS
from pygenutils.operative_systems.os_operations import run_system_command, exit_info
from pygenutils.strings.text_formatters import format_string, print_format_string

#-------------------------#
# Define custom functions #
#-------------------------#

def modify_variable_units_and_values(
        file_list: str | list[str],
        variable_name: str,
        operator: str,
        value: int | float,
        new_unit: str,
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Modify variable units and values in NetCDF files using NCO tools.
    
    This function changes both the units attribute and numerical values of a specified
    variable in NetCDF files. It uses ncatted to modify units and ncap2 to perform
    mathematical operations on the variable values.
    
    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to modify.
    variable_name : str
        Name of the variable to modify.
    operator : {'+', '-', '*', '/'}
        Mathematical operator to apply.
    value : int | float
        Numerical value to use with the operator.
    new_unit : str
        New unit string to assign to the variable.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.
        
    Raises
    ------
    ValueError
        If the operator is not one of the basic four mathematical rules.
        
    Notes
    -----
    This function creates temporary files during processing and automatically
    cleans them up by renaming them back to the original filenames.
    
    Examples
    --------
    >>> # Convert temperature from Celsius to Kelvin
    >>> modify_variable_units_and_values(
    ...     'temperature.nc', 'temp', '+', 273.15, 'K'
    ... )
    
    >>> # Scale precipitation values and change units
    >>> modify_variable_units_and_values(
    ...     ['precip1.nc', 'precip2.nc'], 'pr', '*', 86400, 'mm/day'
    ... )
    """
    
    if not isinstance(file_list, list):
        file_list = [file_list]
    lfl = len(file_list)    
        
    for file_num, file_name in enumerate(file_list, start=1): 
        temp_file = add_to_path(file_name, str2add=file_name)
        
        is_whole_number = (abs(value-int(value)) == 0)
        use_integer_format = int(is_whole_number)
        
        var_chunit_formatted\
        = f"ncatted -a units,{variable_name},o,c,'{new_unit}' '{file_name}'"   

        # Run the command
        process_exit_info = run_system_command(
            var_chunit_formatted,
            capture_output=True,
            return_output_name=True,
            encoding="utf-8",
            shell=True
        )

        # Call exit_info with parameters based on capture_output
        exit_info(process_exit_info,
            check_stdout=True,
            check_stderr=True,
            check_return_code=True
        )
        
        if operator not in BASIC_ARITHMETIC_OPERATORS:
            raise ValueError(INVALID_OPERATOR_ERR_TEMPLATE)
        else:            
            # Print progress information #
            operator_gerund = OPERATOR_GERUND_DICT.get(operator)
            format_args_print = (NCAP2_BASE_ARGS, 
                                 operator_gerund, value, variable_name, 
                                 file_num, lfl)
            print_format_string(PREFMT_STR_PROGRESS_UV, format_args_print)
            
            # Get the command from the corresponding switch case dictionary #
            format_args = (NCAP2_BASE_ARGS,
                           variable_name, variable_name, value,
                           file_name, temp_file)
            
            varval_mod_formatted = \
            format_string(VARVAL_MOD_COMMAND_TEMPLATES_UV
                          .get(operator)
                          .get(use_integer_format),
                          format_args)
        
            # Execute the command through the shell #
            process_exit_info = run_system_command(
                varval_mod_formatted,
                capture_output=capture_output,
                return_output_name=return_output_name,
                encoding=encoding,
                shell=shell
            )        

            # Call exit_info with parameters based on capture_output
            exit_info(process_exit_info,
                check_stdout=capture_output,
                check_stderr=capture_output,
                check_return_code=capture_output
            )
            
            # Rename the temporary file to the given file
            rename_objects(temp_file, file_name)
            

def modify_coordinate_values_by_threshold(
        file_list: str | list[str],
        dimension_name: str,
        threshold: int | float,
        operator: str,
        value: int | float,
        threshold_mode: str = "max",
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Conditionally modify coordinate values based on a threshold in NetCDF files.
    
    This function applies mathematical operations to coordinate values only when
    they meet certain threshold conditions. It uses ncap2 with conditional 'where'
    statements to selectively modify coordinate values.
    
    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to modify.
    dimension_name : str
        Name of the dimension/coordinate to modify.
    threshold : int | float
        Threshold value for the conditional operation.
    operator : {'+', '-', '*', '/'} 
        Mathematical operator to apply.
    value : int | float
        Numerical value to use with the operator.
    threshold_mode : str, optional
        Threshold comparison mode. Either 'max' or 'min'. Default is 'max'.
        - 'max': Apply operation where coordinate < threshold
        - 'min': Apply operation where coordinate > threshold
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.
        
    Raises
    ------
    ValueError
        If the operator is not one of the basic four mathematical rules.
    ValueError
        If threshold_mode is not 'max' or 'min'.
        
    Notes
    -----
    This function creates temporary files during processing and automatically
    cleans them up by renaming them back to the original filenames.
    
    Examples
    --------
    >>> # Add 360 to longitude values less than 0 (convert from [-180,180] to [0,360])
    >>> modify_coordinate_values_by_threshold(
    ...     'data.nc', 'lon', 0, '+', 360, threshold_mode='min'
    ... )
    
    >>> # Subtract 360 from longitude values greater than 180
    >>> modify_coordinate_values_by_threshold(
    ...     'data.nc', 'lon', 180, '-', 360, threshold_mode='max'
    ... )
    """
    
    if not isinstance(file_list, list):
        file_list = [file_list]
    lfl = len(file_list) 
    
    for file_num, file_name in enumerate(file_list, start=1):
        temp_file = add_to_path(file_name, str2add=file_name)
        
        is_whole_number = (abs(value-int(value)) == 0)
        use_integer_format = int(is_whole_number)
        
        if operator not in BASIC_ARITHMETIC_OPERATORS:
            raise ValueError(INVALID_OPERATOR_ERR_TEMPLATE)
        else:
            if threshold_mode not in THRESHOLD_MODE_OPTS:
                raise ValueError(format_string(INVALID_THRESHOLD_MODE_ERR_TEMPLATE,
                                               THRESHOLD_MODE_OPTS))
            
            else:
                # Print progress information #
                operator_gerund = OPERATOR_GERUND_DICT.get(operator)
                    
                format_args_print = (NCAP2_BASE_ARGS, 
                                     operator_gerund, value, dimension_name, 
                                     file_num, lfl)
                
                print_format_string(PREFMT_STR_PROGRESS_BTH, format_args_print)
                
                # Get the command from the corresponding switch case dictionary #
                format_args = (NCAP2_BASE_ARGS,
                               dimension_name, threshold,
                               dimension_name, dimension_name, value,
                               file_name, temp_file)
        
                dimval_mod_formatted = \
                format_string(VARVAL_MOD_COMMAND_TEMPLATES_BTH
                              .get(operator)
                              .get(threshold_mode)
                              .get(use_integer_format),
                              format_args)
            
                # Execute the command through the shell #
                process_exit_info = run_system_command(
                    dimval_mod_formatted,
                    capture_output=capture_output,
                    return_output_name=return_output_name,
                    encoding=encoding,
                    shell=shell
                )
                
                # Call exit_info with parameters based on capture_output
                exit_info(process_exit_info,
                    check_stdout=capture_output,
                    check_stderr=capture_output,
                    check_return_code=capture_output
                )
                
                # Rename the temporary file to the given file
                rename_objects(temp_file, file_name)
            

def modify_coordinate_all_values(
        file_list: str | list[str],
        dimension_name: str,
        operator: str,
        value: int | float,
        threshold_mode: str = "max",
        capture_output: bool = False,
        return_output_name: bool = False,
        encoding: str = "utf-8",
        shell: bool = True) -> None:
    """
    Modify all coordinate values of a specified dimension in NetCDF files.
    
    This function applies mathematical operations to all values of a specified
    coordinate/dimension in NetCDF files using ncap2. Unlike the threshold-based
    version, this modifies all coordinate values unconditionally.
    
    Parameters
    ----------
    file_list : str | list[str]
        Single file path or list of NetCDF file paths to modify.
    dimension_name : str
        Name of the dimension/coordinate whose values will be modified.
    operator : {'+', '-', '*', '/'}
        Mathematical operator to apply.
    value : int | float
        Numerical value to use with the operator.
    threshold_mode : str, optional
        Threshold comparison mode (kept for consistency with other functions).
        Either 'max' or 'min'. Default is 'max'. Note: This parameter doesn't
        affect behaviour in this function as all values are modified.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.
        
    Raises
    ------
    ValueError
        If the operator is not one of the basic four mathematical rules.
    ValueError
        If threshold_mode is not 'max' or 'min'.
        
    Notes
    -----
    This function creates temporary files during processing and automatically
    cleans them up by renaming them back to the original filenames.
    
    The threshold_mode parameter is maintained for API consistency but doesn't
    affect the operation since all coordinate values are modified regardless.
    
    Examples
    --------
    >>> # Convert all longitude values from degrees to radians
    >>> modify_coordinate_all_values(
    ...     'data.nc', 'lon', '*', 3.14159/180
    ... )
    
    >>> # Shift all time values by adding 30 days
    >>> modify_coordinate_all_values(
    ...     ['file1.nc', 'file2.nc'], 'time', '+', 30
    ... )
        
    >>> # Scale all latitude values
    >>> modify_coordinate_all_values(
    ...     'grid.nc', 'lat', '*', 1.5
    ... )
    """
    
    if not isinstance(file_list, list):
        file_list = [file_list]
    lfl = len(file_list) 
    
    for file_num, file_name in enumerate(file_list, start=1): 
        temp_file = add_to_path(file_name, str2add=file_name)
        
        is_whole_number = (abs(value-int(value)) == 0)
        use_integer_format = int(is_whole_number)
        
        if operator not in BASIC_ARITHMETIC_OPERATORS:
            raise ValueError(INVALID_OPERATOR_ERR_TEMPLATE)
        else:
            if threshold_mode not in THRESHOLD_MODE_OPTS:
                raise ValueError(format_string(INVALID_THRESHOLD_MODE_ERR_TEMPLATE,
                                               THRESHOLD_MODE_OPTS))
            
            else:
                # Print progress information #
                operator_gerund = OPERATOR_GERUND_DICT.get(operator)
                    
                format_args_print = (NCAP2_BASE_ARGS,
                                     operator_gerund, value, dimension_name, 
                                     file_num, lfl)
                
                print_format_string(PREFMT_STR_PROGRESS_BTH, format_args_print)
                
                # Get the command from the corresponding switch case dictionary #
                format_args = (NCAP2_BASE_ARGS,
                               dimension_name, dimension_name, value,
                               file_name, temp_file)
                
                dimval_mod_formatted = \
                format_string(VARVAL_MOD_COMMAND_TEMPLATES_ALL
                              .get(operator)
                              .get(threshold_mode)
                              .get(use_integer_format),
                              format_args)
            
                # Execute the command through the shell #
                process_exit_info = run_system_command(
                    dimval_mod_formatted,
                    capture_output=capture_output,
                    return_output_name=return_output_name,
                    encoding=encoding,
                    shell=shell
                )
                
                # Call exit_info with parameters based on capture_output
                exit_info(process_exit_info,
                    check_stdout=capture_output,
                    check_stderr=capture_output,
                    check_return_code=capture_output
                )
                
                # Rename the temporary file to the given file
                rename_objects(temp_file, file_name)

#--------------------------#
# Parameters and constants #
#--------------------------#

# Template strings #
#------------------#

# NCAP2 command #
NCAP2_BASE_ARGS = "ncap2 -O -s"

# Progress verbose #
PREFMT_STR_PROGRESS_UV = \
"""{} the value of {} to '{}' variable's value for file
{} out of {}..."""

PREFMT_STR_PROGRESS_BTH = \
"""{}, where necessary, the value of {} to '{}' dimension's values for file
{} out of {}..."""

PREFMT_STR_PROGRESS_ALL = \
"""{} the value of {} to '{}' dimension's values for file
{} out of {}..."""

# NCAP2 command's argument syntaxes, for all values or dimensions #
ADDVALUE_COMMAND_TEMPLATE = """{} '{}={}+{}' '{}' '{}'"""
SUBTRVALUE_COMMAND_TEMPLATE = """{} '{}={}-{}' '{}' '{}'"""
MULTVALUE_COMMAND_TEMPLATE = """{} '{}={}*{}' '{}' '{}'"""
DIVVALUE_COMMAND_TEMPLATE = """{} '{}={}/{}' '{}' '{}'"""

ADDVALUE_FLOAT_COMMAND_TEMPLATE = """{} '{}={}+{}.0f' '{}' '{}'"""
SUBTRVALUE_FLOAT_COMMAND_TEMPLATE = """{} '{}={}-{}.0f' '{}' '{}'"""
MULTVALUE_FLOAT_COMMAND_TEMPLATE = """{} '{}={}*{}.0f' '{}' '{}'"""
DIVVALUE_FLOAT_COMMAND_TEMPLATE = """{} '{}={}/{}.0f' '{}' '{}'"""

# NCAP2 command's argument syntaxes, conditional #
ADDVALUE_WHERE_MAX_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}+{}' '{}' '{}'"""
SUBTRVALUE_WHERE_MAX_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}-{}' '{}' '{}'"""
MULTVALUE_WHERE_MAX_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}*{}' '{}' '{}'"""
DIVVALUE_WHERE_MAX_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}/{}' '{}' '{}'"""

ADDVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}+{}.0f' '{}' '{}'"""
SUBTRVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}-{}.0f' '{}' '{}'"""
MULTVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}*{}.0f' '{}' '{}'"""
DIVVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE = """{} 'where({}<{}) {}={}/{}.0f' '{}' '{}'"""

ADDVALUE_WHERE_MIN_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}+{}' '{}' '{}'"""
SUBTRVALUE_WHERE_MIN_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}-{}' '{}' '{}'"""
MULTVALUE_WHERE_MIN_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}*{}' '{}' '{}'"""
DIVVALUE_WHERE_MIN_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}/{}' '{}' '{}'"""

ADDVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}+{}.0f' '{}' '{}'"""
SUBTRVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}-{}.0f' '{}' '{}'"""
MULTVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}*{}.0f' '{}' '{}'"""
DIVVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE = """{} 'where({}>{}) {}={}/{}.0f' '{}' '{}'"""

# Fixed strings #
#---------------#

# Error messages #
INVALID_OPERATOR_ERR_TEMPLATE = \
f"Invalid basic operator chosen. Options are {BASIC_ARITHMETIC_OPERATORS}."
INVALID_THRESHOLD_MODE_ERR_TEMPLATE = \
"""Invalid threshold mode. Options are {}."""


# Locally available threshold mode list #
#---------------------------------------#

THRESHOLD_MODE_OPTS = ["max", "min"]

# Switch case dictionaries #
#--------------------------#

OPERATOR_GERUND_DICT = {
    BASIC_ARITHMETIC_OPERATORS[0] : "Adding",
    BASIC_ARITHMETIC_OPERATORS[1] : "Subtracting",
    BASIC_ARITHMETIC_OPERATORS[2] : "Multiplying",
    BASIC_ARITHMETIC_OPERATORS[3] : "Dividing"
    }

VARVAL_MOD_COMMAND_TEMPLATES_UV = {
    BASIC_ARITHMETIC_OPERATORS[0] : {
        1 : ADDVALUE_COMMAND_TEMPLATE,
        0 : ADDVALUE_FLOAT_COMMAND_TEMPLATE
    },
    BASIC_ARITHMETIC_OPERATORS[1] : {
        1 : SUBTRVALUE_COMMAND_TEMPLATE,
        0 : SUBTRVALUE_FLOAT_COMMAND_TEMPLATE
    },
    BASIC_ARITHMETIC_OPERATORS[2] : {
        1 : MULTVALUE_COMMAND_TEMPLATE,
        0 : MULTVALUE_FLOAT_COMMAND_TEMPLATE
    },
    BASIC_ARITHMETIC_OPERATORS[3] : {
        1 : DIVVALUE_COMMAND_TEMPLATE,
        0 : DIVVALUE_FLOAT_COMMAND_TEMPLATE
    }
}

VARVAL_MOD_COMMAND_TEMPLATES_BTH = {
    BASIC_ARITHMETIC_OPERATORS[0] : {
        "max" : {
            1 : ADDVALUE_WHERE_MAX_COMMAND_TEMPLATE,
            0 : ADDVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : ADDVALUE_WHERE_MIN_COMMAND_TEMPLATE,
            0 : ADDVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE
        },
    },
    BASIC_ARITHMETIC_OPERATORS[1] : {
        "max" : {
            1 : SUBTRVALUE_WHERE_MAX_COMMAND_TEMPLATE,
            0 : SUBTRVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : SUBTRVALUE_WHERE_MIN_COMMAND_TEMPLATE,
            0 : SUBTRVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE
        },
    },
    BASIC_ARITHMETIC_OPERATORS[2] : {
        "max" : {
            1 : MULTVALUE_WHERE_MAX_COMMAND_TEMPLATE,
            0 : MULTVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : MULTVALUE_WHERE_MIN_COMMAND_TEMPLATE,
            0 : MULTVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE
        },
    },
    BASIC_ARITHMETIC_OPERATORS[3] : {
        "max" : {
            1 : DIVVALUE_WHERE_MAX_COMMAND_TEMPLATE,
            0 : DIVVALUE_WHERE_MAX_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : DIVVALUE_WHERE_MIN_COMMAND_TEMPLATE,
            0 : DIVVALUE_WHERE_MIN_FLOAT_COMMAND_TEMPLATE
        }
    }
}

VARVAL_MOD_COMMAND_TEMPLATES_ALL = {
    BASIC_ARITHMETIC_OPERATORS[0] : {
        "max" : {
            1 : ADDVALUE_COMMAND_TEMPLATE,
            0 : ADDVALUE_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : ADDVALUE_COMMAND_TEMPLATE,
            0 : ADDVALUE_FLOAT_COMMAND_TEMPLATE
        },
    },
    BASIC_ARITHMETIC_OPERATORS[1] : {
        "max" : {
            1 : SUBTRVALUE_COMMAND_TEMPLATE,
            0 : SUBTRVALUE_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : SUBTRVALUE_COMMAND_TEMPLATE,
            0 : SUBTRVALUE_FLOAT_COMMAND_TEMPLATE
        },
    },
    BASIC_ARITHMETIC_OPERATORS[2] : {
        "max" : {
            1 : MULTVALUE_COMMAND_TEMPLATE,
            0 : MULTVALUE_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : MULTVALUE_COMMAND_TEMPLATE,
            0 : MULTVALUE_FLOAT_COMMAND_TEMPLATE
        },
    },
    BASIC_ARITHMETIC_OPERATORS[3] : {
        "max" : {
            1 : DIVVALUE_COMMAND_TEMPLATE,
            0 : DIVVALUE_FLOAT_COMMAND_TEMPLATE
        },
        "min" : {
            1 : DIVVALUE_COMMAND_TEMPLATE,
            0 : DIVVALUE_FLOAT_COMMAND_TEMPLATE
        }
    }
}
