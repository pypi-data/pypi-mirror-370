#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**General note**

This module provides functionalities for converting between 
strings, bytes, and integers. It includes functions for converting 
strings to bytes objects using different procedures, converting 
bytes objects to integers, and decoding bytes objects back to string
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.strings.text_formatters import get_type_str

#------------------#
# Define functions #
#------------------#

# Main operations #
#-----------------#

# From strings to bytes objects #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def str2bytes(string, proc="straightforward", encoding="utf-8"):
    """
    Convert a string to a bytes object.

    Parameters
    ----------
    string : str
        The string to convert.
    proc : str, optional
        The procedure to use for conversion.
        Options are:
        - "class": use the bytes class for conversion.
        - "straightforward": use the .encode(encoding) method for conversion.
        Default is "straightforward".
    encoding : str, optional
        The encoding to use. Default is "utf-8".

    Returns
    -------
    bytes_obj: bytes
        The converted bytes object.

    Raises
    ------
    ValueError: If an unsupported conversion procedure is specified.
    TypeError: If the input is not a string.
    """
    if proc not in CONV_TO_BYTE_OPTIONS:
        raise ValueError("Unsupported conversion procedure. "
                         f"Choose one from {CONV_TO_BYTE_OPTIONS}.")
    
    validate_input(string, str)
    
    if proc == "class":
        bytes_obj = bytes(string, encoding)
    else:  # "straightforward"
        bytes_obj = string.encode(encoding)
    
    return bytes_obj


def str_to_byte_array(string, encoding="utf-8"):
    """
    Convert a string to a bytearray object.

    Parameters
    ----------
    string : str
        The string to convert.
    encoding : str, optional
        The encoding to use. Default is "utf-8".

    Returns
    -------
    bytearray_obj: bytearray
        The converted bytearray object.

    Raises
    ------
    TypeError: If the input is not a string.
    """
    validate_input(string, str)
    
    bytearray_obj = bytearray(string, encoding)
    return bytearray_obj


# From bytes objects to integers or list of them #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def bytes_obj_to_int(bytes_obj):
    """
    Convert a bytes or bytearray object to a list of integers.

    Parameters
    ----------
    bytes_obj : bytes | bytearray
        The bytes object to convert.

    Returns
    -------
    list_of_ints: list[int]
        A list of integers representing the byte values.

    Raises
    ------
    TypeError: If the input is not bytes or bytearray.
    """
    validate_input(bytes_obj, (bytes, bytearray))
    
    list_of_ints = list(bytes_obj)
    return list_of_ints


# Decode bytes objects #
#-#-#-#-#-#-#-#-#-#-#-#-

def bytes_obj_to_str(bytes_obj, encoding="utf-8"):
    """
    Decode a bytes or bytearray object to a string.

    Parameters
    ----------
    bytes_obj : bytes | bytearray
        The bytes object to decode.
    encoding : str, optional
        The encoding to use. Default is "utf-8".

    Returns
    -------
    string: str
        The decoded string.

    Raises
    ------
    TypeError: If the input is not bytes or bytearray.
    """
    validate_input(bytes_obj, (bytes, bytearray))
    
    string = bytes_obj.decode(encoding)
    return string

# Validations #
#-------------#

# Input object type validation #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def validate_input(obj, expected_type):
    """
    Validate the type of the input object.

    Parameters
    ----------
    obj : any
        The object to validate.
    expected_type: type | tuple[type, ...]
        The expected type(s) of the object.

    Raises
    ------
    TypeError: If the object is not of the expected type.
    """
    if not isinstance(obj, expected_type):
        obj_type = get_type_str(obj)
        expected_type_str = get_type_str(expected_type)
        raise TypeError(f"Expected '{expected_type_str}', got '{obj_type}'.")


#--------------------------#
# Parameters and constants #
#--------------------------#

# String to bytes object conversion procedures
CONV_TO_BYTE_OPTIONS = ["class", "straightforward"]
