#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import calendar
import datetime

import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str
from filewise.pandas_utils.pandas_obj_handler import save2csv, save2excel
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.arrays_and_lists.patterns import unique_type_objects
from pygenutils.strings.string_handler import modify_obj_specs
from pygenutils.time_handling.date_and_time_utils import (
    find_dt_key,
    infer_frequency,
)

#------------------#
# Define functions #
#------------------#

# Calendar standardisers #
#------------------------#
# %%

def standardise_calendar(obj,
                         file_path,
                         interpolation_method=None,
                         order=None,
                         axis=0,
                         save_as_new_obj=False, 
                         extension=None, 
                         separator=",",
                         save_index=False,
                         save_header=False):
    
    """
    Standardise the calendar of a pandas or xarray object to the Gregorian calendar and 
    interpolate missing timestamps.
    
    This function aligns the time axis of a given pandas DataFrame or xarray Dataset/DataArray
    to a Gregorian calendar by identifying missing timestamps and interpolating missing data.
    Useful when handling model outputs with non-standard calendars.
    
    Parameters
    ----------
    obj : pandas.DataFrame, xarray.Dataset, xarray.DataArray, or list of them
        Object containing data. For pandas DataFrames, the first column 
        must be of datetime64 type.
    file_path : str | list[str]
        Path(s) to the file(s) from which the data object was extracted.
    interpolation_method : str, optional
        Interpolation method to use for filling missing data, e.g., 'linear', 'polynomial'.
    order : int, optional
        Order of the interpolation method if polynomial or spline interpolation is used.
    axis : int, optional
        Axis along which to interpolate, for pandas objects (default is 0).
    save_as_new_obj : bool, optional
        If True, saves the standardised object to a new file (CSV, Excel, or NetCDF).
    extension : str, optional
        File extension for saving the standardised object, either 'csv', 'xlsx', or 'nc'.
    separator : str, optional
        Separator for CSV files (default is ',').
    save_index : bool, optional
        Whether to save the index in the output file (default is False).
    save_header : bool, optional
        Whether to include headers in the output file (default is False).
    
    Returns
    -------
    obj : pandas.DataFrame, xarray.Dataset, or xarray.DataArray
        Object with a standardised calendar and interpolated data.
    
    Notes
    -----
    For Excel files, data will be saved with separate sheets for each variable (if applicable).
    """

    obj_type = get_type_str(obj, lowercase=True)
    
    # Validate extension if save_as_new_obj is True
    if save_as_new_obj and extension is not None:
        if obj_type == "pandas" and extension not in SUPPORTED_FILE_EXTS_PANDAS:
            raise ValueError(f"Unsupported file extension for pandas objects: '{extension}'. "
                           f"Supported extensions are: {SUPPORTED_FILE_EXTS_PANDAS}")
    
    # Handling pandas dataframes #
    if obj_type == "pandas" \
        or (obj_type == "list" and all(get_type_str(element) == "dataframe")
            for element in obj):
        
        obj = np.atleast_1d(obj)  # Ensure obj is list-like
        file_path = np.atleast_1d(file_path)  # Ensure file_path is list-like
        
        # Handle nested lists by flattening them first
        if isinstance(file_path, list):
            if any(isinstance(item, list) for item in file_path):
                file_path = flatten_list(file_path)
        
        obj_std_calendar = []
        len_objects = len(obj)
        
        # Check if all objects passed in a list are of the same type
        len_unique_type_list = unique_type_objects(obj)[-1]
        if len_unique_type_list > 1:
            raise ValueError("Not every object in the list is of the same type.")
        
        # Assuming all elements are pandas DataFrames
        for obj_num, (current_obj, fp) in enumerate(zip(obj, file_path)):
            
            time_col = find_dt_key(current_obj)
            time_freq = infer_frequency(current_obj.loc[:10, time_col])
            
            time_shorter = current_obj[time_col].to_numpy()
            full_times = pd.date_range(start=current_obj.iloc[0, time_col],
                                       end=current_obj.iloc[-1, time_col], 
                                       freq=time_freq)
            
            print(f"Data frames remaining: {len_objects - (obj_num+1)}")
            
            # Check for missing dates
            missing_dates = set(full_times) - set(time_shorter)
            for ft in missing_dates:
                missing_date_yesterday = ft - pd.Timedelta(days=1)
                index_yesterday = current_obj[current_obj[time_col] == missing_date_yesterday].index
                
                # Insert missing rows with NaNs
                index_missing_time = index_yesterday + 1
                new_row = pd.DataFrame([[ft] + [np.nan] * (current_obj.shape[1] - 1)], 
                                       columns=current_obj.columns, 
                                       index=[index_missing_time])
                current_obj = pd.concat([current_obj.iloc[:index_missing_time], 
                                         new_row, 
                                         current_obj.iloc[index_missing_time:]]).reset_index(drop=True)
            
            # Interpolate missing data
            if interpolation_method:
                # Import here to avoid circular imports
                from statflow.core.interpolation_methods import interp_pd
                current_obj.iloc[:, 1:] = interp_pd(current_obj.iloc[:, 1:],
                                                    method=interpolation_method,
                                                    order=order,
                                                    axis=axis)
            obj_std_calendar.append(current_obj)
        
            # Save as CSV or Excel if needed
            if save_as_new_obj:
                obj2change = "name_noext"
                str2add = "_std_calendar"
                saving_file_name = modify_obj_specs(fp, obj2change, new_obj=None, str2add=str2add)
                
                if extension == "csv":        
                    save2csv(saving_file_name, current_obj, separator, save_index, save_header)
                elif extension == "xlsx":
                    frame_dict = {col: current_obj[[time_col, col]] for col in current_obj.columns[1:]}
                    save2excel(saving_file_name, frame_dict, save_index, save_header)
                else:
                    raise ValueError(f"Unsupported file extension: '{extension}'")
        
        return obj_std_calendar
    
    # Handling xarray datasets or data arrays #
    elif obj_type in ["dataarray", "dataset"] \
        or (obj_type == "list" and all(get_type_str(element) in ["dataarray", "dataset"] 
                                       for element in obj)):
        
        from xarray import cftime_range
        from filewise.xarray_utils.patterns import get_file_dimensions
            
        if isinstance(obj, list):
            obj = obj[0]  # Assuming only one object in the list

        # Get the time dimension using get_file_dimensions
        time_dim = get_file_dimensions(obj)
        if isinstance(time_dim, list):
            time_dim = time_dim[0]  # Assuming time is the first dimension

        full_times = cftime_range(start=obj[time_dim][0].values, 
                                  end=obj[time_dim][-1].values, 
                                  freq=infer_frequency(obj[time_dim]))
        obj_std_calendar = obj.reindex({time_dim: full_times}, method=None)
        
        if interpolation_method:
            # Import here to avoid circular imports
            from statflow.core.interpolation_methods import interp_xr
            obj_std_calendar = interp_xr(obj_std_calendar, 
                                         method=interpolation_method,
                                         order=order,
                                         dim=time_dim)            
        
        # Save as NetCDF if needed
        if save_as_new_obj:
            obj2change = "name_noext"
            str2add = "_std_calendar"
            saving_file_name = modify_obj_specs(file_path, obj2change, new_obj=None, str2add=str2add)
            if extension == "nc":
                obj_std_calendar.to_netcdf(saving_file_name)
            else:
                raise ValueError(f"Unsupported file extension: '{extension}'")
        
        return obj_std_calendar
    
    else:
        raise TypeError("Unsupported object type. "
                        "Please provide a pandas DataFrame, xarray Dataset, or xarray DataArray.")



# %%
# Leap years #
#------------#

def leap_year_detector(start_year, end_year, return_days=False):
    """
    Detects leap years in a given range or returns the number of days 
    in each year of the range.

    This function can return a dictionary indicating whether each year 
    in the range is a leap year, or return the number of days in each year,
    depending on the `return_days` flag.

    Parameters
    ----------
    start_year : int or str
        The start year of the range (inclusive). Can be a string representing the year.
    end_year : int or str
        The end year of the range (inclusive). Can be a string representing the year.
    return_days : bool, optional
        If True, return the number of days in each year. Otherwise, return a dictionary
        with leap year status for each year in the range (default is False).

    Returns
    -------
    dict or list
        - If `return_days` is False: A dictionary where the keys are years
          from `start_year` to `end_year`, and the values are booleans 
          (True if the year is a leap year, otherwise False).
        - If `return_days` is True: A list of the number of days for each year in the range.
    """
    
    # Ensure input years are integers
    start_year = int(start_year)
    end_year = int(end_year)
    
    # Return number of days in each year if requested
    if return_days:
        days_per_year = [len(pd.date_range(f'{year}', f'{year+1}', inclusive="left"))
                         for year in range(start_year, end_year+1)]
        return days_per_year
    
    # Otherwise, return a dictionary with leap year status
    leap_years = {year: calendar.isleap(year) for year in range(start_year, end_year+1)}
    return leap_years

        
        
def nearest_leap_year(year):
    """
    Finds the nearest leap year to a given year.

    If the given year is not a leap year, this function will search for the closest leap year 
    within a range of four years before or after the input year. If there are two equally 
    distant leap years, both are returned.

    Parameters
    ----------
    year : int
        The year for which to find the nearest leap year.

    Returns
    -------
    int or str
        The nearest leap year. If two leap years are equally close,
        a string with both years is returned.
    """
    
    if leap_year_detector(year, year)[year]:
        return year

    # Search range of years within 4 years before and after the given year
    for offset in range(1, 5):
        if calendar.isleap(year - offset):
            return year - offset
        elif calendar.isleap(year + offset):
            return year + offset

    return f"No nearby leap year found in the given range for year {year}"  # This case should be rare


# Date/time ranges #
#------------------#

def week_range(date):
    """
    Finds the first and last date of the week for a given date.
    
    This function calculates the range of the week (Monday to Sunday) 
    where the given date falls, based on ISO calendar conventions.
    
    In this convention, the day of the week ('dow' === 'day of week') 
    is 'Mon' = 1, ... , 'Sat' = 6, 'Sun' = 7.
    
    Parameters
    ----------
    date : datetime.date, datetime.datetime, np.datetime64, pd.Timestamp.
         The date for which the week range is calculated. Supports standard Python 
         date/datetime objects, pandas Timestamps, and numpy datetime64 types.

    Returns
    -------
    tuple
        A tuple containing two pd.Timestamp objects:
        - start_date: The first day of the week (Monday).
        - end_date: The last day of the week (Sunday).

    Raises
    ------
    ValueError
        If the provided date is not a pandas Timestamp object.
    """
    
    if isinstance(date, (datetime.date, datetime.datetime, np.datetime64, pd.Timestamp)):
        dow = date.isocalendar().weekday
        
        # Calculate the start of the week (Monday)
        start_date = date - pd.Timedelta(days=dow - 1)
        
        # Calculate the end of the week (Sunday)
        end_date = start_date + pd.Timedelta(days=6)
        
        return (start_date, end_date)
    else:
        raise TypeError("Unsupported data type",
                        "The date provided must be a datetime.date, datetime.datetime, "
                        "np.datetime64 or pd.Timestamp object.")


#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported file extensions for calendar standardisations #
SUPPORTED_FILE_EXTS_PANDAS = ['csv', 'xlsx']
