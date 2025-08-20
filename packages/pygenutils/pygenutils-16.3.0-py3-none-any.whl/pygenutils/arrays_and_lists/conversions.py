#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_type_str
from pygenutils.arrays_and_lists.data_manipulation import flatten_list

#------------------#
# Define functions #
#------------------#

# Data types #
#------------#
        
def convert_data_type(obj_data, old_type, new_type, colnames=None, convert_to_list=False):
    """
    Function that converts the original data type of the values in a given object 
    (numpy array, pandas DataFrame/Series) to the desired one.
    If the new data type is the same as the original, the function returns 
    the object unchanged, and prints a message showing the latter.

    Parameters
    ----------
    obj_data : pandas.DataFrame | pandas.Series | numpy.ndarray | list
        Object containing the data to be converted.
    old_type : str
        Current type of the object's values.
    new_type : str
        Type to which the data should be converted.
    colnames : str | list[str] | '__all_columns__', optional
        Column(s) to apply conversion in case of pandas DataFrame.
        If '__all_columns__', conversion will be applied to all columns.
        Not applicable for pandas Series or numpy arrays.
    convert_to_list : bool, optional
        If True, converts the result to a list before returning.
    
    Returns
    -------
    obj_data : pandas.DataFrame | pandas.Series | numpy.ndarray | list
        Object with the converted data type, or unchanged if no conversion was made.

    Raises
    ------
    TypeError
        If the conversion to the new type cannot be done or if the object type is invalid.
    KeyError
        If specified columns are not found in pandas DataFrame.
    """
    # Get input object's type
    obj_type = get_type_str(obj_data)
    
    # Handle pandas DataFrames
    if obj_type == "DataFrame":
        if colnames is None:
            raise ValueError("Please specify 'colnames' for pandas DataFrame.")
        if colnames == '__all_columns__':  # apply to all columns
            colnames = obj_data.columns
        elif isinstance(colnames, str):
            colnames = [colnames]  # convert to list for consistency
        elif isinstance(colnames, list):
            pass
        else:
            raise TypeError("'colnames' must be a str | list[str] | '__all_columns__'.")

        # Find missing columns
        missing_cols = [col for col in colnames if col not in obj_data.columns]
        if missing_cols:
            raise KeyError(f"The following columns were not found: {missing_cols}")

        # Apply conversion
        data_converted = obj_data.copy()
        for col in colnames:
            if obj_data[col].dtype == old_type:
                try:
                    data_converted[col] = obj_data[col].astype(new_type)
                except:
                    raise TypeError(f"Cannot convert column '{col}' to type '{new_type}'.")
            else:
                print(f"Column '{col}' data type unchanged.")
        
        return data_converted

    # Handle pandas Series
    elif obj_type == "Series":       
        if obj_data.dtype == old_type:
            try:
                return obj_data.astype(new_type)
            except:
                raise TypeError(f"Cannot convert Series to type '{new_type}'.")
        else:
            print("Series data type unchanged.")
            return obj_data

    # Handle numpy arrays and lists
    elif obj_type in ["ndarray", "list"]:
        try:
            # Handle nested lists by flattening them first
            if isinstance(obj_data, list):
                obj_data = np.array(flatten_list(obj_data))
            else:
                obj_data = np.array(obj_data)  # convert to numpy array if it's not already
            if obj_data.dtype == old_type:
                try:
                    data_converted = obj_data.astype(new_type)
                except:
                    raise TypeError(f"Cannot convert array to type '{new_type}'.")
                if convert_to_list:
                    return list(data_converted)
                return data_converted
            else:
                print("Array data type unchanged.")
                if convert_to_list:
                    return list(obj_data)
                return obj_data
        except Exception as e:
            raise TypeError(f"Error occurred during conversion: {e}")

    # Raise TypeError if the object type is not supported
    else:
        raise TypeError("Unsupported object type. "
                        "Expected pandas.DataFrame | pandas.Series | numpy.ndarray | list.")

            
def combine_arrays(array_of_lists):
    """
    Combine a list of NumPy arrays or lists into a single NumPy array.
    
    This function takes a list of NumPy arrays (or lists) and combines them 
    into a single NumPy array. It supports arrays with up to 3 dimensions.
    If the arrays have inhomogeneous lengths, it uses `np.hstack` to flatten 
    and concatenate the arrays. Nested lists are automatically flattened.
    
    Parameters
    ----------
    array_of_lists : list[numpy.ndarray | list]
        A list of NumPy arrays or lists to be combined. Lists can be nested.
    
    Returns
    -------
    array : numpy.ndarray
        A single NumPy array formed by combining the input arrays.
    
    Raises
    ------
    ValueError
        - If the arrays in the list have more than 3 dimensions.
        - If the shapes of the arrays are inconsistent and cannot be combined.
    
    Example
    -------
    >>> import numpy as np
    >>> array1 = np.array([[1, 2], [3, 4]])
    >>> array2 = np.array([[5, 6], [7, 8]])
    >>> array_of_lists = [array1, array2]
    >>> result = combine_arrays(array_of_lists)
    >>> print(result)
    [[1 2]
     [3 4]
     [5 6]
     [7 8]]
    
    >>> # With nested lists
    >>> nested_list = [[1, 2], [[3, 4], 5]]
    >>> result = combine_arrays(nested_list)
    >>> print(result)
    [1 2 3 4 5]
    
    Notes
    -----
    - If the arrays have different shapes, they are concatenated and flattened 
      using `np.hstack`.
    - Nested lists are automatically flattened before processing.
    - This function assumes that the input contains valid NumPy arrays or lists.
    """    
    # Handle nested lists by flattening the top-level structure first
    processed_arrays = []
    for item in array_of_lists:
        if isinstance(item, list):
            # Check if this is a nested list structure
            try:
                # Try to convert to numpy array directly first
                arr = np.array(item)
                processed_arrays.append(arr)
            except ValueError:
                # If direct conversion fails due to irregular nesting,
                # flatten the list and convert
                flattened = flatten_list(item)
                processed_arrays.append(np.array(flattened))
        else:
            processed_arrays.append(item)
    
    # Get the list of unique dimensions of the processed arrays #
    dim_list = np.unique([arr.ndim for arr in processed_arrays])
    ld = len(dim_list)
    
    # If all arrays/lists are of the same dimension #
    if ld == 1:
        dims = dim_list[0]
        
        if dims == 2:
            array = np.vstack(processed_arrays)
        elif dims == 3:
            array = np.stack(processed_arrays)
        else:
            raise ValueError("Cannot handle arrays with dimensions greater than 3.")
            
    # If the arrays/lists have inconsistent dimensions #
    else:
        array = np.hstack(processed_arrays)
        
    return array


def flatten_to_string(obj, delim=" ", add_final_space=False):
    """
    Flatten the content of a list, NumPy array, or pandas DataFrame/Series 
    into a single string, where elements are separated by a specified delimiter.

    This method takes an input object (list, NumPy array, pandas DataFrame, or Series),
    flattens it (if needed), converts all elements to strings, and joins them into 
    a single string. Optionally, a final delimiter can be added to the end of the string.
    Handles nested lists automatically.

    Parameters
    ----------
    obj : list | numpy.ndarray | pandas.DataFrame | pandas.Series
        The input object containing data to be flattened and converted to a string.
        Lists can be nested to any depth.
    delim : str, optional
        The delimiter to use for separating elements in the resulting string.
        By default, a space character (' ') is used.
    add_final_space : bool, optional
        If True, adds a delimiter (or space) at the end of the string.
        Default is False.
    
    Returns
    -------
    str
        A single string containing all elements of the input object, 
        separated by the specified delimiter.

    Raises
    ------
    TypeError
        If the input object is not a list | numpy.ndarray | pandas.DataFrame | pandas.Series.

    Example
    -------
    >>> import numpy as np
    >>> arr = np.array([[1, 2], [3, 4]])
    >>> flatten_to_string(arr, delim=',', add_final_space=True)
    '1,2,3,4,'
    
    >>> # With nested lists
    >>> nested = [1, [2, 3], [4, [5, 6]]]
    >>> flatten_to_string(nested, delim='-')
    '1-2-3-4-5-6'
    
    Notes
    -----
    This method is particularly useful for converting arrays or lists of file names 
    into a single string to pass as arguments to shell commands or other processes 
    that require string input. Nested lists are automatically flattened.
    """
    # Get input object type 
    obj_type = get_type_str(obj)
    
    # Validate input type #
    if obj_type not in ["list", "ndarray", "DataFrame", "Series"]:
        raise TypeError("'flatten_to_string' supports list | numpy.ndarray | pandas.DataFrame | pandas.Series.")
    
    # Handle different input types and convert to flattened array
    if obj_type == "list":
        # Use flatten_list for proper nested list handling
        obj_val_array = np.array(flatten_list(obj))
    elif obj_type == "ndarray":
        # NumPy arrays can be flattened directly
        obj_val_array = obj.flatten()
    else:  # DataFrame or Series
        # Convert pandas objects to NumPy array first
        obj_val_array = obj.values
        # Flatten the array if it has more than one dimension
        if hasattr(obj_val_array, "flatten"):
            obj_val_array = obj_val_array.flatten()

    # Convert all elements to strings #
    obj_list = [str(el) for el in obj_val_array]
    
    # Join all elements into a single string #
    allobj_string = delim.join(obj_list)
    
    # Optionally add a final delimiter/space #
    if add_final_space:
        allobj_string += delim
    
    return allobj_string
