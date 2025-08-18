#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np
from pandas import Series, DataFrame

#------------------------#
# Import project modules #
#------------------------#

#------------------#
# Define functions # 
#------------------#

# Sorting algorithms #
#--------------------#

# Basic #
#-#-#-#-#

# Helpers #
def _pos_swapper(A, x, y):
    """
    Swap two elements in a list or numpy array at specified positions.
    
    This function exchanges the values located at positions `x` and `y` in the 
    provided list or numpy array `A`. It operates in-place, meaning the input
    object is modified directly without returning a new object.
    
    Parameters
    ----------
    A : list | numpy.ndarray
        The list or numpy array where the elements will be swapped.
    x : int
        The index of the first element to be swapped.
    y : int
        The index of the second element to be swapped.
    
    Returns
    -------
    None
        The input array `A` is modified in-place.
    
    Raises
    ------
    IndexError
        If `x` or `y` are out of bounds for the list or array `A`.
    
    Examples
    --------
    >>> A = [1, 2, 3, 4]
    >>> _pos_swapper(A, 0, 2)
    >>> A
    [3, 2, 1, 4]
    
    >>> A = np.array([10, 20, 30, 40])
    >>> _pos_swapper(A, 1, 3)
    >>> A
    array([10, 40, 30, 20])
    """
    A[x], A[y] = A[y], A[x]

def _flatten_generator(lst):
    """
    Recursively flatten a nested list using a generator.
    
    This helper function takes a potentially nested list and yields
    each element in a flattened manner. It handles lists of arbitrary
    depth, ensuring that all nested elements are extracted in a single
    flat sequence.
    
    Parameters
    ----------
    lst : list
        The list to be flattened, which may contain nested lists.
    
    Yields
    ------
    item
        Each non-list element from the nested structure, in order.
    """
    for item in lst:
        if isinstance(item, list):
            yield from _flatten_generator(item)
        else:
            yield item

# Main #
def sort_values_standard(array, key=None, reverse=False,
                         axis=-1, order=None,
                         want_numpy_array=False):
    """
    Sort values in an array (list, numpy, or pandas Series) using np.sort or list.sort.
    
    Parameters
    ----------
    array : list | numpy.ndarray | pandas.Series
        Array containing values to be sorted.
    key : function, optional
        Key function to sort list items by their function values. Only for lists.
    reverse : bool
        Sort in ascending (False) or descending (True) order. Default is False.
    axis : int, optional
        Axis to sort for numpy arrays. Default is -1.
    order : str | list[str], optional
        Order fields for structured numpy arrays. Default is None.
    want_numpy_array : bool
        Return the result as a numpy array. Default is False.
          
    Returns
    -------
    sorted_array : list | numpy.ndarray | pandas.Series
        Sorted array or list.

    Examples
    --------
    >>> sort_values_standard([3, 1, 2])
    [1, 2, 3]

    >>> sort_values_standard(np.array([10, 5, 7]), reverse=True)
    array([10, 7, 5])

    >>> sort_values_standard(pd.Series([4, 2, 8]), reverse=True)
    2    8
    0    4
    1    2
    dtype: int64
    """
    # Check input type (allow pandas Series as well)
    if isinstance(array, (list, np.ndarray, Series)):
        if isinstance(array, list):
            array.sort(key=key, reverse=reverse)
        elif isinstance(array, np.ndarray):
            array = np.sort(array, axis=axis, order=order)[::-1] if reverse else np.sort(array, axis=axis, order=order)
        elif isinstance(array, Series):
            array = array.sort_values(ascending=not reverse)
        return np.array(array) if want_numpy_array else array
    else:
        raise TypeError(f"Unsupported type '{type(array)}' for sorting.")

def sort_1d_basic(arr, reverse=False):
    """
    Sort a 1D array or list without external libraries (basic function).
    
    Parameters
    ----------
    arr : list | numpy.ndarray of int | float | complex | str
        1D array or list with values to sort.
    reverse : bool
        Sort in ascending (False) or descending (True) order. Default is False.
    
    Returns
    -------
    arr : list | numpy.ndarray
        Sorted array.
    """
    # Flatten the array if N >= 2 (irrespective of having inhomogeneous parts) #
    if isinstance(arr, np.ndarray):
        if arr.ndim >= 2:
            arr = arr.flatten()
    elif isinstance(arr, list):
        arr = flatten_list(arr)

    # Operations #
    for i in range(len(arr)):
        current = i
        for k in range(i+1, len(arr)):
            if not reverse and arr[k] < arr[current]:
                current = k
            elif reverse and arr[k] > arr[current]:
                current = k
        _pos_swapper(arr, current, i)
    return arr


# Advanced #
#-#-#-#-#-#-

def sort_rows_by_column(array, ncol, reverse=False, order=None): 
    """*
    Sort a 2D array by a specific column, preserving row structure.    
    The mechanism preserves the original structure of each row, 
    only sorting based on the specified column. 
    This is especially useful when the user needs to sort an array by a single column,
    without altering the rows.
    
    Parameters
    ----------
    array : list | numpy.ndarray | pandas.DataFrame
        2D array to sort.
    ncol : int
        Column index to sort by.
    reverse : bool
        If True, sort in descending order. Default is False (ascending).
    order : str | list[str], optional
        Field order for structured arrays. Default is None.
    
    Returns
    -------
    sorted_array : numpy.ndarray | pandas.DataFrame
        Sorted array by column.

    Examples
    --------
    >>> array = np.array([[6, 4, 2, 3],
                          [3, 9, 7, 1],
                          [4, 6, 4, 5]])
    >>> sort_rows_by_column(array, ncol=0)
    array([[3, 9, 7, 1],
           [4, 6, 4, 5],
           [6, 4, 2, 3]])

    >>> sort_rows_by_column(array, ncol=0, reverse=True)
    array([[6, 4, 2, 3],
           [4, 6, 4, 5],
           [3, 9, 7, 1]])
    """
    if isinstance(array, DataFrame):
        return array.sort_values(by=array.columns[ncol], ascending=not reverse)
    
    if isinstance(array, (list, np.ndarray)):
        array = np.array(array) if isinstance(array, list) else array
        sorted_indices = np.argsort(array[:, ncol])[::-1] if reverse else np.argsort(array[:, ncol])
        return array[sorted_indices]
    raise TypeError(f"Unsupported type '{type(array)}' for sorting.")


def sort_columns_by_row(array, nrow, reverse=False): 
    """
    Sort columns of a 2D array by a specific row, preserving column structure.
    Just like `sort_rows_by_column`, this function sorts the columns based on 
    the values in the specified row while maintaining the column structure.
    
    Parameters
    ----------
    array : list | numpy.ndarray | pandas.DataFrame
        2D array to sort.
    nrow : int
        Row index to sort by.
    reverse : bool
        If True, sort in descending order. Default is False (ascending).
    
    Returns
    -------
    sorted_array : numpy.ndarray | pandas.DataFrame
        Array sorted by the specified row.

    Examples
    --------
    >>> array = np.array([[6, 4, 2, 3],
                          [3, 9, 7, 1],
                          [4, 6, 4, 5]])
    >>> sort_columns_by_row(array, nrow=0)
    array([[2, 3, 4, 6],
           [7, 1, 9, 3],
           [4, 5, 6, 4]])

    >>> sort_columns_by_row(array, nrow=0, reverse=True)
    array([[6, 4, 3, 2],
           [3, 9, 1, 7],
           [5, 4, 6, 4]])
    """
    if isinstance(array, DataFrame):
        return array.T.sort_values(by=array.T.columns[nrow], ascending=not reverse).T
    
    array = np.array(array).T
    sorted_array = sort_rows_by_column(array, ncol=nrow, reverse=reverse).T
    return sorted_array

# Flipping or reversing #
#-----------------------#

# Basic #
#-#-#-#-#

def revert_1d_basic(arr, procedure="index"):
    """
    Reverses a 1D array in-place.

    Parameters
    ----------
    arr : list | numpy.ndarray
        The array to reverse.
    procedure : str
        The procedure to use for reversing the array.
    
    Returns
    -------
    numpy.ndarray
        The reversed array.
    """
    # Parameter validation #
    if procedure not in FLIP_BASIC_OPTIONS:
        raise ValueError(f"Invalid procedure '{procedure}' for reversing an array. "
                         f"Choose from: {FLIP_BASIC_OPTIONS}.")
    
    # Flatten the array if N >= 2 (irrespective of having inhomogeneous parts) #
    if isinstance(arr, np.ndarray):
        if arr.ndim >= 2:
            arr = arr.flatten()
    elif isinstance(arr, list):
        arr = flatten_list(arr)

    # Operations #
    arr_len = len(arr)-1
    if procedure == "iterative":
        for i in range(arr_len//2):
            _pos_swapper(arr, i, arr_len-i)
    elif procedure == "index":
        arr = arr[::-1]
    return arr


# Advanced #
#-#-#-#-#-#-

def flip_array(array, procedure="numpy_default", axis=None):
    """
    Flip a numpy array or list along a specified axis.

    Parameters
    ----------
    array : list | numpy.ndarray
        The array to flip.
    procedure : str
        The procedure to use for flipping the array.
        Options:
            - "numpy_default": Use numpy.flip.
            - "numpy_lr": Use numpy.fliplr (equivalent to numpy.flip(array, axis=1)).
            - "numpy_ud": Use numpy.flipud (equivalent to numpy.flip(array, axis=0)).
            - "index_lr": Use left-right list slicing (equivalent to array[:,::-1]).
            - "index_ud": Use up-down list slicing (equivalent to array[::-1,:]).
    axis : int, optional
        The axis to flip the array along. Default is None.
    """
    if procedure not in FLIP_ADVANCED_OPTIONS:
        raise ValueError(f"Invalid procedure '{procedure}' for flipping an array. "
                         f"Choose from: {FLIP_ADVANCED_OPTIONS}.")
    
    return ADVANCED_FLIP_DICT[procedure](array, axis=axis)


# Inserting, Extending, and Removing Data #
#-----------------------------------------#

def insert_values(x, index, values, axis=None):
    """
    Insert values into a list, numpy array, or pandas Series at a specific index.
    
    Parameters
    ----------
    x : list | numpy.ndarray | pandas.Series
        Object to insert values into.
    index : int
        Position to insert values.
    values : list | numpy.ndarray | pandas.Series
        Values to insert.
    axis : int, optional
        Axis along which to insert values for numpy arrays.
    
    Returns
    -------
    appended_array : numpy.ndarray | list
        Updated array with inserted values.

    Examples
    --------
    >>> insert_values([1, 2, 3], 1, 100)
    [1, 100, 2, 3]

    >>> insert_values(np.array([1, 2, 3]), 1, 100)
    array([  1, 100,   2,   3])

    >>> insert_values(pd.Series([1, 2, 3]), 1, 100)
    0      1
    1    100
    1      2
    2      3
    dtype: int64
    """
    if isinstance(x, (list, np.ndarray, Series)):
        if isinstance(x, list):
            x.insert(index, values)
        elif isinstance(x, np.ndarray):
            x = np.insert(x, index, values, axis=axis)
        elif isinstance(x, Series):
            x = x.append(Series(values)).sort_index()
        return x
    raise TypeError(f"Unsupported type '{type(x)}' for insertion.")


def extend_array(obj, obj2extend, np_axis=None):
    """
    Extend a list or concatenate a NumPy array with another list or array.
    
    Parameters
    ----------
    obj : list | numpy.ndarray | pandas.Series
        The original list, numpy array, or pandas Series to be extended.
    obj2extend : list | numpy.ndarray | pandas.Series
        The object to extend `obj` with.
    np_axis : int, optional
        Axis along which to concatenate numpy arrays. Default is None.
    
    Returns
    -------
    Extended list | numpy.ndarray | pandas.Series.

    Examples
    --------
    >>> extend_array([1, 2, 3], [4, 5])
    [1, 2, 3, 4, 5]

    >>> extend_array(np.array([1, 2, 3]), np.array([4, 5]), np_axis=0)
    array([1, 2, 3, 4, 5])

    >>> extend_array(pd.Series([1, 2, 3]), pd.Series([4, 5]))
    0    1
    1    2
    2    3
    3    4
    4    5
    dtype: int64
    """
    if isinstance(obj, list):
        obj.extend(obj2extend)
    elif isinstance(obj, np.ndarray):
        obj = np.concatenate((obj, obj2extend), axis=np_axis)
    elif isinstance(obj, Series):
        obj = obj.append(Series(obj2extend)).sort_index()
    return obj


def remove_elements(array, idx2access, axis=None):    
    """
    Remove elements from a list, numpy array, or pandas Series using indices.
    
    Parameters
    ----------
    array : list | numpy.ndarray | pandas.Series
        List, numpy array, or pandas Series from which elements will be removed.
    idx2access : int | list | numpy.ndarray
        Indices to access the elements that will be removed. For lists, multiple
        indices are now allowed.
    axis : int, optional
        Axis along which to remove elements for numpy arrays. Default is None.
    
    Returns
    -------
    Updated list | numpy.ndarray | pandas.Series with specified elements removed.

    Examples
    --------
    >>> remove_elements([1, 2, 3, 4], [1, 3])
    [1, 3]

    >>> remove_elements(np.array([10, 20, 30, 40]), [1, 3])
    array([10, 30])

    >>> remove_elements(pd.Series([10, 20, 30, 40]), [0, 2])
    1    20
    3    40
    dtype: int64
    """
    if isinstance(array, list):
        if isinstance(idx2access, int):  # Handle single index
            array.pop(idx2access)
        elif isinstance(idx2access, (list, np.ndarray)):  # Handle multiple indices
            for index in sorted(idx2access, reverse=True):
                if index < 0 or index >= len(array):
                    raise IndexError(f"Index {index} is out of range for list of size {len(array)}.")
                del array[index]
        else:
            raise TypeError("For list inputs, indices must be an integer or a list/array of integers.")
    elif isinstance(array, np.ndarray):
        array = np.delete(array, idx2access, axis=axis)
    elif isinstance(array, Series):
        array = array.drop(idx2access)
    else:
        raise TypeError(f"Unsupported type '{type(array)}' for removal.")
    return array

# Extracting Unique Values #
#--------------------------#

# Basic #
#-#-#-#-#

def flatten_list(lst, return_list=True, sort=False, reverse=False):
    """
    Recursively flatten a nested list.
    
    This function takes a potentially nested list and either yields each element
    in a flattened manner (if return_list=False) or returns a complete flattened list
    (if return_list=True). It handles lists of arbitrary depth, ensuring that all 
    nested elements are extracted in a single flat sequence.
    
    Parameters
    ----------
    lst : list
        The list to be flattened, which may contain nested lists.
    return_list : bool, optional
        If True, return a list; if False, return a generator. Default is True.
    sort : bool, optional
        Whether to sort the flattened elements. Only applicable when return_list=True.
        Default is False.
    reverse : bool, optional
        Whether to sort in descending order. Only applicable if sort=True and 
        return_list=True. Default is False.
    
    Returns
    -------
    list | generator
        If return_list=True, returns a list of flattened elements (optionally sorted).
        If return_list=False, returns a generator yielding flattened elements.
    
    Yields
    ------
    item (when return_list=False)
        Each non-list element from the nested structure, in order.
    
    Examples
    --------
    >>> flatten_list([1, [2, 3], [4, [5, 6]]])
    [1, 2, 3, 4, 5, 6]
    
    >>> flatten_list([3, [1, 2], [6, [4, 5]]], sort=True)
    [1, 2, 3, 4, 5, 6]
    
    >>> flatten_list([1, [2, 3], [4, [5, 6]]], return_list=True)
    [1, 2, 3, 4, 5, 6]
    """
    if return_list:
        flattened = list(_flatten_generator(lst))
        if sort:
            return sort_1d_basic(flattened, reverse=reverse)
        return flattened
    else:
        return _flatten_generator(lst)

def extract_1d_unique_basic(arr, procedure="dict", sort=False, reverse=False):
    """
    Extract unique values from an array or list.
    
    This function flattens the input if it is a Numpy array with dimensions 
    greater than or equal to 2, or if it is a list, regardless of whether 
    the list contains inhomogeneous parts (e.g., [1, [2, 3], 4]).
    
    Parameters
    ----------
    arr : list | numpy.ndarray
        The input array or list from which to extract unique values. If the 
        input is a Numpy array with N >= 2 dimensions, it will be flattened. 
        Similarly, if the input is a list, it will be recursively flattened 
        to handle any nested lists.
    procedure : {'dict', 'list', 'set'}, optional
        The method to use for extracting unique values. Default is 'dict'.
    sort : bool, optional
        Whether to sort the unique values. Default is False.
    reverse : bool, optional
        Whether to sort in descending order. Only applicable if sort is True.
    
    Returns
    -------
    unique_val_arr : list
        A list of unique values from the input array or list. If `sort` is True,
        the list is sorted in ascending order by default, or in descending order
        if `reverse` is also True. If `sort` is False, the order of unique values
        is determined by the order of their first appearance in the input.
    
    Raises
    ------
    ValueError
        If 'sort' is False and 'reverse' is True.
    """
    # Parameter validation #
    if not sort and reverse:
        raise ValueError("If keyword argument 'sort' is set to False, "
                         "'reverse' is not allowed to be True.")
    
    if procedure not in PROCEDURE_OPTIONS:
        raise ValueError(f"Invalid procedure '{procedure}' for extracting unique values. "
                         f"Choose from: {PROCEDURE_OPTIONS}.")
    
    # Flatten the array if N >= 2 (irrespective of having inhomogeneous parts) #
    if isinstance(arr, np.ndarray):
        if arr.ndim >= 2:
            arr = arr.flatten()
    elif isinstance(arr, list):
        arr = flatten_list(arr)

    # Operations #
    if procedure == "dict":
        unique_key_dict = dict.fromkeys(arr)
        unique_val_arr = list(unique_key_dict.keys())
    
    elif procedure == "list":
        unique_val_arr = []
        for num in arr:
            if num not in unique_val_arr:
                unique_val_arr.append(num)
    
    elif procedure == "set":
        unique_val_arr = list(set(arr))
                
    if sort:
        return sort_1d_basic(unique_val_arr, reverse)
    return unique_val_arr

#--------------------------#
# Parameters and constants #
#--------------------------#

# Procedure options #
#-------------------#

# Array flipping #
FLIP_BASIC_OPTIONS = ["iterative", "index"]

# Unique values extraction #
PROCEDURE_OPTIONS = ["dict", "list", "set"]

# Switch case dictionaries #
#--------------------------#

# Array flipping #
ADVANCED_FLIP_DICT = {
    "numpy_default": lambda array, axis: np.flip(array, axis=axis),
    "numpy_lr": lambda array: np.fliplr(array),
    "numpy_ud": lambda array: np.flipud(array),
    "index_lr": lambda array: array[:,::-1],
    "index_ud": lambda array: array[::-1,:]
}

FLIP_ADVANCED_OPTIONS = ADVANCED_FLIP_DICT.keys()
