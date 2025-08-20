#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

# Standard modules #
import time
from datetime import datetime, timedelta

# Third-party modules #
import numpy as np
import pandas as pd
from dateutil.parser import parse

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_func_name, get_type_str
from paramlib.global_parameters import (
    NUMPY_DATE_UNIT_LIST,
    PANDAS_DATE_UNIT_LIST,
    UNIT_FACTOR_DICT
)
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.strings.text_formatters import format_string
from pygenutils.time_handling.time_utils import (
    get_datetime_object_unit,
    get_nano_datetime,
)

#------------------#
# Define functions #
#------------------#

# %% INPUT VALIDATION STREAMLINERS

def _validate_option(explanation, option, allowed_options):
    """
    Validate if the given option is within the list of allowed options.

    Parameters
    ----------
    explanation : str
        A brief description or context of the validation.
    option : object
        The option to be validated.
    allowed_options : list/iterable
        A list or iterable of valid options.

    Raises
    ------
    ValueError: 
        If the option is not in the list of allowed options, with a detailed explanation.
    """
    if option not in allowed_options:
        raise ValueError(f"{explanation} '{option}' not supported for this operation. "
                         f"Choose one from {allowed_options}.")

def _validate_precision(frac_precision, option, min_prec=0, max_prec=9):
    """
    Validate the precision level for a floating-point number and ensure it is within a valid range.
    
    Parameters
    ----------
    frac_precision : int or None
        The desired fractional precision to validate.
    option : str
        Specifies the type of object or library (e.g., "pandas") that supports higher precision.
    min_prec : int, optional
        The minimum allowed precision. Default is 0.
    max_prec : int, optional
        The maximum allowed precision. Default is 9.
    
    Raises
    ------
    ValueError
        If `frac_precision` is outside the range [min_prec, max_prec] or
        `frac_precision` is greater than or equal to 7 but `option` is not "pandas".
    """
    if ((frac_precision is not None) and not (min_prec <= frac_precision <= max_prec)):
        raise ValueError(f"Fractional precision must be between {min_prec} and {max_prec}.")
    if ((7 <= frac_precision <= max_prec) and option != "pandas"):
        raise ValueError(f"Only option 'pandas' supports precision={frac_precision}.")
        
def _validate_unit(unit, module):
    """
    Validates the date unit based on the module.

    Parameters
    ----------
    unit : str
        Time unit for the floated time. 
        Only applicable if the module is 'numpy' or 'pandas'.
    module : {"numpy", "pandas"}
        The module used for parsing the floated time.

    Raises
    ------
    ValueError
        If `unit` is not supported for the specified `module`.
    """
    
    # Define allowed date units for each module    
    if module == "numpy" and unit not in NUMPY_DATE_UNIT_LIST:
        raise ValueError("Unsupported date unit for numpy.datetime64 objects. "
                         f"Choose one from {NUMPY_DATE_UNIT_LIST}.")
        
    if module == "pandas" and unit not in PANDAS_DATE_UNIT_LIST:
        raise ValueError("Unsupported date unit for pandas.Timestamp objects. "
                         f"Choose one from {PANDAS_DATE_UNIT_LIST}.")

# %% UTILITY FUNCTIONS

def _arrow_get_with_import(*args, **kwargs):
    """
    Helper function to import arrow and call arrow.get() with lazy import.
    
    Parameters
    ----------
    *args : Any
        Arguments to pass to arrow.get()
    **kwargs : Any
        Keyword arguments to pass to arrow.get()
    
    Returns
    -------
    arrow.Arrow
        The result of arrow.get(*args, **kwargs)
    
    Raises
    ------
    ImportError
        If arrow package is not installed
    """
    try:
        import arrow
    except ImportError:
        raise ImportError("arrow package is required for arrow operations. Install with: pip install arrow")
    
    return arrow.get(*args, **kwargs)

# %% SIMPLE DATA PARSING

# Input format: str #
#-------------------#

def parse_dt_string(datetime_str, dt_fmt_str=None, module="datetime", unit="ns", dayfirst=False, yearfirst=False):
    """
    Convert a time string or object to a date/time object using a specified library.
    
    Parameters
    ----------
    datetime_str : str | object
        A string representing the date and/or time.
        If ``module="pandas"``, this can also be:
            - Python datetime objects
            - NumPy datetime64 objects
            - Integer/float timestamps
            - Series objects
            - DataFrame columns
            - Lists or arrays of timestamps
    dt_fmt_str : str | None
        A format string that defines the structure of `datetime_str`. 
        Must follow the format required by the chosen module.
        If None and module is 'pandas', pandas will try to infer the format.
        If empty and module is 'pandas' with a numeric timestamp, it will use the unit parameter.
    module : {"datetime", "dateutil", "pandas", "numpy", "arrow"}, default 'datetime'
        Specifies the library used for conversion.
        If 'numpy', datetime_str must be in ISO 8601 date or datetime format.
    unit : str, optional
        Applies only if ``module`` is either 'numpy' or 'pandas'.
        Denotes which unit ``floated_time`` is expressed in.
        
        For Pandas, allowed units are {'D', 's', 'ms', 'us', 'ns'}.
        For NumPy, allowed units are {'Y', 'M', 'D', 'h', 'm', 's' , 'ms', 'us', 'ns'}.
       
        According the standards, this parameter defaults to 'ns' for Pandas 
        and 'us' for NumPy.
        Then, in order to maintain compatibility, the largest common time unit 'us'
        has been defined as default in this function.
    dayfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
        Only applies when module is 'pandas'.
    yearfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).
        Only applies when module is 'pandas'.
    
    Returns
    -------
    datetime_obj : object
        The converted date/time object, as per the chosen module.
    
    Raises
    ------
    ValueError
        - If the module is not supported
        - If no time string is provided or if it does not match the provided format.
    """
    
    # Input validation #
    #-#-#-#-#-#-#-#-#-#-
    
    # Module #
    allowed_modules = list(TIME_STR_PARSING_DICT.keys())
    _validate_option("Module", module, allowed_modules)
    
    # Formatting string #
    if dt_fmt_str is None and module != "pandas":
        raise ValueError("A datetime format string must be provided for non-pandas modules.")
        
    # Time string parsing #
    #-#-#-#-#-#-#-#-#-#-#-#
    
    try:
        parse_func = TIME_STR_PARSING_DICT.get(module)
        
        # Special handling for pandas module
        if module == "pandas":
            # If datetime_str is a string and looks like a numeric timestamp, use unit
            if isinstance(datetime_str, str) and (datetime_str.isdigit() or (datetime_str.replace('.', '', 1).isdigit() and datetime_str.count('.') <= 1)):
                datetime_obj = pd.to_datetime(datetime_str, unit=unit, dayfirst=dayfirst, yearfirst=yearfirst)
            else:
                # Otherwise use format if provided, or let pandas infer the format
                if dt_fmt_str is None:
                    datetime_obj = pd.to_datetime(datetime_str, dayfirst=dayfirst, yearfirst=yearfirst)
                else:
                    datetime_obj = parse_func(datetime_str, dt_fmt_str, unit, dayfirst, yearfirst)
        else:
            # For other modules, use the parse_func as defined
            datetime_obj = parse_func(datetime_str, dt_fmt_str, unit) if module == "numpy" else parse_func(datetime_str, dt_fmt_str)
    except ValueError as e:
        raise ValueError(f"The time string does not match the format string provided: {str(e)}")
    else:
        return datetime_obj
    
# %% 

# Input format: int, float #
#--------------------------#

# Main function #
#~~~~~~~~~~~~~~~#

def parse_float_dt(datetime_float, 
                   frac_precision=None,
                   origin="unix", 
                   unit="us", 
                   dt_fmt_str=None, 
                   module="datetime",
                   dayfirst=False,
                   yearfirst=False):
    """
    Converts an integer or float time to a date/time object.
    It also converts to a string representation if requested.
    
    datetime_float : int or float
        Time representing a time unit relative to an origin.
    frac_precision : int [0,9] or None 
        Precision of the fractional part of the seconds.
        If not None, this part is rounded to the desired number of decimals,
        which must be between 0 and 9. For decimals in [7,9], nanoscale
        datetime is generated, supported only by 'pandas'.
        Raises a ValueError if 7 <= frac_precision <= 9 and module is not 'pandas'.        
        Defaults to None, i.e., the original precision is used.
    origin : {"arbitrary", "unix"}, default 'unix'
        Determines whether to compute time relative to an arbitrary origin 
        or to the Unix epoch start (1970-01-01 00:00:00).
        For example, the elapsed time for a program to execute has its origin at 
        the moment of execution, whereas for clock times, seconds are counted 
        from the epoch time.
    unit : str, optional
        Applies only if ``origin='unix'`` and ``convert_to={'numpy', 'pandas'}``.
        Denotes which unit ``datetime_str`` is expressed in. 
        
        For Pandas, allowed units are {'D', 's', 'ms', 'us', 'ns'}.
        For NumPy, allowed units are {'Y', 'M', 'D', 'h', 'm', 's', 'ms', 'us', 'ns'}.
        Defaults to 'ns' for Pandas and 'us' for NumPy.
    dt_fmt_str : str
        Format string to convert the date/time object to a string.
    module : {"datetime", "time", "pandas", "numpy", "arrow", "str"}, default 'datetime'.
         The module or class used to parse the floated time. 
         If 'numpy', datetime_float represents an offset from the Unix epoch start.
    dayfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
        Only applies when module is 'pandas'.
    yearfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).
        Only applies when module is 'pandas'.
      
    Returns
    -------
    object
        The converted date/time object or string representation.
    
    Raises
    ------
    ValueError
        If parameters are invalid or the conversion fails.
    """        
    
    # Input validation #
    #-#-#-#-#-#-#-#-#-#-
    
    # Module #
    allowed_modules = ["str"] + list(FLOATED_TIME_PARSING_DICT.keys())
    _validate_option("Object type conversion", module, allowed_modules)
    
    # Time formatting string #
    if module == "str" and not dt_fmt_str:
        raise ValueError("You must provide a formatting string.")

    # Fractional second precision #
    _validate_precision(frac_precision, module)

    # Date unit #
    _validate_unit(unit, module)

    # Floated time parsing #
    #-#-#-#-#-#-#-#-#-#-#-#-

    if module == "str":
        return _parse_float_to_string(datetime_float,
                                      frac_precision, 
                                      origin,
                                      dt_fmt_str,
                                      unit,
                                      module,
                                      dayfirst,
                                      yearfirst)
    else:
        return _float_dt_parser(datetime_float, module, unit, dayfirst, yearfirst)
    
    
# Auxiliary functions #
#~~~~~~~~~~~~~~~~~~~~~#

def _parse_float_to_string(floated_time, 
                           frac_precision, 
                           origin, 
                           dt_fmt_str, 
                           unit,
                           module,
                           dayfirst,
                           yearfirst):
    """        
    Converts a floated time to its string representation.

    Parameters
    ----------
    floated_time : int or float
        Time in seconds representing a time unit relative to an origin.
    frac_precision : int [0,9] or None
        Precision of the fractional seconds.
        Only supported by 'pandas' for high precision.
    origin : {"arbitrary", "unix"}
        Origin of the time measurement.
    dt_fmt_str : str
        Format string for the string representation.
    unit : str, optional
        Time unit for `floated_time` if `origin='unix'` and `module` in {'numpy', 'pandas'}.
    module : {"datetime", "time", "pandas", "numpy", "arrow"}
        Module used for parsing.
    dayfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
        Only applies when module is 'pandas'.
    yearfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).
        Only applies when module is 'pandas'.

    Returns
    -------
    str
        The formatted string representation of the floated time.
    """
    
    if origin == "arbitrary":
        return _format_arbitrary_dt(floated_time, frac_precision)
       
    elif origin == "unix":
        # Accommodation of the fractional second #
        if frac_precision is not None:
            if frac_precision <= 6:
                dt_seconds = round(floated_time)
                dt_obj = _float_dt_parser(dt_seconds, module, unit, dayfirst, yearfirst)
                dt_str = dt_obj.strftime(dt_fmt_str)
            elif 7 <= frac_precision <= 9:
                return get_nano_datetime(floated_time, module)
        # Keep the original precision #
        else:
            dt_str = _float_dt_parser(floated_time, module, unit, dayfirst, yearfirst).strftime(dt_fmt_str)
    
        return dt_str  

    
def _float_dt_parser(floated_time, module, unit, dayfirst, yearfirst):
    """
    Parses a floated time into a date/time object.
    
    Parameters
    ----------
    floated_time : int or float
        Time representing a time unit relative to an origin.
    module : {"datetime", "time", "pandas", "numpy", "arrow"}
        Module used for parsing.
    unit : str, optional
        Time unit for `floated_time` if `module` in {'numpy', 'pandas'}.
    dayfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
        Only applies when module is 'pandas'.
    yearfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).
        Only applies when module is 'pandas'.
    
    Returns
    -------
    datetime_obj : object
        The parsed date/time object.
    """
    
    # Input validation #
    #-#-#-#-#-#-#-#-#-#-
    
    # Module #
    allowed_modules = list(FLOATED_TIME_PARSING_DICT.keys())
    _validate_option("Object type conversion", module, allowed_modules)

    # Date unit #
    _validate_unit(unit, module)
    
    # Calculate datetime object #
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    datetime_obj = FLOATED_TIME_PARSING_DICT.get(module)(floated_time, unit, dayfirst, yearfirst)
    return datetime_obj


def _format_arbitrary_dt(floated_time, frac_precision):
    """
    Formats an arbitrary time into a string representation
    based on the provided format.
    
    Parameters
    ----------
    floated_time : int or float
        Time in seconds representing a time unit relative to an arbitrary origin.
    frac_precision : int [0,6] or None
        Precision of the fractional seconds.
        This parameter is originally set in 'parse_float_dt' function,
        which allows integers in [0,9], because for 6 < frac_precision <=9 
        it performs optional nanoscale time computing, unlike this internal function.
        So in order to maintain organisation, the upper bound for the precision
        will be 6.
    
    Returns
    -------
    str
        The formatted time string.
    
    Raises
    ------
    ValueError
        If the format string is invalid or not supported.
        
    Notes
    -----
    Negative times or hours over 24 represent seconds matching 
    the next day's midnight. If so, set the hour to zero instead of 24.
    """

    # Compute time components #
    days, hours = divmod(floated_time // 3600, 24)
    minutes, seconds = divmod(floated_time % 3600, 60)
    
    # Maintain precisions higher than 6 in the upper bound #
    if frac_precision > 6:
        frac_precision = 6
        
    seconds = round(seconds, frac_precision)
   
    # Format time parts #
    try:
        if days > 0:
            time_tuple = (days, hours, minutes, seconds)
            time_parts_formatted = format_string(_TIME_STR_PARTS_TEMPLATES[0], time_tuple)
        elif hours > 0:
            time_tuple = (hours, minutes, seconds)
            time_parts_formatted = format_string(_TIME_STR_PARTS_TEMPLATES[1], time_tuple)
        elif minutes > 0:
            time_tuple = (minutes, seconds)
            time_parts_formatted = format_string(_TIME_STR_PARTS_TEMPLATES[2], time_tuple)
        else:
            time_tuple = (seconds,)
            time_parts_formatted = format_string(_TIME_STR_PARTS_TEMPLATES[3], time_tuple)
    except (KeyError, IndexError, ValueError) as e:
        raise ValueError(f"Invalid format string or time components: {e}")
    return time_parts_formatted 
        

# %% PARSING AMONG COMPLEX DATA OBJECTS

# Main functions #
#----------------#

# All except 'float' #
#~~~~~~~~~~~~~~~~~~~~#

def dt_obj_converter(datetime_obj,
                     convert_to,
                     unit="s",
                     float_class="d", 
                     int_class="int",
                     dt_fmt_str=None,
                     dayfirst=False,
                     yearfirst=False):

    """
    Convert a date/time object to another, including float and string representation.
    If float, it represents seconds since the Unix epoch.
    
    Parameters
    ----------
    datetime_obj : object
        The date/time object to be converted.
        Accepted objects by library are:
        - datetime : `datetime.datetime`, 
        - time : `datetime.time`, 
        - numpy : `np.datetime64`, `np.ndarray`,
        - pandas : `pd.Timestamp`, `pd.DataFrame`, `pd.Series`
        - arrow : `arrow`, 
        - struct_time : `time.struct_time`
        
    convert_to : str
        The target type to convert `datetime_obj` to.
        Accepted values depend on the input type.
        For example, if `datetime_obj` is a `datetime`, `convert_to` could be
        `datetime64`, `Timestamp`, etc.
    unit : str
        The date unit for conversion, applicable to certain types.
        Default is `"s"` (seconds).
    float_class : str | numpy float class
        The float precision class. Default is `"d"` (double precision).
    int_class : str | numpy int class
        The integer precision class. Default is `"int"` (signed integer type).
    dt_fmt_str : str
        Format string to convert the date/time object to a string.
    dayfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
        Only applies when converting to pandas objects.
    yearfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).
        Only applies when converting to pandas objects.

    Returns
    -------
    The converted date/time object in the format/type specified by `convert_to`.

    Raises
    ------
    ValueError
        If `convert_to` is not a valid target type for the given `datetime_obj`.
    RuntimeError
        If there is an error during the conversion process.
        
    Conversion Options:   
    +------------------+---------+--------------+---------------+------------+--------------+---------+-------+
    |    Input Type    | `float` | `datetime`   | `struct_time` | `Timestamp`| `datetime64` | `arrow` | `str` |
    +------------------+---------+--------------+---------------+------------+--------------+---------+-------+
    | `datetime`       | Yes     | Yes          | Yes           | Yes        | Yes          | Yes     | Yes   |
    | `datetime64`     | Yes     | Yes          | Yes           | Yes        | No           | Yes     | Yes   |
    | `time`           | Yes     | Yes          | Yes           | Yes        | Yes          | Yes     | Yes   |
    | `Timestamp`      | Yes     | Yes          | Yes           | No         | Yes          | Yes     | Yes   |
    | `arrow`          | Yes     | Yes          | Yes           | Yes        | Yes          | No      | Yes   |
    | `struct_time`    | Yes     | Yes          | No            | Yes        | Yes          | Yes     | No    |
    | `DataFrame`      | Yes     | Yes          | No            | No         | No           | No      | Yes   |
    | `Series`         | Yes     | Yes          | No            | No         | No           | No      | Yes   |
    | `ndarray`        | Yes     | Yes          | No            | No         | No           | No      | Yes   |
    +------------------+---------+--------------+---------------+------------+--------------+---------+-------+

    Notes
    -----
    - "Yes" in above table indicates that the conversion from the input type
      to the specified type is supported.
    - If the input object is whichever of types [`DataFrame`, `Series`, `ndarray`]
      and ``convert_to={'float', 'str'``}, the resulting object type will also be array-like,
      but an attempt will be made to convert its all values accordingly.
    """

    # Input validation #
    #-#-#-#-#-#-#-#-#-#-
    
    # Object type to convert to #
    if not convert_to:
        raise ValueError("Argument 'convert_to' not provided.")
        
    # Helper function to perform conversion and handle exceptions
    def perform_conversion(conversion_dict, obj, **kwargs):
        try:
            return conversion_dict.get(convert_to)(
                obj,
                kwargs.get("unit"),
                kwargs.get("float_class"),
                kwargs.get("int_class"),
                kwargs.get("dt_fmt_str"),
                kwargs.get("dayfirst"),
                kwargs.get("yearfirst"),
            )
        except Exception as err:
            raise RuntimeError(f"Error during conversion to '{convert_to}': {err}")
              
    # Date unit factor #
    allowed_factors = list(UNIT_FACTOR_DICT.keys())
    _validate_option("Time unit factor", unit, allowed_factors)
            
    # Numpy precision classes #
    _validate_option("Numpy float precision class", float_class, _FLOAT_CLASS_LIST)
    _validate_option("Numpy integer precision class", int_class, _INT_CLASS_LIST)
    
    # Program progression #
    #-#-#-#-#-#-#-#-#-#-#-#
    
    # Get the object type's name #
    obj_type = get_type_str(datetime_obj, lowercase=True)    
    
    # Validate here the type to convert to, according the input data type # 
    _validate_option(f"Object type conversion for object type '{obj_type}' where", 
                     convert_to, 
                     list(CONVERSION_OPT_DICT[obj_type].keys()))
    
    # Perform the conversion # 
    conversion_dict = CONVERSION_OPT_DICT[obj_type]
    return perform_conversion(conversion_dict, datetime_obj, unit=unit, 
                              float_class=float_class, int_class=int_class,
                              dt_fmt_str=dt_fmt_str, dayfirst=dayfirst, yearfirst=yearfirst)
    
        
# Auxiliary functions #
#---------------------#

# Exclusively to 'float' #
#~~~~~~~~~~~~~~~~~~~~~~~~#

# Scalar complex data #
#-#-#-#-#-#-#-#-#-#-#-#

def _total_dt_unit(datetime_obj, unit, float_class=None, int_class=None):
    """
    Convert a datetime object into total time based on the specified unit
    (e.g., seconds, microseconds, nanoseconds).
    
    Parameters
    ----------
    datetime_obj : object
        The datetime object to be converted. Can be of various types
        (e.g., `datetime`, `datetime64`, `Timestamp`).
    unit : str 
        The time unit for conversion (e.g., "seconds", "microseconds", "nanoseconds"). 
        The actual unit factors are provided by the `unit_factor_dict`.
    float_class : str | numpy float class
        Specifies the precision class to use for floating-point results.
    int_class : str | numpy int class
        Specifies the precision class to use for integer results.
    
    Returns
    -------
    The total time in the specified unit, converted based on the object's type.
    
    Raises
    ------
    ValueError: 
        If the object type is unsupported for conversion.
    RuntimeError: 
        If an error occurs during the conversion process.
    """
    # Input validation #
    ####################
    
    # Current function name #
    current_function = get_func_name()
    
    # Program progression #
    #######################
    
    unit_factor = UNIT_FACTOR_DICT.get(unit)
    obj_type = get_type_str(datetime_obj, lowercase=True)    
    try:
        conversion_func = _TOTAL_TIME_UNIT_DICT.get(obj_type)
        if conversion_func is None:
            raise ValueError(f"Unsupported object type, function '{current_function}': {obj_type}")
        return conversion_func(datetime_obj, unit, float_class, int_class, unit_factor)
    except Exception as err:
        raise RuntimeError(f"Error in conversion process, function '{current_function}': {err}")
        
        
# Array-like complex data #
def _total_dt_complex_data(datetime_obj, int_class, unit_factor):
    """
    Calculate total time in a given unit for complex data types,
    such as Series and DataFrames, by converting all values to float.

    Parameters
    ----------
    datetime_obj : pandas.{DataFrame, Series}
        The complex data object to be processed.
    int_class : str
        Specifies the precision class to use for integer results.
    unit_factor : str
        The factor by which to multiply the converted values to get the
        total time in the specified unit.

    Returns
    -------
    pd.Series or pd.DataFrame
        The input data object with all values converted to total time in the specified unit.

    Raises
    ------
    RuntimeError: 
        If an error occurs during the conversion process for
        `Series` or `DataFrame` type objects.
    """
    # Input validation #
    current_function = get_func_name()
    
    # Operations #
    dt_obj_aux = datetime_obj.copy()
    
    if isinstance(datetime_obj, pd.Series):
        try:
            return dt_obj_aux.astype(int_class) * unit_factor
        except (ValueError, Exception) as err:
            raise RuntimeError(f"Error in '{current_function}' function "
                               f"for 'Series' type object:\n{err}.")

    elif isinstance(datetime_obj, pd.DataFrame):
        try:
            for col in datetime_obj.columns:
                try:
                    dt_obj_aux[col] = dt_obj_aux[col].astype(int_class) * unit_factor
                except ValueError:
                    pass
            return dt_obj_aux
        except Exception as err:
            raise RuntimeError(f"Error in '{current_function}' function "
                               f"for 'DataFrame' type object:\n{err}.")


# Timezone aware information #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def _tzinfo_remover(dt_obj):
    """
    Remove timezone information from a datetime object if present.

    Parameters
    ----------
    dt_obj : datetime-like
        The datetime object from which timezone information should be removed.

    Returns
    -------
    datetime-like
        The datetime object without timezone information.
    """
    if hasattr(dt_obj, "tzinfo"):
        return dt_obj.replace(tzinfo=None)
    else:
        return dt_obj
    

# Conversions among different complex data #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def _to_string(dt_obj, unit, dt_fmt_str):
    """
    Converts a datetime-like object to its string representation. 
    Handles various datetime types including pd.DataFrame, pd.Series, 
    np.ndarray, np.datetime64, and datetime.datetime.

    Parameters
    ----------
    dt_obj : datetime-like
        The datetime object to be converted.
    dt_fmt_str : str
        Format string for the string representation.
    unit : str, optional
        Time unit for np.datetime64 conversion if applicable.

    Returns
    -------
    str | pd.DataFrame | pd.Series
        The string representation, or object with string values.
    """
    
    # Handle individual scalar datetime objects
    if hasattr(dt_obj, "strftime"):
        return dt_obj.strftime(dt_fmt_str)

    # Handle np.datetime64 objects
    if isinstance(dt_obj, np.datetime64):
        dt_obj = _to_datetime_aux(dt_obj, unit)
        return dt_obj.strftime(dt_fmt_str)

    # Handle np.ndarray with datetime-like objects
    if isinstance(dt_obj, np.ndarray):
        try:
            dt_obj = np.vectorize(lambda x: _to_datetime_aux(x, unit).strftime(dt_fmt_str))(dt_obj)
        except Exception as e:
            raise ValueError(f"Error in converting np.ndarray to string: {e}")
        return dt_obj

    # Handle pd.Series
    if isinstance(dt_obj, pd.Series):
        try:
            return dt_obj.apply(lambda dfs_col: dfs_col.strftime(dt_fmt_str)
                                if hasattr(dfs_col, 'strftime') else str(dfs_col))
        except Exception as e:
            raise ValueError(f"Error in converting pd.Series to string: {e}")

    # Handle pd.DataFrame
    if isinstance(dt_obj, pd.DataFrame):
        try:
            return dt_obj.map(lambda df_col: df_col.strftime(dt_fmt_str)
                              if hasattr(df_col, 'strftime') else str(df_col))
        except Exception as e:
            raise ValueError(f"Error in converting pd.DataFrame to string: {e}")

    # Default case
    else:
        return str(dt_obj)


def _to_float(dt_obj, unit=None, float_class=None):
    """
    Convert a datetime object to a float representing the total time in the specified unit.

    Parameters
    ----------
    dt_obj : datetime-like
        The datetime object to be converted.
    unit : str
        The unit for conversion (e.g., "s" for seconds, "ms" for milliseconds).
    float_class : str | numpy float class, optional
        The precision class for the float result.

    Returns
    -------
    float
        The converted value in the specified unit.
    """
    obj_type = get_type_str(dt_obj, lowercase=True)
    if obj_type == "datetime64":
        return dt_obj.astype(f"timedelta64[{unit}]").astype(float_class) if unit and float_class else dt_obj.astype(float)
    elif obj_type == "time": # datetime.time
        return __time_component_to_float(dt_obj)
    if hasattr(dt_obj, 'timestamp'):
        return dt_obj.timestamp()  # works for datetime and pandas
    return float(dt_obj.float_timestamp)  # arrow


def __time_component_to_float(t):
    """
    Convert a time object to seconds since Unix epoch start.

    Parameters
    ----------
    t : datetime.time
        The time object to be converted.

    Returns
    -------
    time_component_float : int
        Seconds relative to the Unix epoch.
    """
    time_component_float = timedelta(hours=t.hour,
                                     minutes=t.minute, 
                                     seconds=t.second,
                                     microseconds=t.microsecond)
    return time_component_float.total_seconds()


def _to_datetime(dt_obj, unit=None):
    """
    Convert a given datetime-like object or each value in DataFrame/Series to a 
    standard Python datetime object.

    Parameters
    ----------
    dt_obj : datetime-like, pd.DataFrame, or pd.Series
        The object or DataFrame/Series to be converted to a Python datetime object.
    unit : str
        The unit for conversion (e.g., "ns" for nanoseconds).

    Returns
    -------
    datetime, pd.DataFrame, or pd.Series
        The converted Python datetime object, DataFrame, or Series.
        
    Note
    ----
    For datetime.time objects a datetime.datetime object is returned.
    Since the date is arbitrary, then to maintain some organisation,
    the current date will be placed in its date part.
    """
    obj_type = get_type_str(dt_obj, lowercase=True)
    
    # Array-like with datetime-like values
    if obj_type == "dataframe":
        return dt_obj.map(lambda df_col: _to_datetime_aux(df_col, unit))
    elif obj_type == "time":
        current_date = datetime.today().date()
        return datetime(current_date.year, current_date.month, current_date.day,
                        dt_obj.hour, dt_obj.minute, dt_obj.second, dt_obj.microsecond)
        
    elif obj_type == "series":
        return dt_obj.apply(lambda df_col: _to_datetime_aux(df_col, unit))
    
    # Handle scalar values
    else:
        if obj_type == "datetime64":
            # If unit is 'ns' (nanoseconds), use the auxiliary conversion function
            unit = unit or get_datetime_object_unit(dt_obj)
            if unit == "ns":
                return _to_datetime_aux(dt_obj, unit)
            else:
                return dt_obj.astype(datetime)
        if obj_type == "timestamp":
            return dt_obj.to_pydatetime()
        if hasattr(dt_obj, 'fromtimestamp'):
            return dt_obj.fromtimestamp(dt_obj.float_timestamp)  # arrow
        return datetime(*dt_obj[:6])  # time.struct_time

    
def _to_datetime_aux(dt_obj, unit):
    """
    Convert np.datetime64 to Python datetime using pandas.

    Parameters
    ----------
    dt_obj : np.datetime64
        The numpy datetime object to be converted.
    unit : str
        The unit for conversion (e.g., "ns" for nanoseconds).

    Returns
    -------
    datetime
        The converted Python datetime object.
    """
    return pd.to_datetime(dt_obj, unit=unit).to_pydatetime()


def _to_time_struct(dt_obj, unit=None):
    """
    Convert a datetime-like object to a time.struct_time object.

    Parameters
    ----------
    dt_obj : datetime-like
        The object to be converted to time.struct_time.
    unit : str, optional
        The unit for conversion (if needed).

    Returns
    -------
    time.struct_time
        The converted time.struct_time object.
    """
    return _to_datetime(dt_obj, unit).timetuple()

def _to_pandas(dt_obj, unit, dayfirst=False, yearfirst=False):
    """
    Convert a datetime-like object to a pandas Timestamp object with the specified unit.

    Parameters
    ----------
    dt_obj : datetime-like
        The object to be converted to a pandas Timestamp.
    unit : str, optional
        The unit for conversion.
    dayfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True, parses dates with the day first, e.g. "10/11/12" is parsed as 2012-11-10.
    yearfirst : bool, default False
        Specify a date parse order if datetime_str is str or is list-like.
        If True parses dates with the year first, e.g. "10/11/12" is parsed as 2010-11-12.
        If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).

    Returns
    -------
    pd.Timestamp
        The converted pandas Timestamp object.
    """
    return pd.to_datetime(_to_datetime(dt_obj), unit=unit, dayfirst=dayfirst, yearfirst=yearfirst)

def _to_numpy(dt_obj, unit=None):
    """
    Convert a datetime-like object to a NumPy datetime64 object with the specified unit.

    Parameters
    ----------
    dt_obj : datetime-like
        The object to be converted to a NumPy datetime64.
    unit : str, optional
        The unit for conversion (default is "ns" for nanoseconds).

    Returns
    -------
    np.datetime64
        The converted NumPy datetime64 object.
    """
    dt_obj = _to_datetime(dt_obj, unit)
    return np.datetime64(_tzinfo_remover(dt_obj), unit)

def _to_arrow(dt_obj):
    """
    Convert a datetime-like object to an Arrow object.

    Parameters
    ----------
    dt_obj : datetime-like
        The object to be converted to an Arrow object.

    Returns
    -------
    arrow.Arrow
        The converted Arrow object.
    """
    try:
        import arrow
    except ImportError:
        raise ImportError("arrow package is required for arrow conversion. Install with: pip install arrow")
    
    dt_obj = _to_datetime(dt_obj)
    return arrow.get(dt_obj)


# %% PARAMETERS AND CONSTANTS

# Precision classes for number integer or floating precision #
_FLOAT_CLASS_LIST = [np.float16, np.float32, "f", np.float64, "float", "d", np.float128]
_INT_CLASS_LIST = [np.int8, np.int16, "i", np.float32, "int", np.int64]

# Switch case dictionaries #
#--------------------------#

# Time parsing #
#~~~~~~~~~~~~~~#

# String #    
#-#-#-#-#-

TIME_STR_PARSING_DICT = {
    "datetime" : lambda datetime_str, dt_fmt_str: datetime.strptime(datetime_str, dt_fmt_str),
    "dateutil" : lambda datetime_str, dt_fmt_str: parse(datetime_str),
    "pandas"   : lambda datetime_str, dt_fmt_str, unit, dayfirst=False, yearfirst=False : pd.to_datetime(datetime_str, format=dt_fmt_str, dayfirst=dayfirst, yearfirst=yearfirst),
    "numpy"    : lambda datetime_str, _, unit : np.datetime64(datetime_str, unit),
    "arrow"    : lambda datetime_str, dt_fmt_str: _arrow_get_with_import(datetime_str, dt_fmt_str)
}

# Floated #
#-#-#-#-#-#

FLOATED_TIME_PARSING_DICT = {
    "datetime" : lambda floated_time, unit, dayfirst=False, yearfirst=False : datetime.fromtimestamp(floated_time),
    "time"     : lambda floated_time, unit, dayfirst=False, yearfirst=False : datetime(*tuple(time.localtime(floated_time))[:6]),
    "pandas"   : lambda floated_time, unit, dayfirst=False, yearfirst=False : pd.to_datetime(floated_time, unit=unit, dayfirst=dayfirst, yearfirst=yearfirst),
    "numpy"    : lambda floated_time, unit, dayfirst=False, yearfirst=False : np.datetime64(floated_time, unit),
    "arrow"    : lambda floated_time, unit, dayfirst=False, yearfirst=False : _arrow_get_with_import(floated_time)
}

# Complex data # 
#-#-#-#-#-#-#-#-

# To other objects #
DT_OBJ_CONVERSION_DICT = {
    "float"  : lambda dt_obj, _, __, ___, ____, _____, ______ : dt_obj.timestamp(),
    "time"   : lambda dt_obj, _, __, ___, ____, _____, ______ : dt_obj.timetuple(),
    "pandas" : lambda dt_obj, unit, __, ___, ____, dayfirst, yearfirst : _to_pandas(_tzinfo_remover(dt_obj), unit, dayfirst, yearfirst),
    "numpy"  : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_numpy(_tzinfo_remover(dt_obj), unit),
    "arrow"  : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_arrow(dt_obj),
    "str"    : lambda dt_obj, unit, __, ___, dt_fmt_str, _____, ______ : _to_string(dt_obj, unit, dt_fmt_str)
}

DT64_OBJ_CONVERSION_DICT = {
    "float"    : lambda dt_obj, unit, float_class, __, ___, _____, ______ : _to_float(dt_obj, unit, float_class),
    "datetime" : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_datetime(dt_obj, unit),
    "time"     : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_time_struct(dt_obj, unit),
    "pandas"   : lambda dt_obj, unit, __, ___, ____, dayfirst, yearfirst : _to_pandas(dt_obj, unit, dayfirst, yearfirst),
    "arrow"    : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_arrow(dt_obj),
    "str"      : lambda dt_obj, unit, __, ___, dt_fmt_str, _____, ______ : _to_string(_to_datetime(dt_obj), unit, dt_fmt_str)
}

DT_TIME_OBJ_CONVERSION_DICT = {
    "float"    : lambda dt_obj, unit, float_class, __, ___, _____, ______ : _to_float(dt_obj, unit, float_class),
    "datetime" : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_datetime(dt_obj, unit),
    "time"     : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_time_struct(dt_obj),
    "pandas"   : lambda dt_obj, unit, __, ___, ____, dayfirst, yearfirst : _to_pandas(_to_datetime(dt_obj), unit, dayfirst, yearfirst),
    "numpy"    : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_numpy(_to_datetime(dt_obj), unit),
    "arrow"    : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_arrow(dt_obj),
    "str"      : lambda dt_obj, unit, __, ___, dt_fmt_str, _____, ______ : _to_string(dt_obj, unit, dt_fmt_str)
}

TIMESTAMP_OBJ_CONVERSION_DICT = {
    "float"    : lambda dt_obj, unit, float_class, __, ___, _____, ______ : _to_float(dt_obj, unit, float_class),
    "datetime" : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_datetime(dt_obj, unit),
    "time"     : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_time_struct(dt_obj),
    "numpy"    : lambda dt_obj, _, __, ___, ____, _____, ______ : dt_obj.to_numpy(),
    "arrow"    : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_arrow(dt_obj),
    "str"      : lambda dt_obj, unit, __, ___, dt_fmt_str, _____, ______ : _to_string(dt_obj, unit, dt_fmt_str)
}

ARROW_OBJ_CONVERSION_DICT = {
    "float"    : lambda dt_obj, unit, float_class, __, ___, _____, ______ : _to_float(dt_obj, unit, float_class),
    "datetime" : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_datetime(dt_obj, unit),
    "time"     : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_time_struct(dt_obj),
    "pandas"   : lambda dt_obj, unit, __, ___, ____, dayfirst, yearfirst : _to_pandas(dt_obj, unit, dayfirst, yearfirst),
    "numpy"    : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_numpy(dt_obj, unit),
    "str"      : lambda dt_obj, unit, __, ___, dt_fmt_str, _____, ______ : _to_string(dt_obj, unit, dt_fmt_str)
}

TIME_STT_OBJ_CONVERSION_DICT = {
    "float"    : lambda dt_obj, unit, float_class, __, ___, _____, ______ : _to_float(dt_obj, unit, float_class),
    "datetime" : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_datetime(dt_obj, unit),
    "pandas"   : lambda dt_obj, unit, __, ___, ____, _____, ______ : pd.Timestamp(*dt_obj[:6], unit=unit),
    "numpy"    : lambda dt_obj, unit, __, ___, ____, _____, ______ : np.datetime64(datetime(*dt_obj[:6]), unit),
    "arrow"    : lambda dt_obj, _, __, ___, ____, _____, ______ : _to_arrow(dt_obj),
}

_DT_LIKE_OBJ_CONVERSION_DICT = {
    "float"  : lambda dt_obj, unit, float_class, int_class, ___, _____, ______ : _total_dt_unit(dt_obj, unit, float_class, int_class),
    "pandas" : lambda dt_obj, unit, __, ___, ____, _____, ______ : _to_datetime(dt_obj, unit),
    "str"    : lambda dt_obj, unit, __, ___, dt_fmt_str, _____, ______ : _to_string(dt_obj, unit, dt_fmt_str)
}
       
# Enumerate all possibilities #
CONVERSION_OPT_DICT = {
    "datetime": DT_OBJ_CONVERSION_DICT,
    "datetime64": DT64_OBJ_CONVERSION_DICT,
    "time" : DT_TIME_OBJ_CONVERSION_DICT,
    "timestamp": TIMESTAMP_OBJ_CONVERSION_DICT,
    "arrow": ARROW_OBJ_CONVERSION_DICT,
    "struct_time": TIME_STT_OBJ_CONVERSION_DICT,
    "dataframe": _DT_LIKE_OBJ_CONVERSION_DICT,
    "series": _DT_LIKE_OBJ_CONVERSION_DICT,
    "ndarray": _DT_LIKE_OBJ_CONVERSION_DICT
} 

# Exclusively to floated time #
_TOTAL_TIME_UNIT_DICT = {
    "datetime"    : lambda dt_obj, _, __, ___, ____ : dt_obj.timestamp(),
    "datetime64"  : lambda dt_obj, unit, float_class, _, __ : dt_obj.astype(f"timedelta64[{unit}]").astype(float_class),
    "struct_time" : lambda dt_obj, _, __, ___, ____ : datetime(*dt_obj[:6]),
    "arrow"       : lambda dt_obj, _, __, ___, ____ : dt_obj.float_timestamp,
    "dataframe"   : lambda dt_obj, _, __, int_class, unit_factor : _total_dt_complex_data(dt_obj, int_class, unit_factor),
    "series"      : lambda dt_obj, _, __, int_class, unit_factor : _total_dt_complex_data(dt_obj, int_class, unit_factor),
    "ndarray"     : lambda dt_obj, unit, float_class, _, __ : dt_obj.astype(f"datetime64[{unit}]").astype(float_class)  
}


# Template strings #
#------------------#

_TIME_STR_PARTS_TEMPLATES = [
    "{} days {} hours {} minutes {} seconds",
    "{} hours {} minutes {} seconds",
    "{} minutes {} seconds",
    "{} seconds",
]