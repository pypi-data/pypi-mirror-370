#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared time utilities to avoid circular imports.
"""

#----------------#
# Import modules #
#----------------#

# Standard modules #
import time
from datetime import datetime, timedelta

# Third-party modules #
import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str

#------------------#
# Define functions #
#------------------#

def get_datetime_object_unit(dt_obj):
    """
    Get the unit of a datetime object.
    
    Parameters
    ----------
    dt_obj : datetime.datetime, datetime.time, pandas.Timestamp, numpy.datetime64
        The datetime object to get the unit from.
    
    Returns
    -------
    str
        The unit of the datetime object.
        For datetime objects, returns 'us' (microseconds).
        For pandas objects, returns 'ns' (nanoseconds).
        For numpy objects, returns the unit from the dtype string.
    
    Raises
    ------
    TypeError
        If the input is not a supported datetime object type.
    """
    if isinstance(dt_obj, (datetime, time)):
        return "us"  # datetime objects use microsecond precision
    elif isinstance(dt_obj, pd.Timestamp):
        return "ns"  # pandas timestamps use nanosecond precision
    elif isinstance(dt_obj, np.datetime64):
        # Extract unit from dtype string (e.g., "datetime64[ns]" -> "ns")
        dtype_str = str(dt_obj.dtype)
        return dtype_str[dtype_str.find("[") + 1:dtype_str.find("]")]
    else:
        raise TypeError(f"Unsupported datetime object type: {type(dt_obj)}")

def get_nano_datetime(t=None, module="datetime"):
    """
    Get the current or specified time in nanoseconds, formatted as a datetime string.
    
    Parameters
    ----------
    t : int | float | None, optional
        Time value in nanoseconds. If None, the current time is used.
    module : {"datetime", "time", "pandas", "numpy", "arrow"}, default "datetime"
        Module used to parse the floated time.

    Returns
    -------
    nano_dt_str : str
        The formatted datetime string with nanoseconds.
    """
    if t is not None and not isinstance(t, (float, int)):
        raise TypeError("Time value must either be integer or float.")
    
    # Use current time if none is provided
    if t is None:
        t = time.time_ns()  # Get current time in nanoseconds
    
    # Ensure we handle floating-point times by converting to int
    if isinstance(t, float):
        t = int(str(t).replace(".", ""))
        
    floated_nanotime_str = _nano_floated_time_str(t)
    nano_dt_str = _convert_floated_time_to_datetime(floated_nanotime_str, module)
    return nano_dt_str

def _convert_floated_time_to_datetime(floated_time, module):
    """
    Convert a floated time value to a datetime object with nanosecond precision.

    Parameters
    ----------
    floated_time : float | int
        The floated time value to be converted.
    module : str
        Module used to parse the floated time.

    Returns
    -------
    nano_dt_str : str
        The formatted datetime string with nanoseconds.
    """
    # Convert to float if input is a string
    if isinstance(floated_time, str):
        floated_time = np.float128(floated_time)
        
    # Split into seconds and nanoseconds
    seconds = int(floated_time)
    nanoseconds = int((floated_time - seconds) * 1_000_000_000)

    # Convert the seconds part into a datetime object using the specified module
    if module == "datetime":
        dt = datetime.fromtimestamp(seconds)
    elif module == "pandas":
        dt = pd.Timestamp.fromtimestamp(seconds).to_pydatetime()
    elif module == "numpy":
        dt = pd.Timestamp.fromtimestamp(seconds).to_pydatetime()  # Convert via pandas for compatibility
    elif module == "arrow":
        try:
            import arrow
        except ImportError:
            raise ImportError("arrow package is required for arrow module conversion. Install with: pip install arrow")
        dt = arrow.get(seconds).datetime
    elif module == "time":
        dt = datetime.fromtimestamp(seconds)  # time module uses same as datetime
    else:
        raise ValueError(f"Unsupported module: {module}")
    
    # Add the nanoseconds part and return the formatted string
    dt_with_nanos = dt + timedelta(microseconds=nanoseconds / 1_000)
    dt_with_nanos_str = datetime_obj_converter(dt_with_nanos, 
                                               convert_to="str",
                                               dt_fmt_str='%FT%T')
    nano_dt_str = f"{dt_with_nanos_str}.{nanoseconds:09d}"
    return nano_dt_str

def _nano_floated_time_str(time_ns):
    """
    Convert a time value in nanoseconds to a formatted floating-point time string.

    Parameters
    ----------
    time_ns : int
        Time value in nanoseconds.

    Returns
    -------
    str
        The floating-point time string with nanosecond precision.
    """
    # Convert nanoseconds to seconds and nanoseconds parts
    seconds = time_ns // 1_000_000_000
    nanoseconds = time_ns % 1_000_000_000

    # Format the floating-point time with nanosecond precision
    return f"{seconds}.{nanoseconds:09d}"

def datetime_obj_converter(datetime_obj,
                           convert_to,
                           unit="s",
                           float_class="d", 
                           int_class="int",
                           dt_fmt_str=None):
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
        Supported values: "datetime", "timestamp", "datetime64", "arrow", "str", "float", "int".
        For example, if `datetime_obj` is a `datetime`, `convert_to` could be
        "datetime64", "timestamp", "float", etc.
    unit : str
        The date unit for conversion, used with numpy datetime64 and pandas Timestamp conversions.
        Default is `"s"` (seconds).
    float_class : str | np.floating
        The float precision class used when `convert_to="float"`. 
        Supported values: "d"/"float" (double), "f" (float32), numpy float types.
        Default is `"d"` (double precision).
    int_class : str | np.integer
        The integer precision class used when `convert_to="int"`.
        Supported values: "int" (Python int), "i" (int32), numpy integer types.
        Default is `"int"` (Python integer type).
    dt_fmt_str : str
        Format string to convert the date/time object to a string when `convert_to="str"`.

    Returns
    -------
    The converted date/time object in the format/type specified by `convert_to`.

    Raises
    ------
    ValueError
        If `convert_to` is not a valid target type for the given `datetime_obj`.
    RuntimeError
        If there is an error during the conversion process.
    """
    # Input validation
    if not convert_to:
        raise ValueError("Argument 'convert_to' not provided.")
    
    # Get the object type's name
    obj_type = get_type_str(datetime_obj, lowercase=True)
    
    # Convert to string if requested
    if convert_to == "str":
        if dt_fmt_str:
            return datetime_obj.strftime(dt_fmt_str)
        return str(datetime_obj)
    
    # Convert to datetime if requested
    if convert_to == "datetime":
        if isinstance(datetime_obj, datetime):
            return datetime_obj
        if isinstance(datetime_obj, pd.Timestamp):
            return datetime_obj.to_pydatetime()
        if isinstance(datetime_obj, np.datetime64):
            return pd.Timestamp(datetime_obj).to_pydatetime()
        # Check if the object is an Arrow object using string comparison to avoid import
        if obj_type == "arrow":
            return datetime_obj.datetime
        raise ValueError(f"Cannot convert {obj_type} to datetime")
    
    # Convert to pandas Timestamp if requested
    if convert_to == "timestamp":
        if isinstance(datetime_obj, pd.Timestamp):
            return datetime_obj
        if isinstance(datetime_obj, datetime):
            return pd.Timestamp(datetime_obj)
        if isinstance(datetime_obj, np.datetime64):
            return pd.Timestamp(datetime_obj, unit=unit)
        if obj_type == "arrow":
            return pd.Timestamp(datetime_obj.datetime)
        raise ValueError(f"Cannot convert {obj_type} to Timestamp")
    
    # Convert to numpy datetime64 if requested
    if convert_to == "datetime64":
        if isinstance(datetime_obj, np.datetime64):
            return datetime_obj.astype(f'datetime64[{unit}]')
        if isinstance(datetime_obj, (datetime, pd.Timestamp)):
            return np.datetime64(datetime_obj, unit)
        if obj_type == "arrow":
            return np.datetime64(datetime_obj.datetime, unit)
        raise ValueError(f"Cannot convert {obj_type} to datetime64")
    
    # Convert to arrow if requested
    if convert_to == "arrow":
        try:
            import arrow
        except ImportError:
            raise ImportError("arrow package is required for arrow conversion. Install with: pip install arrow")
        
        if obj_type == "arrow":
            return datetime_obj
        if isinstance(datetime_obj, datetime):
            return arrow.get(datetime_obj)
        if isinstance(datetime_obj, pd.Timestamp):
            return arrow.get(datetime_obj.to_pydatetime())
        if isinstance(datetime_obj, np.datetime64):
            return arrow.get(pd.Timestamp(datetime_obj).to_pydatetime())
        raise ValueError(f"Cannot convert {obj_type} to arrow")
    
    # Convert to float if requested
    if convert_to == "float":
        if hasattr(datetime_obj, 'timestamp'):
            # For datetime and pandas objects
            timestamp = datetime_obj.timestamp()
        elif isinstance(datetime_obj, np.datetime64):
            # For numpy datetime64 objects
            timestamp = datetime_obj.astype(f'datetime64[{unit}]').astype(float_class)
            return timestamp
        elif obj_type == "arrow":
            timestamp = datetime_obj.float_timestamp
        else:
            raise ValueError(f"Cannot convert {obj_type} to float")
        
        # Apply float precision class
        if float_class == "d" or float_class == "float":
            return float(timestamp)
        elif float_class == "f":
            return np.float32(timestamp)
        elif isinstance(float_class, type) and issubclass(float_class, np.floating):
            return float_class(timestamp)
        else:
            return np.dtype(float_class).type(timestamp)
    
    # Convert to int if requested
    if convert_to == "int":
        if hasattr(datetime_obj, 'timestamp'):
            # For datetime and pandas objects
            timestamp = int(datetime_obj.timestamp())
        elif isinstance(datetime_obj, np.datetime64):
            # For numpy datetime64 objects
            timestamp = datetime_obj.astype(f'datetime64[{unit}]').astype(int_class)
            return timestamp
        elif obj_type == "arrow":
            timestamp = int(datetime_obj.float_timestamp)
        else:
            raise ValueError(f"Cannot convert {obj_type} to int")
        
        # Apply int precision class
        if int_class == "int":
            return int(timestamp)
        elif int_class == "i":
            return np.int32(timestamp)
        elif isinstance(int_class, type) and issubclass(int_class, np.integer):
            return int_class(timestamp)
        else:
            return np.dtype(int_class).type(timestamp)
    
    raise ValueError(f"Unsupported conversion target: {convert_to}") 
