#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Goal**

This module provides functions to perform conversions between various number bases.
The supported bases include binary, octal, decimal, and hexadecimal, as well as
arbitrary bases.
"""

#------------------------#
# Import project modules # 
#------------------------#

from pygenutils.strings.string_handler import find_substring_index, substring_replacer

#------------------#
# Define functions #
#------------------#

# Validator helpers #
#-------------------#

# Input format checkers #
#-#-#-#-#-#-#-#-#-#-#-#-#

def _check_input_str(x):
    """
    Ensures the input number is in string format.

    Parameters
    ----------
    x : int | str
        The input number.

    Returns
    -------
    x_str : str
        The input number as a string.
    """
    if isinstance(x, int):
        x_str = str(x)
    else:
        x_str = x
    return x_str

def _check_input_binary(b):
    """
    Checks if the input binary number is in the correct format.

    Parameters
    ----------
    b : str
        The binary number as a string. It can contain the 'b' or '0b' prefix.

    Returns
    -------
    str
        The binary number as a string without the 'b' or '0b' prefix.
    """
    b_clean = substring_replacer(substring_replacer(b, "b", ""), "0b", "")
    are_only_binaries = find_substring_index(b_clean, "^[01]+$")
    if are_only_binaries == -1:
        raise ValueError("The input binary number is not in the correct format.")
    return b_clean


def _check_input_int(x):
    """
    Ensures the input number is in integer format.

    Parameters
    ----------
    x : int | str
        The input number.

    Returns
    -------
    x_int : int
        The input number as an integer.
    """
    if isinstance(x, int):
        x_int = x
    else:
        if substring_replacer(x, '-', '').isdigit():
            x_int = int(x)
        else:
            raise ValueError("The input value will not be convertible to an integer.")
    return x_int

# Procedure checker #
#-#-#-#-#-#-#-#-#-#-#

def _procedure_checker(arg, procedure_opts):
    """
    Checks if the provided procedure is valid.

    Parameters
    ----------
    arg : str
        The procedure to check.

    Raises
    ------
    ValueError : If the procedure is not valid.
    """
    if arg not in procedure_opts:
        raise ValueError(f"Unsupported procedure. Choose one from {procedure_opts}.")
        
# Frequently used bases #
#-----------------------#

# Basic #
#-#-#-#-#

def dec2bin_basic(n):
    """
    Converts a decimal number to binary, using mathematical operations
    by definition (hence the name 'basic').

    Parameters
    ----------
    n : int
        The decimal number to convert.
        
    Returns
    -------
    str
        The binary representation of the input number.
    """
    n_checked = _check_input_int(n)
    b = "" # or '_bin', so that we understand the var name better?
    while n_checked >= 1:
        floordiv, mod = divmod(n_checked,2)
        b += str(mod)
        n_checked //= 2
    return b[::-1]

# Advanced #
#-#-#-#-#-#-

# From decimal to bases 2, 8, 16 #
def base2bin(n, procedure="format_string", zero_pad=4):
    """
    Converts a number to binary.

    Parameters
    ----------
    n : int
        The input number.
    procedure : str
        The procedure to use for conversion ('default' or 'format_string').
    zero_pad : int
        The number of zeros to pad (used with 'format_string').

    Returns
    -------
    str
        The binary representation of the input number.
    """
    _procedure_checker(procedure, NUMBER_CONVERSION_PROCEDURE_OPTS)

    if procedure == "default":
        n_bin = bin(n)
    elif procedure == "format_string":
        n_bin = f"{n:0{zero_pad}b}"
    return n_bin

def base2oct(n, procedure="format_string", zero_pad=4):
    """
    Converts a number to octal.

    Parameters
    ----------
    n : int
        The input number.
    procedure : str
        The procedure to use for conversion ('default' or 'format_string').
    zero_pad : int
        The number of zeros to pad (used with 'format_string').

    Returns
    -------
    str
        The octal representation of the input number.
    """
    _procedure_checker(procedure, NUMBER_CONVERSION_PROCEDURE_OPTS)

    if procedure == "default":
        n_oct = oct(n)
    elif procedure == "format_string":
        n_oct = f"{n:0{zero_pad}o}"
    return n_oct

def base2hex(n, procedure="format_string", zero_pad=4):
    """
    Converts a number to hexadecimal.

    Parameters
    ----------
    n : int
        The input number.
    procedure : str
        The procedure to use for conversion ('default' or 'format_string').
    zero_pad : int
        The number of zeros to pad (used with 'format_string').

    Returns
    -------
    str
        The hexadecimal representation of the input number.
    """
    _procedure_checker(procedure, NUMBER_CONVERSION_PROCEDURE_OPTS)

    if procedure == "default":
        if isinstance(n, float):
            n_hex = n.hex()
        else:
            n_hex = hex(n)
    elif procedure == "format_string":
        n_hex = f"{n:0{zero_pad}x}"
    return n_hex

# From above bases to decimal #
def bin2dec(n_bin):
    """
    Converts a binary number to decimal.

    Parameters
    ----------
    n_bin : str
        The binary number as a string.

    Returns
    -------
    int
        The decimal equivalent of the binary number.
    """
    if isinstance(n_bin, int):
        n = n_bin
    else:
        n = int(n_bin, base=2)
    return n

def bin2dec_basic(b, procedure="loop"):
    """
    Converts a binary number to decimal, using mathematical operations
    by definition (hence the name 'basic').

    Parameters
    ----------
    b : str
        The binary number as a string.
        It can contain the 'b' or '0b' prefix. If so, the function 
        will take into account the string without the prefix.
    procedure : str
        The procedure to use for conversion. Options are:
        - 'list_comprehension': Uses a list comprehension with enumerate for a more
          functional approach. Might be more memory intensive for large numbers.
        - 'loop': Uses a traditional for loop with enumerate. More memory efficient
          as it doesn't create an intermediate list.

    Returns
    -------
    int
        The decimal equivalent of the binary number.
    """

    # Validations #
    ###############

    # Procedure #
    _procedure_checker(procedure, BIN2DEC_PROCEDURE_OPTS)

    # Number input #
    b_checked = _check_input_binary(b)
    lb = len(b_checked)

    # Calculation #
    ###############

    if procedure == "list_comprehension":
        summands_iter = [int(b_checked[i]) * 2 ** pos for pos, i in enumerate(range(lb-1,-1,-1))]
        res = sum(summands_iter)

    elif procedure == "loop":
        res = 0
        for pos, i in enumerate(range(lb-1,-1,-1)):
            res += int(b_checked[i]) * 2 ** pos
        return res


def oct2dec(n_oct):
    """
    Converts an octal number to decimal.

    Parameters
    ----------
    n_oct : str
        The octal number as a string.

    Returns
    -------
    int
        The decimal equivalent of the octal number.
    """
    if isinstance(n_oct, int):
        n = n_oct
    else:
        n = int(n_oct, base=8)
    return n

def hex2dec(n_hex):
    """
    Converts a hexadecimal number to decimal.

    Parameters
    ----------
    n_hex : str
        The hexadecimal number as a string.

    Returns
    -------
    int
        The decimal equivalent of the hexadecimal number.
    """
    if isinstance(n_hex, int):
        n = n_hex
    else:
        n = int(n_hex, base=16)
    return n

# Arbitrary bases #
#-----------------#

def arbitrary2dec(x, base=10):
    """
    Converts a number from an arbitrary base to decimal.

    Parameters
    ----------
    x : str
        The number as a string.
    base : int
        The base of the input number.

    Returns
    -------
    int
        The decimal equivalent of the input number.
    """
    x_checked = _check_input_str(x)
    n = int(x_checked, base=base)
    return n

def convert_among_arbitraries(x, base):
    """
    Converts a number from one arbitrary base to another.

    Parameters
    ----------
    x : str
        The number as a string.
    base : int
        The base of the input number.

    Returns
    -------
    int
        The number converted to the specified base.
    """
    x_checked = _check_input_str(x)
    y = int(x_checked, base=base)
    return y

#--------------------------#
# Parameters and constants #
#--------------------------#

BIN2DEC_PROCEDURE_OPTS = ['list_comprehension', 'loop']
NUMBER_CONVERSION_PROCEDURE_OPTS = ['default', 'format_string']
