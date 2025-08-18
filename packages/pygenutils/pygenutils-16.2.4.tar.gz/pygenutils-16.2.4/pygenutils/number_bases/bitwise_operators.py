#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module provides functions to perform bitwise logical operations
and shift operations. The results are provided in both binary and decimal
formats. Each function utilises custom converters to switch between 
binary and decimal systems.

Functions
---------
- bitwise_and(n1, n2): Performs a bitwise AND operation.
- bitwise_or(n1, n2): Performs a bitwise OR operation.
- bitwise_xor(n1, n2): Performs a bitwise XOR operation.
- rightwards_bitshift(n, despl): Performs a rightwards bitwise shift.
- leftwards_bitshift(n, despl): Performs a leftwards bitwise shift.

Note
----
All functions return a tuple containing the result in both binary and 
decimal formats. The conversion functions `base2bin` and `bin2dec` 
from the `numeral_systems.base_converters` module are used for this 
purpose.
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.numeral_systems.base_converters import base2bin, bin2dec

#-------------------------#
# Define custom functions #
#-------------------------#

def bitwise_and(n1, n2):
    """
    Performs a bitwise AND operation on two integers.

    Parameters
    ----------
    n1 : int
        First integer operand.
    n2 : int
        Second integer operand.

    Returns
    -------
    tuple
        A tuple containing the result in binary and decimal formats.
    """
    res_bitwise_and = n1 & n2
    res_bin = base2bin(res_bitwise_and)
    res_dec = bin2dec(res_bin)
    return (res_bin, res_dec)

def bitwise_or(n1, n2):
    """
    Performs a bitwise OR operation on two integers.

    Parameters
    ----------
    n1 : int
        First integer operand.
    n2 : int
        Second integer operand.

    Returns
    -------
    tuple
        A tuple containing the result in binary and decimal formats.
    """
    res_bitwise_or = n1 | n2
    res_bin = base2bin(res_bitwise_or)
    res_dec = bin2dec(res_bin)
    return (res_bin, res_dec)

def bitwise_xor(n1, n2):
    """
    Performs a bitwise XOR operation on two integers.

    Parameters
    ----------
    n1 : int
        First integer operand.
    n2 : int
        Second integer operand.

    Returns:
    tuple: A tuple containing the result in binary and decimal formats.
    """
    res_bitwise_xor = n1 ^ n2
    res_bin = base2bin(res_bitwise_xor)
    res_dec = bin2dec(res_bin)
    return (res_bin, res_dec)

def rightwards_bitshift(n, despl):
    """
    Performs a rightwards bitwise shift on an integer.

    Parameters
    ----------
    n : int
        The integer to be shifted.
    despl : int
        The number of positions to shift.

    Returns
    -------
    tuple
        A tuple containing the result in binary and decimal formats.
    """
    res_right_shift = n >> despl
    res_bin = base2bin(res_right_shift)
    res_dec = bin2dec(res_bin)
    return (res_bin, res_dec)

def leftwards_bitshift(n, despl):
    """
    Performs a leftwards bitwise shift on an integer.

    Parameters
    ----------
    n : int
        The integer to be shifted.
    despl : int
        The number of positions to shift.

    Returns
    -------
    tuple
        A tuple containing the result in binary and decimal formats.
    """
    res_left_shift = n << despl
    res_bin = base2bin(res_left_shift)
    res_dec = bin2dec(res_bin)
    return (res_bin, res_dec)
