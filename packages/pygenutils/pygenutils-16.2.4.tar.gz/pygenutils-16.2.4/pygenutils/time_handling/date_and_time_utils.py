#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date and time utilities.
"""

#----------------#
# Import modules #
#----------------#

# Standard modules #
import os
import time
from datetime import datetime, timedelta, timezone

# Third-party modules #
import pandas as pd
import xarray as xr

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args, get_type_str
from filewise.xarray_utils.file_utils import ncfile_integrity_status
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.strings.text_formatters import format_string, print_format_string
from pygenutils.time_handling.time_utils import datetime_obj_converter

# Try to import `pytz` and set a flag for availability
try:
    import pytz
    pytz_installed = True
except ImportError:
    pytz_installed = False

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
    error_class : {ValueError, AttributeError}
        Error class to raise if option is not in the list of allowed ones.
    error_str : str
        Single or multiple line string denoting an error.

    Raises
    ------    
    ValueError or AttributeError: 
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

# Dates and times #
#-----------------#

def get_current_datetime(dtype="datetime", time_fmt_str=None, tz_arg=None):    
    """
    Returns the current date and time based on the specified data type.

    Parameters
    ----------
    dtype : str
        Type of current time to retrieve. 
        Available options:
        - 'datetime'  : Returns datetime object using datetime.datetime.now()
        - 'str'       : Returns string representation of current time using time.ctime()
        - 'timestamp' : Returns timestamp object using pd.Timestamp.now()
        Default is 'datetime'.

    time_fmt_str : str, optional
        Optional format string for datetime formatting using .strftime().
        Default is None.

    tz_arg : timezone or str, optional
        Optional timezone object or string for specifying the timezone.
        If a string is provided, it will be converted to a timezone using pytz.

    Raises
    ------
    ValueError
    - If dtype is not one of the valid options ('datetime', 'str', 'timestamp').
    - If 'time_fmt_str' is provided and dtype is 'str' (which returns a string),
      as strings do not have .strftime() attribute.
    RuntimeError
        Possible only if ``dtype='str'``, if there is an error during the conversion process.

    Returns
    -------
    current_time : str | datetime.datetime | pd.Timestamp
        Current date and time object based on the dtype.
        If 'time_fmt_str' is provided, returns a formatted string representation.
    """    
    # Validate string representing the data type #
    format_args_current_time = (dtype, DT_DTYPE_OPTIONS)
    _validate_option(format_args_current_time, ValueError, UNSUPPORTED_OPTION_TEMPLATE)
    
    # Handle timezone argument
    if tz_arg is None:
        tz = None
    
    elif isinstance(tz_arg, str):
        if pytz_installed:
            try:
                tz_arg = pytz.timezone(tz_arg)
            except pytz.UnknownTimeZoneError:
                raise ValueError(f"Invalid timezone: {tz_arg}")
        else:
            raise ValueError("'pytz' library is required for string timezone arguments.")
    elif isinstance(tz_arg, int):
        tz = timezone(timedelta(hours=tz_arg))
    elif isinstance(tz_arg, timezone):
        tz = tz_arg
    else:
        raise TypeError("'tz_arg' must be a timezone object, string, or integer for UTC offset.")

    # Get the current date and time #
    current_time = CURRENT_DATETIME_DICT.get(dtype)(tz)
    
    # A string does not have .strftime attribute, warn accordingly #
    param_keys = get_caller_args()
    fmt_str_arg_pos = find_substring_index(param_keys, "time_fmt_str")
    if (isinstance(current_time, str) and time_fmt_str is not None):
        raise ValueError("Current time is already a string. "
                         f"Choose another data type or "
                         f"set '{param_keys[fmt_str_arg_pos]}' to None.")
    
    # Format the object based on 'time_fmt_str' variable, if provided #
    if time_fmt_str is not None:
        try:
            current_time = datetime_obj_converter(current_time, convert_to="str")
        except Exception as err:
            raise RuntimeError(f"Error during conversion to 'str'': {err}")
        else:
            return current_time

# Date/time attributes and keys #
#------------------------------#

def find_dt_key(data):
    """
    Function that searches for the date/time key in various data structures.
    Supports both exact matches and partial matches with common time-related terms.

    Parameters
    ----------
    data : pandas.DataFrame, xarray.Dataset, xarray.DataArray, or str
        The input data structure to search for time-related keys:
        - For pandas DataFrame: searches column names
        - For xarray Dataset/DataArray: searches dimensions and variables
        - For str: assumes it's a file path and opens it as xarray Dataset

    Returns
    -------
    str
        The identified time-related key name.

    Raises
    ------
    TypeError
        If the input data type is not supported.
    ValueError
        If no time-related key is found.
    """
    
    # Common time-related keywords - both full words and prefixes
    time_keywords = {
        'exact': ['time', 'Time', 'TIME', 't', 'T', 'date', 'Date', 'DATE'],
        'prefix': ['da', 'fe', 'tim', 'yy', 't_', 'ti']
    }
    
    def check_exact_match(name):
        """Helper to check for exact matches"""
        return name.lower() in [k.lower() for k in time_keywords['exact']]
    
    def check_prefix_match(name):
        """Helper to check for prefix matches"""
        name_lower = name.lower()
        return any(name_lower.startswith(prefix.lower()) for prefix in time_keywords['prefix'])
    
    # Handle pandas DataFrame
    obj_type = get_type_str(data, lowercase=True)
    if obj_type == "dataframe":
        # Try exact matches first
        df_cols = data.columns.tolist()
        for col in df_cols:
            if check_exact_match(col):
                return col
        
        # Try prefix matches if no exact match found
        for col in df_cols:
            if check_prefix_match(col):
                return col
                
        raise ValueError("No time-related column found in the pandas DataFrame.")
    
    # Handle xarray objects
    elif isinstance(data, (xr.Dataset, xr.DataArray)):
        # First check dimensions
        for dim in data.dims:
            if check_exact_match(dim):
                return dim
            if check_prefix_match(dim):
                return dim
        
        # Then check variables
        for var in data.variables:
            if check_exact_match(var):
                return var
            if check_prefix_match(var):
                return var
                
        raise ValueError("No time-related dimension or variable found in the xarray object.")
    
    # Handle string (assumed to be file path)
    elif isinstance(data, str):
        try:
            ds = xr.open_dataset(data)
            try:
                time_key = find_dt_key(ds)
                return time_key
            finally:
                ds.close()
        except Exception as e:
            raise ValueError(f"Could not find time dimension in file {data}: {e}")
    
    else:
        raise TypeError("Unsupported data type. Must be pandas DataFrame, "
                       "xarray Dataset/DataArray, or file path string.")

# %%

# Display and Conversion Utilities #
#----------------------------------#

def display_user_timestamp(user_timestamp, user_timezone_str):
    """
    Converts a UTC timestamp to the user's local timezone and formats it for display.
    
    Parameters
    ----------
    user_timestamp : datetime.datetime or str
        The timestamp to be converted. If a string, it should be in ISO format (e.g., "2023-01-01T12:00:00Z").
        The function assumes `user_timestamp` is in UTC if naive (no timezone).
        
    user_timezone_str : str
        The IANA timezone name (e.g., "America/New_York", "Europe/London") for the target timezone.

    Returns
    -------
    datetime.datetime or str
        The timestamp converted to the specified timezone.
        Returns as a `datetime` object if conversion is successful; otherwise, as a string with error details.

    Notes
    -----
    - If the `pytz` library is available, it is used for timezone conversion, providing extensive IANA timezone support.
    - If `pytz` is unavailable, the function defaults to using `datetime`'s built-in `astimezone()` mechanism, but limited to standard UTC offset conversions.
    
    Example
    -------
    >>> display_user_timestamp(datetime.now(timezone.utc), "America/New_York")
    datetime.datetime(2023, 1, 1, 7, 0, tzinfo=<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>)
    
    >>> display_user_timestamp("2023-01-01T12:00:00Z", "Europe/London")
    datetime.datetime(2023, 1, 1, 12, 0, tzinfo=<DstTzInfo 'Europe/London' GMT0:00:00 STD>)
    """
    # Ensure user_timestamp is a datetime object in UTC
    if isinstance(user_timestamp, str):
        try:
            user_timestamp = datetime.fromisoformat(user_timestamp.replace("Z", "+00:00"))
        except ValueError:
            return "Invalid timestamp format. Expected ISO format (e.g., '2023-01-01T12:00:00Z')."
    elif not isinstance(user_timestamp, datetime):
        return "Invalid timestamp type. Expected `datetime` or ISO format string."
    
    if user_timestamp.tzinfo is None:
        user_timestamp = user_timestamp.replace(tzinfo=timezone.utc)

    # Convert timestamp using pytz if available, or fallback otherwise
    try:
        if pytz_installed:
            try:
                user_timezone = pytz.timezone(user_timezone_str)
            except pytz.UnknownTimeZoneError:
                raise ValueError(f"Invalid timezone: {user_timezone_str}")
            localized_timestamp = user_timestamp.astimezone(user_timezone)
        else:
            offset_hours = int(user_timezone_str.split("UTC")[-1].split(":")[0])
            offset_minutes = int(user_timezone_str.split(":")[1]) if ":" in user_timezone_str else 0
            offset = timedelta(hours=offset_hours, minutes=offset_minutes)
            localized_timestamp = user_timestamp.astimezone(timezone(offset))
            
    except Exception as e:
        raise RuntimeError(f"Error converting timestamp: {e}")

    return localized_timestamp


# Dates and times #
#-----------------#

def get_current_datetime(dtype="datetime", time_fmt_str=None, tz_arg=None):    
    """
    Returns the current date and time based on the specified data type.

    Parameters
    ----------
    dtype : str
        Type of current time to retrieve. 
        Available options:
        - 'datetime'  : Returns datetime object using datetime.datetime.now()
        - 'str'       : Returns string representation of current time using time.ctime()
        - 'timestamp' : Returns timestamp object using pd.Timestamp.now()
        Default is 'datetime'.

    time_fmt_str : str, optional
        Optional format string for datetime formatting using .strftime().
        Default is None.

    tz_arg : timezone or str, optional
        Optional timezone object or string for specifying the timezone.
        If a string is provided, it will be converted to a timezone using pytz.

    Raises
    ------
    ValueError
    - If dtype is not one of the valid options ('datetime', 'str', 'timestamp').
    - If 'time_fmt_str' is provided and dtype is 'str' (which returns a string),
      as strings do not have .strftime() attribute.
    RuntimeError
        Possible only if ``dtype='str'``, if there is an error during the conversion process.

    Returns
    -------
    current_time : str | datetime.datetime | pd.Timestamp
        Current date and time object based on the dtype.
        If 'time_fmt_str' is provided, returns a formatted string representation.
    """    
    # Validate string representing the data type #
    format_args_current_time = (dtype, DT_DTYPE_OPTIONS)
    _validate_option(format_args_current_time, ValueError, UNSUPPORTED_OPTION_TEMPLATE)
    
    # Handle timezone argument
    if tz_arg is None:
        tz = None
    
    elif isinstance(tz_arg, str):
        if pytz_installed:
            try:
                tz_arg = pytz.timezone(tz_arg)
            except pytz.UnknownTimeZoneError:
                raise ValueError(f"Invalid timezone: {tz_arg}")
        else:
            raise ValueError("'pytz' library is required for string timezone arguments.")
    elif isinstance(tz_arg, int):
        tz = timezone(timedelta(hours=tz_arg))
    elif isinstance(tz_arg, timezone):
        tz = tz_arg
    else:
        raise TypeError("'tz_arg' must be a timezone object, string, or integer for UTC offset.")

    # Get the current date and time #
    current_time = CURRENT_DATETIME_DICT.get(dtype)(tz)
    
    # A string does not have .strftime attribute, warn accordingly #
    param_keys = get_caller_args()
    fmt_str_arg_pos = find_substring_index(param_keys, "time_fmt_str")
    if (isinstance(current_time, str) and time_fmt_str is not None):
        raise ValueError("Current time is already a string. "
                         f"Choose another data type or "
                         f"set '{param_keys[fmt_str_arg_pos]}' to None.")
    
    # Format the object based on 'time_fmt_str' variable, if provided #
    if time_fmt_str is not None:
        try:
            current_time = datetime_obj_converter(current_time, convert_to="str")
        except Exception as err:
            raise RuntimeError(f"Error during conversion to 'str'': {err}")
        else:
            return current_time
        

# Date/time attributes #
#-#-#-#-#-#-#-#-#-#-#-#-

def get_datetime_object_unit(dt_obj):
    """
    Retrieve the time unit of a numpy.datetime64 or similar datetime object.

    Parameters
    ----------
    dt_obj : object
        The datetime-like object from which the unit is to be retrieved. 
        Must have a 'dtype' attribute, such as numpy.datetime64 or pandas.Timestamp.

    Returns
    -------
    str
        The time unit of the datetime object (e.g., "ns" for nanoseconds).
    
    Raises
    ------
    AttributeError
        If the object does not have a 'dtype' attribute or is not of a supported type.
    ValueError
        If the string parsing fails
    """
    obj_type = get_type_str(dt_obj)
    
    if hasattr(dt_obj, "dtype"):
        dtype_str = str(dt_obj.dtype)
        if ("[" in dtype_str and "]" in dtype_str):
            return dtype_str.split("[", 1)[1].split("]", 1)[0]
        else:
            raise ValueError(f"Could not determine unit from dtype: '{dtype_str}'")
    else:
        raise AttributeError(f"Object of type '{obj_type}' has no attribute 'dtype'.")
        

def infer_frequency(data):
    """
    Infer the most likely frequency from the input, which can be either 
    a pandas DataFrame, Series, DatetimeIndex, TimedeltaIndex, 
    a NetCDF file path (as a string), or an xarray Dataset/DataArray.

    Parameters
    ----------
    data : pandas.DataFrame, pandas.Series, pandas.DatetimeIndex, pandas.TimedeltaIndex, 
           str (NetCDF file path), or xarray.Dataset/xarray.DataArray
        The input data for which to infer the frequency. 
        - For pandas objects, the method will try to infer the time frequency using 
          the 'find_dt_key' helper to locate the date column or index.
        - For NetCDF files (string or xarray object), the method will infer the time frequency 
          using the 'find_dt_key' helper to locate the time dimension.

    Returns
    -------
    str
        The inferred time frequency. If the frequency cannot be determined, a ValueError is raised.

    Raises
    ------
    ValueError
        If the frequency cannot be inferred from the input data.

    Notes
    -----
    - For pandas Series, the method will infer the frequency based on the series values, 
      not the index.
    - For NetCDF files, the method can handle either file paths (strings) or already-opened 
      xarray.Dataset/xarray.DataArray objects.
    """
    # Check input data type #
    #########################
    obj_type = get_type_str(data, lowercase=True)
    
    # Section 1: Handling Pandas DataFrame, Series, DatetimeIndex, or TimedeltaIndex #
    ##################################################################################
    if obj_type in ["dataframe", "series", "datetimeindex","timedeltaindex"]:
        try:
            # Attempt to find date column and infer frequency
            date_key = find_dt_key(data)
            time_freq = pd.infer_freq(data[date_key])
        except (TypeError, ValueError):
            # If no date key is found, assume the input is an index
            time_freq = pd.infer_freq(data)
            
        if not time_freq:
            raise ValueError("Could not determine the time frequency from the pandas object.")
        return time_freq

    # Section 2: Handling NetCDF Files (string or xarray objects) #
    ###############################################################

    elif obj_type == "str":
        ds = ncfile_integrity_status(data)
    elif obj_type in ["dataset", "dataarray"]:
        ds = data.copy()
    else:
        raise TypeError("Unsupported data type. Must be pandas DataFrame, "
                        "Series, DatetimeIndex, TimedeltaIndex, "
                        "NetCDF file path (string), or xarray.Dataset/DataArray.")
        
    # Lazy import of xarray (if not already imported)
    if 'xr' not in globals():
        import xarray as xr
     
    # Infer time frequency for NetCDF data
    date_key = find_dt_key(ds)
    time_freq = xr.infer_freq(ds[date_key])

    if not time_freq:
        raise ValueError("Could not determine the time frequency from the NetCDF data.")
    return time_freq


def infer_dt_range(data):
    """
    Infer the date and time range (first and last timestamps) from the input data,
    which can be either a pandas DataFrame, Series, or a NetCDF file path (as a string),
    or an xarray Dataset/DataArray.

    Parameters
    ----------
    data : pandas.DataFrame, pandas.Series, str (NetCDF file path), or xarray.Dataset/xarray.DataArray
        The input data from which to infer the date range.
        - For pandas objects, the method will use the 'find_dt_key' to locate the date column.
        - For NetCDF files (string or xarray object), the method will infer the time range
          using the 'find_dt_key' to locate the time dimension.

    Returns
    -------
    str
        A string representing the full time period in the format 'start_year-end_year'.

    Raises
    ------
    TypeError
        If the input data type is not supported.

    Notes
    -----
    - For pandas Series, the method will infer the date range based on the series values, 
      not the index.
    - For NetCDF files, the method will attempt a lazy import of xarray to avoid unnecessary 
      installation for non-climate-related tasks.
    """
    # Check input data type #
    obj_type = get_type_str(data, lowercase=True)
    
    # Section 1: Handling Pandas DataFrame or Series
    if obj_type in ["dataframe", "series"]:
        date_key = find_dt_key(data)
        years = pd.unique(data[date_key].dt.year)
        full_period = f"{years[0]}-{years[-1]}"
        return full_period

    # Section 2: Handling NetCDF Files (string or xarray objects)
    elif obj_type == "str":
        ds = ncfile_integrity_status(data)
        try:
            date_key = find_dt_key(ds)
            years = pd.unique(ds[date_key].dt.year)
            full_period = f"{years[0]}-{years[-1]}"
            return full_period
        finally:
            ds.close()
    elif obj_type in ["dataset", "dataarray"]:
        ds = data.copy()
        date_key = find_dt_key(ds)
        years = pd.unique(ds[date_key].dt.year)
        full_period = f"{years[0]}-{years[-1]}"
        return full_period
    else:
        raise TypeError("Unsupported data type. Must be pandas DataFrame, Series, "
                        "NetCDF file path (string), or xarray.Dataset/DataArray.")


# %%

# File manipulation time attributes #
#-----------------------------------#

def get_obj_operation_datetime(obj_list,
                               attr="modification",
                               time_fmt_str="%F %T",
                               want_numpy_array=True):
    """
    Returns a 2D numpy array where each row contains an object (file path)
    from obj_list and its corresponding time attribute (creation, modification,
    or access time).

    Parameters
    ----------
    obj_list : str | list[str]
        List of file paths or a single file path string.
    attr : {'creation', 'modification', or 'access'}, optional
        Type of time attribute to retrieve. Defaults to 'modification'.
    time_fmt_str : str, optional
        Format string for formatting the time attribute using .strftime(). 
        Defaults to '%F %T'.
    want_numpy_array : bool
        Determines whether to convert the final object to a 2D Numpy array.
        If True, a 2D Numpy array is returned, else a list composed of lists.
        Defaults to True.
        
    Returns
    -------
    obj_timestamp_container : list[list] | numpy.ndarray
        If 'want_numpy_array' is False, a list of lists, where each of the latter
        contains the [file path, formatted time attribute], else a 2D Numpy array.

    Raises
    ------
    AttributeError
        If attr is not one of the valid options ('creation', 'modification', 'access').
        
    Note
    ----
    By default, 'want_numpy_array' is set to True, because
    it is expected to perform high-level operations with arrays frequently.
    However, this is a large library an since it's used only minimally in this module,
    lazy and selective import will be made.
    """
    
    # Validate the type of time attribute #
    format_args_operation_datetime = (attr, ATTR_OPTIONS)
    _validate_option(format_args_operation_datetime, AttributeError, ATTRIBUTE_ERROR_TEMPLATE)
    
    # Convert the input file object to a list if it is a string #
    if isinstance(obj_list, str):
        obj_list = [obj_list]
    
    # Handle nested lists by flattening them first
    elif isinstance(obj_list, list):
        if any(isinstance(item, list) for item in obj_list):
            obj_list = flatten_list(obj_list)
    
    # Retrieve operation times #
    obj_timestamp_container = []
    
    for obj in obj_list:
        struct_time_attr_obj = STRUCT_TIME_ATTR_DICT.get(attr)(obj)
        timestamp_str_attr_obj = time.strftime(time_fmt_str, struct_time_attr_obj)
        info_list = [obj, timestamp_str_attr_obj]
        obj_timestamp_container.append(info_list)
        
    # Format the result into a Numpy array if desired #
    if want_numpy_array:
        from numpy import array
        return array(obj_timestamp_container)
    else:
        return obj_timestamp_container    

#%%

# Pandas DataFrames of dates and times #
#--------------------------------------#

def merge_datetime_dataframes(df1, df2,
                              operator="inner",
                              time_fmt_str=None):
    """
    Merges two datetime objects (either pandas.DataFrames or named/unnamed pandas.Series) 
    based on a specified operator, and optionally formats the datetime columns.

    Parameters
    ----------
    df1 : pandas.DataFrame or pandas.Series
        The first datetime object.
    df2 : pandas.DataFrame or pandas.Series
        The second datetime object.
    operator : {'inner', 'outer', 'left', 'right'}, default 'inner'
        The type of merge to be performed.
    time_fmt_str : str, optional
        Format string for formatting the datetime columns using .strftime(). 
        Defaults to None.

    Returns
    -------
    pandas.DataFrame
        The merged datetime DataFrame.

    Raises
    ------
    ValueError
        If the operator is not one of the valid options:
        ('inner', 'outer', 'left', 'right').
    TypeError
        If df1 or df2 are not pandas.DataFrame or pandas.Series.
    AttributeError
        If df2 is a pandas.Series and does not have a name attribute.
    """
    
    # Input validations #
    #-#-#-#-#-#-#-#-#-#-#
    
    # Get the main argument names and their position on the function's arg list #    
    param_keys = get_caller_args()
    df1_arg_pos = find_substring_index(param_keys, "df1")
    df2_arg_pos = find_substring_index(param_keys, "df2")
    
    # Convert Series to DataFrame if necessary and standardize the column name #
    if isinstance(df1, pd.Series):
        df1 = df1.to_frame(name=df1.name if df1.name else "Date")        
    if isinstance(df2, pd.Series):
        df2 = df2.to_frame(name=df2.name if df2.name else "Date")
        
    # If objects are DataFrames, ensure first datetime column name is standardised #
    std_date_colname = "Date"
    
    # First object
    try:
        dt_colname = find_dt_key(df1)
    except Exception as err:
        format_args_df1 = (err, param_keys[df1_arg_pos])
        print_format_string(DATE_COLNAME_NOT_FOUND_TEMPLATE, format_args_df1)
        
        df1_cols = list(df1.columns)
        df1_cols[0] = std_date_colname
        df1.columns = df1_cols
    
    # Second object
    try:
        dt_colname = find_dt_key(df2)
    except Exception as err:
        format_args_df2 = (err, param_keys[df2_arg_pos])
        print_format_string(DATE_COLNAME_NOT_FOUND_TEMPLATE, format_args_df2)
        
        df2_cols = list(df2.columns)
        df2_cols[0] = std_date_colname
        df2.columns = df2_cols
                
    # Operator argument choice #    
    format_args_dt_range_op1 = (operator, DT_RANGE_OPERATORS)
    _validate_option(format_args_dt_range_op1, ValueError, UNSUPPORTED_OPTION_TEMPLATE)
        
    # Operations #
    #-#-#-#-#-#-#-
    
    # Perform merge operation #
    res_dts = pd.merge(df1, df2, how=operator)
    
    # Sort values by datetime column #
    try:
        res_dts = res_dts.sort_values(by=dt_colname)
    except:
        res_dts = res_dts.sort_values(by=std_date_colname)
    
    # Optionally format datetime values #
    if time_fmt_str is not None:
        res_dts = datetime_obj_converter(res_dts, convert_to="str", dt_fmt_str=time_fmt_str)
        
    return res_dts
  
#%%

#--------------------------#
# Parameters and constants #
#--------------------------#

# Option lists #
DT_RANGE_OPERATORS = ["inner", "outer", "cross", "left", "right"]
DT_DTYPE_OPTIONS = ["datetime", "str", "timestamp"]
ATTR_OPTIONS = ["creation", "modification", "access"]
ERROR_CLASS_LIST = [ValueError, AttributeError]

# Time span shortands #
TIME_KWS = ["da", "fe", "tim", "yy"]

# Template strings #
#------------------#

# Error strings #
UNSUPPORTED_OPTION_TEMPLATE = """Unsupported option '{}'. Options are {}."""
ATTRIBUTE_ERROR_TEMPLATE = "Invalid attribute '{}'. Options are {}. "
DATE_COLNAME_NOT_FOUND_TEMPLATE = """{} at object '{}'.
Setting default name 'Date' to column number 0."""

# Switch dictionaries #
#---------------------#

# Dictionary mapping attribute names to corresponding methods #
STRUCT_TIME_ATTR_DICT = {
    ATTR_OPTIONS[0]: lambda obj: time.gmtime(os.path.getctime(obj)),
    ATTR_OPTIONS[1]: lambda obj: time.gmtime(os.path.getmtime(obj)),
    ATTR_OPTIONS[2]: lambda obj: time.gmtime(os.path.getatime(obj))
}

# Dictionary mapping current time provider methods to the corresponding methods #
CURRENT_DATETIME_DICT = {
    DT_DTYPE_OPTIONS[0] : lambda tz_arg: datetime.datetime.now(tz_arg),
    DT_DTYPE_OPTIONS[1] : lambda tz_arg: time.ctime(tz_arg),
    DT_DTYPE_OPTIONS[2] : lambda tz_arg: pd.Timestamp.now(tz_arg)
}
