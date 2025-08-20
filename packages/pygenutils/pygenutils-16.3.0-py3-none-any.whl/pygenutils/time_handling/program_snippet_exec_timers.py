#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import os
import time
import timeit

from numpy import round as np_round

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.strings.text_formatters import format_string, print_format_string
from pygenutils.time_handling.time_formatters import parse_float_dt

#------------------#
# Define functions #
#------------------#

# Input validation streamliners #
#-------------------------------#

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

def _validate_precision(frac_precision, min_prec=0, max_prec=9):
    """
    Validate the precision level for a floating-point number and ensure it is within a valid range.
    
    Parameters
    ----------
    frac_precision : int | None
        The desired fractional precision to validate.
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

# Timers #
#--------#

def program_exec_timer(mode, module="time", frac_precision=3):
    """
    General purpose method that measures and returns the execution time
    of a code snippet based on the specified module.

    Parameters
    ----------
    mode : {"start", "stop"}
        Mode to start or stop the timer.
    module : {"os", "time", "timeit"}, optional
        Module to use for timing. Default is "time".
    frac_precision : int | None
        Precision of the fractional seconds (range 0-6).

    Returns
    -------
    str
        Formatted string of the elapsed time if mode is "stop".
        
    Raises
    ------
    ValueError
        If the specified module is not supported or if the mode is invalid.
    """

    global ti
   
    # Input validations #
    #-#-#-#-#-#-#-#-#-#-#
    
    # Module #
    _validate_option("Module", module, MODULE_LIST)

    # Fractional second precision #        
    _validate_precision(frac_precision, max_prec=6)
    
    # Program progression #
    #-#-#-#-#-#-#-#-#-#-#-#
    
    if mode == "start":
        ti = MODULE_OPERATION_DICT[module]()
        
    elif mode == "stop":
        tf = MODULE_OPERATION_DICT[module]()
        elapsed_time = abs(ti - tf)
       
        elapsed_time_kwargs = dict(
            module="str",
            origin="arbitrary",
            frac_precision=frac_precision
            )
            
        return parse_float_dt(elapsed_time, **elapsed_time_kwargs)
    
    else:
        raise ValueError("Invalid mode. Choose 'start' or 'stop'.")

    
def snippet_exec_timer(snippet_str, 
                       repeats=None, 
                       trials=int(1e4), 
                       roundoff=None,
                       format_time_str=False,
                       return_best_time=False):
        
    # Roundoff validation #
    #-#-#-#-#-#-#-#-#-#-#-#

    param_keys = get_caller_args()
    roundoff_arg_pos = find_substring_index(param_keys, "roundoff")
    
    if not isinstance(roundoff, int):
        raise TypeError(format_string(TYPE_ERROR_TEMPLATE, f'{param_keys[roundoff_arg_pos]}'))
    
    # Set keyword argument dictionary for float time parsing #
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

    float_time_parsing_kwargs =  dict(
        module="str",
        origin="arbitrary",
        frac_precision=roundoff
    )

    # Execution time in the specified number of trials with no repeats #
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

    if repeats is None:
        exec_time_norep = timeit.timeit(setup=snippet_str,
                                        number=trials,
                                        globals=globals())
        """
        Equivalent to the following
        ---------------------------
        exec_time_norep = timeit.repeat(snippet_str, repeat=1, number=10000)[0]
        """
        
        if roundoff is not None:
            exec_time_norep = np_round(exec_time_norep, roundoff)
        
        if not format_time_str:
            time_unit_str = SEC_TIME_UNIT_STR
        else:
            exec_time_norep = parse_float_dt(exec_time_norep, **float_time_parsing_kwargs)
            time_unit_str = DEFAULT_TIME_UNIT_STR
        
        # Complete and display the corresponding output information table #
        format_args_exec_timer1 = (time_unit_str, trials, exec_time_norep)
        print_format_string(NOREP_EXEC_TIME_INFO_TEMPLATE, format_args_exec_timer1)
      
    # Execution time in the specified number of trials for several repeats #
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

    else:
        exec_time_rep = timeit.repeat(setup=snippet_str, 
                                      repeat=repeats,
                                      number=trials,
                                      globals=globals())
        
        if roundoff is not None:
            exec_time_rep = np_round(exec_time_rep, roundoff)
        
        # Compute best time
        best_time = min(exec_time_rep) 
        
        # Format floated times to string representation (arbitrary origin)
        if not format_time_str:
            time_unit_str = SEC_TIME_UNIT_STR
        else:
            exec_time_rep = [parse_float_dt(t, **float_time_parsing_kwargs)
                             for t in exec_time_rep]
            best_time = parse_float_dt(best_time, **float_time_parsing_kwargs)
            time_unit_str = DEFAULT_TIME_UNIT_STR
          
        # Complete and display the corresponding output information table
        format_args_exec_timer2 = (time_unit_str, repeats, trials, exec_time_rep)
        exec_timer2_str = format_string(REP_EXEC_TIME_INFO_TEMPLATE, format_args_exec_timer2)
        
        if not return_best_time:
            print_format_string(REP_EXEC_TIME_INFO_TEMPLATE, format_args_exec_timer2)
        else:
            format_args_exec_timer3 = (exec_timer2_str, best_time)
            print_format_string(REP_EXEC_TIME_INFO_BEST_TEMPLATE, format_args_exec_timer3)
    
#%%

#--------------------------#
# Parameters and constants #
#--------------------------#

# List of libraries containing methods for code execution timing #
MODULE_LIST = ["os", "time", "timeit"]

# Time units #
SEC_TIME_UNIT_STR = 's'
DEFAULT_TIME_UNIT_STR = 'formatted'

# Template strings #
#------------------#

# Informative #
NOREP_EXEC_TIME_INFO_TEMPLATE = \
"""Snippet execution time ({}), for {} trials with no repeats: {}"""

REP_EXEC_TIME_INFO_TEMPLATE = \
"""Snippet execution time ({}), for {} trials with and {} repeats:\n{}"""

REP_EXEC_TIME_INFO_BEST_TEMPLATE = \
"""{}\nBest: {}"""

# Error messages #
TYPE_ERROR_TEMPLATE = """Argument '{}' must be of type 'int'."""
UNSUPPORTED_MODULE_CHOICE_TEMPLATE = """Unsupported module option, choose one from {}."""

# Switch case dictionaries #
#--------------------------#

# Methods for code execution timing #
MODULE_OPERATION_DICT = {
    MODULE_LIST[0]: lambda: os.times()[-1],
    MODULE_LIST[1]: lambda: time.time(),
    MODULE_LIST[2]: lambda: timeit.default_timer(),
}
