#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**Goal**

This module aims to perform basic mathematical operations regarding
Pandas, Numpy date and date/time objects.
"""

#----------------#
# Import modules #
#----------------#

import datetime
import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args, get_type_str
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.arrays_and_lists.patterns import select_elements
from pygenutils.strings.text_formatters import format_string, print_format_string
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.time_handling.time_formatters import (
    datetime_obj_converter,
    parse_float_dt,
    parse_dt_string
)

#------------------#
# Define functions #
#------------------#

#%%

# Input validation streamliner #
#------------------------------#
        
def _validate_option(arg_iterable, error_class, error_str):
    """
    Validate if the given option is within the list of allowed options.
    Specific for printing customised error messages.

    Parameters
    ----------
    arg_iterable : str, list or tuple
        Iterable consisting of elements to map into error_str, 
        particularly the option and the iterable of allowed ones.
    error_class : {TypeError, ValueError}
        Error class to raise if option is not in the list of allowed ones.
    error_str : str
        Single or multiple line string denoting an error.

    Raises
    ------    
    TypeError or ValueError: 
        If the option is not in the list of allowed options, with a detailed explanation.
    KeyError
        If error_class is not within the possible errors.
        It is preferred to raise this error rather than another ValueError
        to avoid confusion with the above case.
    """
    param_keys = get_caller_args()
    err_clas_arg_pos = find_substring_index(param_keys, "error_class")
    
    if error_class not in ERROR_CLASS_LIST:
        raise KeyError(f"Unsupported error class '{param_keys[err_clas_arg_pos]}'. "
                       f"Choose one from {ERROR_CLASS_LIST}.")
    
    option = arg_iterable[0]
    allowed_options = arg_iterable[1]
    
    if option not in allowed_options:
        raise error_class(format_string(error_str, arg_iterable))

# Times #
#-------#

# Sum and subtract operations #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# Main method #
#-#-#-#-#-#-#-#

def sum_dt_objects(dt_obj_list,
                   dt_fmt_str="%T",
                   operation="sum",
                   output_format="standard"):
    """
    Calculate the sum or difference of a list of clock times
    and format the output accordingly.

    Parameters
    ----------
    dt_obj_list : list[str] | tuple[str] | np.ndarray[str]
        A list, tuple, or numpy.ndarray containing time objects as strings 
        that follow the format specified in 'time_fmt_str'.
    operation : str, optional
        The operation to perform on the clock times. Supported operations 
        are "sum" (default) and "subtr" for subtraction.
    dt_fmt_str : str, optional
        A format string that defines the structure of each object in 'dt_obj_list'. 
        Default is '%T'.
    output_format : str, optional
        The format of the output. Supported options:
        - 'standard': Returns the total time as a pandas.Timedelta object (default).
        - 'string': Returns the total time as a string.
        - 'time_only': Returns the total time as a datetime.time object.
        - 'tuple': Returns a tuple of (days, hours, minutes, seconds) from the total time.

    Returns
    -------
    object
        The total time after performing the specified operation,
        formatted based on 'output_format'.

    Raises
    ------
    TypeError
        If 'dt_obj_list' is not a list, tuple, or numpy.ndarray.
    ValueError
        If 'dt_obj_list' contains fewer than 2 elements or if an unsupported 
        operation or output format is specified.
    """

    # Argument adecuacy controls #
    ##############################

    # Date and/or time list format control and its length #
    param_keys = get_caller_args()
    obj_list_pos = param_keys.index("dt_obj_list")
    
    if isinstance(dt_obj_list, str):
        raise TypeError(f"Argument '{param_keys[obj_list_pos]}' "
                        f"(number {obj_list_pos}) must either be a "
                        "list, tuple or numpy.ndarray.")
    elif (isinstance(dt_obj_list, (list, tuple, np.ndarray)) and len(dt_obj_list) < 2):
        raise ValueError(f"Argument '{param_keys[obj_list_pos]}' "
                         "must contain at least two objects.")
    
    # Handle nested lists by flattening them first
    if isinstance(dt_obj_list, list) and any(isinstance(item, list) for item in dt_obj_list):
        dt_obj_list = flatten_list(dt_obj_list)
    
    # Operation argument control #        
    format_args_math_op = (operation, BASIC_MATH_OPT_LIST)
    _validate_option(format_args_math_op, ValueError, INVALID_MATH_OPERATION_ERROR)
        
    # Output format parameter control         
    arg_iterable_output_format = (output_format, TIME_OUTPUT_FORMAT_OPTIONS)
    _validate_option(arg_iterable_output_format, ValueError, INVALID_OUTPUT_FORMAT_TEMPLATE)
    
    # Program progression #
    #######################
    
    # Time delta object conversions #
    timedelta_list = []
    for dt_obj in dt_obj_list:
        dt_obj = parse_dt_string(dt_obj, dt_fmt_str)
        time_obj = extract_dt_part(dt_obj)
        timedelta_obj = datetime_obj_converter(time_obj, "float")
        timedelta_list.append(timedelta_obj)
        
    # Perform the arithmetical operations #
    total_timedelta = OPERATION_DICT.get(operation)(timedelta_list)    
    
    # Return the result in the specified output format #
    total_timedelta_formatted = TIME_OUTPUT_FORMAT_DICT.get(output_format)(total_timedelta)
    return total_timedelta_formatted
    

# Auxiliary methods #
#-#-#-#-#-#-#-#-#-#-#

def extract_dt_part(datetime_obj, part="time", arg_list=None):
    """
    Return the time or date part of a datetime object.

    Parameters
    ----------
    datetime_obj : datetime.datetime
        The datetime object from which to extract the time part.
    part : {'time', 'date'}
        The part of the datetime object to be returned.
        If 'time', the object returned is of type datetime.time 
        and if 'date' a datetime.date object.
        Default value is 'time'.
    arg_list : list, optional
        List containing specific parts of the datetime object.
        
    Raises
    ------
    ValueError
        If 'part' is neither 'time' nor 'date'.

    Returns
    -------
    datetime.time or datetime.date
        The time or date part of the datetime object, depending on the
        value of 'part'.
    """
    format_args_extract = (part, ["time", "date"])
    _validate_option(format_args_extract, ValueError, INVALID_OUTPUT_FORMAT_TEMPLATE)
    
    return DATETIME_OBJECT_PART_DICT.get(part)(datetime_obj, arg_list)


# Time average #
#~~~~~~~~~~~~~~#

# Adapted from https://stackoverflow.com/questions/12033905/using-python-to-create-an-average-out-of-a-list-of-times
# and refined with ChatGPT

# Main method #
#-#-#-#-#-#-#-#

def dt_average(dt_obj_list, 
               time_fmt_str="%T",
               output_format="standard"):
    """
    Calculate the average time from a list of time objects
    and format the output accordingly.
    
    Parameters
    ----------
    dt_obj_list : list, tuple, or numpy.ndarray
        A collection of date and/or time objects or strings that follow 
        the format specified in 'time_fmt_str'.
    time_fmt_str : str, optional
        The format string that specifies the format of the time objects. 
        This only affects objects that are strings. Default is "%T".
        Note that all strings must have at least the detectable part 
        specified by the given format string.
    output_format : str, optional
        The format of the output. Supported options:
        - 'standard': Returns the total time as a pandas.Timedelta object (default).
        - 'string': Returns the total time as a string.
        - 'time_only': Returns the total time as a datetime.time object.
        - 'tuple': Returns a tuple of (days, hours, minutes, seconds) from the total time.
    
    Returns
    -------
    object
        The total time after performing the specified operation,
        formatted based on 'output_format'.
        
    Raises
    ------
    TypeError
        If 'dt_obj_list' is not a list, tuple, or numpy.ndarray.
    ValueError
        If 'dt_obj_list' contains fewer than 2 elements
        or if an unsupported output format is specified.
    """    
    # Argument adecuacy controls #
    ##############################

    # Date and/or time list format control and its length #
    param_keys = get_caller_args()
    obj_list_pos = find_substring_index("dt_obj_list")
    
    if isinstance(dt_obj_list, str):
        raise TypeError(f"Argument '{param_keys[obj_list_pos]}' "
                        f"(number {obj_list_pos}) must either be a "
                        "list, tuple or numpy.ndarray.")
    elif (isinstance(dt_obj_list, (list, tuple, np.ndarray)) and len(dt_obj_list) < 2):
        raise ValueError(f"Argument '{param_keys[obj_list_pos]}' "
                         "must contain at least two objects.")
        
    # Output format parameter control #
    arg_iterable_output_format = (output_format, TIME_OUTPUT_FORMAT_OPTIONS)
    _validate_option(arg_iterable_output_format, ValueError, INVALID_OUTPUT_FORMAT_TEMPLATE)
        
    # Program progression #
    #######################
        
    angles = [_dt_to_radians(dt_obj, "datetime", time_fmt_str) for dt_obj in dt_obj_list]
    avg_angle = _average_angle(angles)    
    time_average = _radians_to_time_of_day(avg_angle)
    
    # Return the result in the specified output format #
    time_average_formatted = TIME_OUTPUT_FORMAT_DICT.get(output_format)(time_average)
    return time_average_formatted


# Auxiliary methods #
#-#-#-#-#-#-#-#-#-#-#

def _dt_to_radians(t, convert_to="datetime", time_fmt_str=None):
    """
    Convert a time object to radians.
    
    Parameters
    ----------
    t : str, numpy.datetime64, time.struct_time, datetime.datetime, 
        datetime.time, or pandas.Timestamp.
        The input time object to be converted.
    convert_to : str
        The target type to convert `datetime_obj` to.
        Accepted values depend on the input type, but as a first attempt,
        default value 'datetime' has been established.
        For example, if `datetime_obj` is a `datetime`, `convert_to` could be
        `datetime64`, `Timestamp`, etc.
    time_fmt_str : str
        The format string that specifies the format of the time objects. 
        This only affects objects that are strings.
        
    Returns
    -------
    float
        The angle in radians representing the input time on a 24-hour clock.
    
    Note
    ----
    Radians are calculated using a 24-hour circle,
    starting at north (midnight) and moving clockwise.
    """
    
    if isinstance(t, str):
        try:
            dt_obj = parse_dt_string(t, dt_fmt_str=time_fmt_str, unit="s")
        except Exception as e:
            raise RuntimeError(f"Error during string time parse to a datetime object: {e}.")
    else:
        try:
            dt_obj = datetime_obj_converter(t, convert_to)
        except Exception as e:
            obj_type = get_type_str(t)
            convert_to = get_caller_args()[1]
            raise RuntimeError("Error during parse of object type "
                               f"'{obj_type}' to '{convert_to}': {e}.")
    
    seconds_from_midnight = \
    datetime_obj_converter(extract_dt_part(dt_obj), "float")
    radians = seconds_from_midnight / (24 * 60 * 60) * 2 * np.pi
    return radians

def _average_angle(angles):
    """
    Calculate the average of a list of angles in RADIANS.
    
    Parameters
    ----------
    angles : list[float]
        The angles in radians to average.
        
    Returns
    -------
    float
        The average angle in radians.
    """
    x_sum = np.sum([np.sin(x) for x in angles])
    y_sum = np.sum([np.cos(x) for x in angles])
    
    x_mean = x_sum / len(angles)
    y_mean = y_sum / len(angles)
    
    return np.arctan2(x_mean, y_mean)  
 

def _radians_to_time_of_day(rads):
    """
    Convert an angle in radians to a time of day.
    
    Parameters
    ----------
    rads : float
        The angle in radians representing the time on a 24-hour clock.
        
    Returns
    -------
    datetime.time
        The time of day corresponding to the input radians.
    """
    seconds_from_midnight = rads / (2 * np.pi) * 24 * 60 * 60
    
    # It cannot be considered the next second
    # until the decimal fraction equals to 1.
    # However in some cases due to the previous calculations using np.pi()
    # and the seconds of a whole day, the decimal fraction can
    # be almost one by an extremely small number.
    # In these cases add one second to the integer part.
    tol = 1.0e-9
    
    second_fraction_to_one\
    = abs(abs(seconds_from_midnight - int(seconds_from_midnight)) - 1)
    
    if second_fraction_to_one < tol:
        seconds_from_midnight_int = int(seconds_from_midnight) + 1
    else:
        seconds_from_midnight_int = int(seconds_from_midnight)
    
    # If the seconds match the next day's midnight,
    # set the hour to zero instead of 24.
    # Minutes and seconds are calculated on the 60th basis.
    time_of_day = extract_dt_part(parse_float_dt(seconds_from_midnight_int))
    return time_of_day

#%%

# Dates #
#-------#

# Sum and subtract operations #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def sum_date_objects(date_list,
                     operation="sum",
                     dt_fmt_str="%F",
                     output_format="default"):
    """
    Calculate the sum or difference of a list of dates 
    and format the output accordingly.

    Parameters
    ----------
    date_list : list, tuple, or numpy.ndarray
        A list, tuple, or numpy.ndarray containing date objects or strings 
        that follow the format specified in 'time_fmt_str'.
    operation : str, optional
        The operation to perform on the dates. Supported operations 
        are "sum" (default) and "subtr" for subtraction.
    dt_fmt_str : str, optional
        A format string that defines the structure of each object in 'date_list'. 
        Default is '%F'.
    output_format : str, optional
        The format of the output. Supported options:
        - 'default': Returns the total date as a datetime.date object (default).
        - 'string': Returns the total date as a string in the format specified by 'time_fmt_str'.
        - 'tuple': Returns a tuple of (year, month, day) from the total date.

    Returns
    -------
    object
        The total date after performing the specified operation, 
        formatted based on 'output_format'.

    Raises
    ------
    TypeError
        If 'date_list' is not a list, tuple, or numpy.ndarray.
    ValueError
        If 'date_list' contains fewer than 2 elements or if an unsupported 
        operation or output format is specified.
    """

    # Argument adecuacy controls #
    ##############################
    
    # Date and/or time list format control and its length #
    param_keys = get_caller_args()
    date_list_pos = find_substring_index(param_keys, "date_list")
    
    if isinstance(date_list, str):
        raise TypeError(f"Argument '{param_keys[date_list_pos]}' "
                        f"(number {date_list_pos}) must either be a "
                        "list, tuple or numpy.ndarray.")
    elif (isinstance(date_list, (list, tuple, np.ndarray)) and len(date_list) < 2):
        raise ValueError(format_string(TOO_FEW_ARG_ERROR_TEMPLATE, "time"))
    
    # Operation argument control #
    format_args_math_op = (operation, BASIC_MATH_OPT_LIST)
    _validate_option(format_args_math_op, ValueError, INVALID_MATH_OPERATION_ERROR)
        
    # Output format parameter control #
    arg_iterable_output_format = (output_format, TIME_OUTPUT_FORMAT_OPTIONS)
    _validate_option(arg_iterable_output_format, ValueError, INVALID_OUTPUT_FORMAT_TEMPLATE)
    
    # Program progression #
    #######################
   
    # Perform the aritmethical operations #
    total_date = parse_dt_string(date_list[0], dt_fmt_str)
    for obj in date_list[1:]:
        date_obj = extract_dt_part(obj, part="date")
        total_date = _add_dates_with_year_gap(total_date, date_obj, operation=operation)
    
    # Return the result in the specified output format #
    total_date_formatted = DATE_OUTPUT_FORMAT_DICT.get(output_format)(total_date)
    return total_date_formatted
        
        
def return_date_part(datetime_obj, arg_list=None):
    """
    Return the date part of a datetime object.

    Parameters
    ----------
    datetime_obj : datetime.datetime
        The datetime object from which to extract the time part.
    arg_list : list, optional
        List containing specific parts of the datetime object.

    Returns
    -------
    datetime.date
        The date part of the datetime object.
    """
    if arg_list is None:
        date_obj = datetime_obj.date()
    else:
        date_obj = datetime_obj.date(*arg_list)
    return date_obj

def _add_dates_with_year_gap(date1, date2, operation):
    """
    Add or subtract two dates with consideration for year gaps 
    and handle overflow/underflow.

    Parameters
    ----------
    date1 : datetime.date
        The first date object.
    date2 : datetime.date
        The second date object.
    operation : str
        The operation to perform. Supported operations are "sum" and "subtr".

    Returns
    -------
    datetime.date
        The result date after performing the specified operation.

    Raises
    ------
    ValueError
        If the resulting date is invalid (e.g., February 30th).

    Notes
    -----
    This function adjusts the dates based on the operation 
    and handles overflow/underflow of months and days when necessary.
    """
    
    # Extract year, month, and day from both dates
    year1, month1, day1 = date1.year, date1.month, date1.day
    year2, month2, day2 = date2.year, date2.month, date2.day

    # Calculate the gap in years
    year_gap = abs(year2 - year1)

    # Date additions #
    ##################
    
    if operation == "sum":        
        # Add the months and days
        new_month = month1 + month2
        new_day = day1 + day2
        
        # Adjust the month and day for overflow
        while new_month > 12:
            new_month -= 12
            year_gap += 1
    
        # Create a dummy date to handle day overflow
        while True:
            try:
                result_date = datetime.date(year1 + year_gap, new_month, new_day)
                break
            except ValueError:
                new_day -= 1
                
                
    elif operation == "subtr":
        # Subtract the months and days
        new_month = month1 - month2
        new_day = day1 - day2
        
        # Adjust the month and day for underflow
        while new_month < 1:
            new_month += 12
            year_gap += 1
    
        # Create a dummy date to handle day underflow
        while True:
            try:
                result_date = datetime.date(year1 - year_gap, new_month, new_day)
                break
            except ValueError:
                new_day += 1

    return result_date


# Natural years #
#~~~~~~~~~~~~~~#

def natural_year(dt_start, dt_end, dt_fmt_str=None,
                 method="pandas",
                 output_format="default",
                 return_date_only=False):
    
    """
    Calculate the natural year range based on the start and end dates.
    
    Parameters
    ----------
    dt_start : str, datetime.datetime, numpy.datetime64, pandas.Timestamp, time.struct_time
        The starting date of the period.
    dt_end : str, datetime.datetime, numpy.datetime64, pandas.Timestamp, time.struct_time
        The ending date of the period.
    dt_fmt_str : str, optional
        The format string for parsing dates if dt_start or dt_end are strings.
    method : str, optional
        The method for converting the date objects. Supported values are:
        "datetime", "timestamp", "datetime64", "arrow", "str".
        Default is "datetime".
    output_format : str, optional
        The format of the output. Supported options are "default", "string", and "tuple".
        "default" returns datetime objects, "string" returns formatted date strings, and
        "tuple" returns tuples of date components.
    return_date_only : bool, optional
        If True, only the date part of the datetime objects will be returned.
    
    Returns
    -------
    object
        The start and end of the natural year,
        after performing the specified operation, formatted based on 'output_format'.
    
    Raises
    ------
    ValueError
        If the output_format is not supported.
    TypeError
        - If the return_date_only parameter is not a boolean.
        - If dt_start or dt_end are not in a supported format.
    """
    
    # Argument adecuacy controls #
    #·#·#·#·#·#·#·#·#·#·#·#·#·#·#·
    
    # Output format parameter control #
    arg_iterable_output_format = (output_format, TIME_OUTPUT_FORMAT_OPTIONS)
    _validate_option(arg_iterable_output_format, ValueError, INVALID_OUTPUT_FORMAT_TEMPLATE)
    
    # Date-only return option #
    param_keys = get_caller_args()
    return_date_arg_pos = find_substring_index(param_keys, "return_date_only")
    if not isinstance(return_date_only, bool):
        raise TypeError(f"Parameter '{param_keys[return_date_arg_pos]}' "
                        "must be a boolean.")
    

    # Program progression #
    #·#·#·#·#·#·#·#·#·#·#·#
    
    # Convert input objects to datetime objects #
    #############################################
    
    dt_start_std = datetime_obj_converter(dt_start, method, dt_fmt_str=dt_fmt_str)
    dt_end_std = datetime_obj_converter(dt_end, method, dt_fmt_str=dt_fmt_str)       

    # Check if there is at least a whole year gap between the two objects #  
    #######################################################################
    
    min_one_year_gap = _has_at_least_one_year_gap(dt_start_std, dt_end_std)
    
    # If so, adjust the starting datetime object so that its day is 1
    # and sum a whole year to it in order to obtain the end datetime
    if min_one_year_gap:
        dt_start_natural = \
        datetime.datetime(dt_start_std.year, dt_start_std.month, 1,
                          dt_start_std.hour, dt_start_std.minute, dt_start_std.second)
        dt_end_natural = dt_start_natural + pd.DateOffset(years=1, days=1)
        
    # Else, return the original edges #
    else:
        dt_start_natural = dt_start_std
        dt_end_natural = dt_end_std
        
        
    # Choose whether to return the date part of the time objects #
    ##############################################################
    if return_date_only:
        dt_start_natural = extract_dt_part(dt_start_std, part="date")
        dt_end_natural = extract_dt_part(dt_end_std, part="date")
        
    # Choose between returning the results as strings or datetime dt_objects #     
    #############################################################################
    if output_format == "default":
        return (dt_start_natural, dt_end_natural)
    elif output_format == "string":
        format_args_natural_year2 = (dt_start_std, dt_end_std)
        print_format_string(NATURAL_YEAR_RANGE_TABLE, format_args_natural_year2)
    elif output_format == "tuple" :
        if return_date_only:
            return ((dt_start_natural.year, dt_start_natural.month, dt_start_natural.day),
                    (dt_end_natural.year, dt_end_natural.month, dt_end_natural.day))
        else:
            return (
                (dt_start_natural.year,
                 dt_start_natural.month,
                 dt_start_natural.day,
                 dt_start_natural.hour,
                 dt_start_natural.minute,
                 dt_start_natural.second),
                (dt_end_natural.year,
                 dt_end_natural.month,
                 dt_end_natural.day,
                 dt_end_natural.hour,
                 dt_end_natural.minute,
                 dt_end_natural.second)
                )
    
    
def _has_at_least_one_year_gap(dt1, dt2):
    # Ensure dt1 is earlier than dt2 #
    if dt1 > dt2:
        dt1, dt2 = dt2, dt1

    # Calculate the difference in years #
    year_difference = dt2.year - dt1.year
    
    # Check if there is at least a whole year gap #
    if year_difference > 1:
        return True
    elif year_difference == 1:
        if (dt2.month > dt1.month) or (dt2.month == dt1.month and dt2.day >= dt1.day):
            return True
    
    return False
    

#--------------------------#
# Parameters and constants #
#--------------------------#

# Option lists #
#--------------#

# Valid option exceptions #
ERROR_CLASS_LIST = [TypeError, ValueError]

# Abbreviated mathematical operations #
BASIC_MATH_OPT_LIST = ["sum", "subtr"]

# Time object output formatting options #
TIME_OUTPUT_FORMAT_OPTIONS = ["default", "string", "time_only", "tuple"]
DATE_OUTPUT_FORMAT_OPTIONS = \
select_elements(TIME_OUTPUT_FORMAT_OPTIONS, [0,1,-1])

# Template strings #
#------------------#

# Error #
INVALID_OUTPUT_FORMAT_TEMPLATE = """Unsupported output format '{}'. Options are: {}"""
        
UNSUPPORTED_OBJ_TYPE_TEMPLATE1 = """Unsupported {} type. Supported types are:
    - string
    - datetime.datetime
    - datetime.{}
    - numpy.datetime64
    - pandas.Timestamp
    - time.struct_time
"""

UNSUPPORTED_OBJ_TYPE_TEMPLATE2 = """Unsupported datetime type. Supported types are:
    - string
    - datetime.datetime
    - numpy.datetime64
    - pandas.Timestamp
    - time.struct_time
"""

INVALID_MATH_OPERATION_ERROR = \
f"Only sum and subtraction operation are supported: {BASIC_MATH_OPT_LIST}"
TOO_FEW_ARG_ERROR_TEMPLATE = \
"At least two {} or datetime objects are required to perform the addition."

# Informative #
NATURAL_YEAR_RANGE_TABLE = \
"""
{} -- {}

|
|
v

{dt_start_natural} -- {dt_end_natural}
"""

# Switch case dictionaries #
#--------------------------#

OPERATION_DICT = {
    BASIC_MATH_OPT_LIST[0] : np.sum,
    BASIC_MATH_OPT_LIST[1] : lambda tds: tds[0] - np.sum(tds[1:])
}

TIME_OUTPUT_FORMAT_DICT = {
    TIME_OUTPUT_FORMAT_OPTIONS[0] : lambda t_obj: t_obj,
    TIME_OUTPUT_FORMAT_OPTIONS[1] : lambda t_obj: str(t_obj),
    TIME_OUTPUT_FORMAT_OPTIONS[2] : lambda t_obj: t_obj.time(),
    TIME_OUTPUT_FORMAT_OPTIONS[3] : lambda t_obj: (t_obj.days,
                                                   t_obj.hours, 
                                                   t_obj.minutes, 
                                                   t_obj.seconds)
}

DATE_OUTPUT_FORMAT_DICT = {
    DATE_OUTPUT_FORMAT_OPTIONS[0] : lambda d_obj: d_obj,
    DATE_OUTPUT_FORMAT_OPTIONS[1] : lambda d_obj: str(d_obj),
    DATE_OUTPUT_FORMAT_OPTIONS[2] : lambda d_obj: (d_obj.year,
                                                   d_obj.month, 
                                                   d_obj.day)
}

DATETIME_OBJECT_PART_DICT = {
    "time" : lambda dt_start_std, arg_list : dt_start_std.time() if arg_list is None else dt_start_std.time(*arg_list),
    "date" : lambda dt_start_std, arg_list : dt_start_std.date() if arg_list is None else dt_start_std.date(*arg_list)
}
