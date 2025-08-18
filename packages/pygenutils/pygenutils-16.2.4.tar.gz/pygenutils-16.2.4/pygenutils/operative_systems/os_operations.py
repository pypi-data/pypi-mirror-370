#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import os

#------------------------#
# Import project modules # 
#------------------------#

from paramlib.global_parameters import FILESYSTEM_CONTEXT_MODULES
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.strings.string_handler import get_type_str
from pygenutils.strings.text_formatters import format_string

# %%

#------------------#
# Define functions #
#------------------#

# Main method #
#-------------#

def run_system_command(command,
                       module="subprocess", 
                       _class="run",
                       capture_output=False,
                       return_output_name=False,
                       encoding="utf-8",
                       shell=True,
                       text=None):
   
    """
    Execute a system command using the specified module and class combination.

    This method runs a command using either the 'os' or 'subprocess' module,
    depending on the provided parameters. It returns relevant output attributes
    like stdout, stderr, stdin, and the return code, depending on the system 
    command execution method.

    Parameters
    ----------
    command : str | list[str]
        The command to execute, either as a string (for 'os' and 'subprocess')
        or a list of arguments (only for 'subprocess' module).
    module : str, optional, default: "subprocess"
        The module to use for executing the command.
        Valid options are 'os' or 'subprocess'.
    _class : str, optional, default "run"
        The class within the module to use.
        Valid options are:
        - 'os': {'system', 'popen'}.
        - 'subprocess': {'Popen', 'call', 'run'}.
    capture_output : bool, optional, default: False
        If True, captures the command's stdout and stderr.
    return_output_name : bool, optional, default: False
        If True, returns the file descriptors' names (if applicable) for stdin,
        stdout, and stderr.
        This parameter is only applicable when using
        (module, _class) = ("subprocess", "Popen").
        For all other combinations, this parameter is ignored.
    encoding : str, optional, default 'utf-8'
        The encoding to use when decoding stdout and stderr. 
        If None, no decoding is applied.
    shell : bool, optional
        Only applicable if (module, _class) == ("subprocess", "run").
        If True, the command will be executed through the shell. Default is True
    text : bool, optional, default: None
        Only applicable if (module, _class) in [("subprocess", "run"), ("subprocess", "Popen")].
        If True, stdout and stderr are returned as strings rather than bytes.
        If None, the value is determined by whether encoding is provided.
        
    Raises
    ------
    ValueError
        If the combo (module, _class) is neither of the allowed ones in 'command_helpers' 

    Returns
    -------
    result : dict
        A dictionary containing relevant output characteristics such as:
        - 'stdout': Captured standard output (if applicable)
        - 'stderr': Captured standard error (if applicable)
        - 'stdin': The name of the input stream (if applicable)
        - 'return_code': The exit code of the command
        - 'errors': Any errors encountered during command execution (if applicable)
    """

    
    # Handle nested lists by flattening them first for list commands
    if isinstance(command, list):
        if any(isinstance(item, list) for item in command):
            command = flatten_list(command)
    
    # Validate module and class
    if (module, _class) not in COMMAND_HELPERS:
        raise ValueError(f"Unsupported module-class combo '{module}'-'{_class}'.")
    
    # Get the appropriate helper function
    helper_func = COMMAND_HELPERS.get((module, _class))
    
    # Run the command via the helper
    if (module, _class) == ("subprocess", "Popen"):
        result = helper_func(command, capture_output=capture_output, encoding=encoding, 
                             return_output_name=return_output_name, text=text)
    elif (module, _class) == ("subprocess", "run"):
        result = helper_func(command, capture_output=capture_output, encoding=encoding, 
                             shell=shell, text=text)
    else:
        result = helper_func(command, capture_output=capture_output, encoding=encoding, shell=shell)
    
    return result


# Helpers #
#---------#

def os_system_helper(command, capture_output):
    """
    Helper function to execute a command using os.system.

    Parameters
    ----------
    command : str
        The system command to execute.
    capture_output : bool, optional
        Cannot capture output with os.system. This argument raises a ValueError 
        if set to True.

    Returns:
    --------
    dict
        A dictionary containing:
        - 'return_code': The exit code of the command.
    """
    
    # Validations #
    #-------------#
    
    # Command and class #
    if not isinstance(command, str):
        obj_type = get_type_str(command)
        raise TypeError(f"Expected str, not '{obj_type}'.")
     
    # Output capturing #
    if capture_output:
        raise ValueError("os.system cannot capture output.")
    
    # Operations #
    #------------#
    
    # Execute the command
    exit_code = os.system(command)
    
    # Return the exit status
    return dict(return_code=exit_code)


def os_popen_helper(command, capture_output):
    """
    Helper function to execute a command using os.popen.

    Parameters
    ----------
    command : str
        The system command to execute.
    capture_output : bool, optional
        Must be True for os.popen to capture output.

    Returns:
    --------
    dict
        A dictionary containing:
        - 'stdout': The captured standard output.
        - 'return_code': None, as os.popen does not provide a return code.
    """
    
    # Validations #
    #-------------#
    
    # Command and class #
    if not isinstance(command, str):
        obj_type = get_type_str(command)
        raise TypeError(f"Expected str, not '{obj_type}'.")
        
    # Output capturing #
    if not capture_output:
        raise ValueError("os.popen must capture output.")
    
    # Operations #
    #------------#
    
    # Capture the output
    output = os.popen(command).read()
    
    # No return code is available for os.popen, return the output
    return dict(stdout=output, return_code=None)


def subprocess_popen_helper(command, capture_output, encoding, return_output_name=False, text=None):
    """
    Helper function to execute a command using subprocess.Popen.

    Parameters
    ----------
    command : str | list[str]
        The system command to execute.
    capture_output : bool, optional
        If True, captures stdout, stderr, and stdin.
    encoding : str, optional
        The encoding to use when decoding stdout and stderr.
    return_output_name : bool, optional
        If True, returns the file descriptors' names for stdin, stdout, and stderr.
    text : bool, optional
        If True, stdout and stderr are returned as strings rather than bytes.
        If None, the value is determined by whether encoding is provided.

    Returns:
    --------
    dict
        A dictionary containing:
        - 'stdin': Captured standard input (if applicable and capture_output=True).
        - 'stdout': The captured standard output (if applicable and capture_output=True).
        - 'stderr': The captured standard error (if applicable and capture_output=True).
        - 'return_code': The exit code of the command.
        - 'errors': Any errors encountered during command execution.
    """
    from subprocess import Popen, PIPE
    
    # Set text parameter (if not provided, use encoding as a fallback)
    text_param = text if text is not None else bool(encoding)
    
    # Define the I/O streams
    pipe_kwargs = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE) if capture_output else {}
    
    # Execute the command
    process = Popen(command, **pipe_kwargs, text=text_param)
    
    # Wait for command to complete
    process.wait()
    
    # Initialise return dictionary with return code
    return_dict = {"return_code": process.returncode}
    
    # Add errors if available
    if hasattr(process, "errors"):
        return_dict["errors"] = process.errors
        
    # Only capture stdin, stdout, stderr if output capturing was requested
    if capture_output:
        if return_output_name:
            # Return file descriptor names
            if process.stdin:
                return_dict["stdin"] = process.stdin.name
            if process.stdout:
                return_dict["stdout"] = process.stdout.name
            if process.stderr:
                return_dict["stderr"] = process.stderr.name
        else:
            # Return actual captured output
            if process.stdin:
                # If text mode is enabled, we already get strings, otherwise decode with encoding
                if text_param:
                    return_dict["stdin"] = process.stdin.read()
                else:
                    return_dict["stdin"] = process.stdin.read().decode(encoding) if encoding else process.stdin.read()
                    
            if process.stdout:
                if text_param:
                    return_dict["stdout"] = process.stdout.read()
                else:
                    return_dict["stdout"] = process.stdout.read().decode(encoding) if encoding else process.stdout.read()
                    
            if process.stderr:
                if text_param:
                    return_dict["stderr"] = process.stderr.read()
                else:
                    return_dict["stderr"] = process.stderr.read().decode(encoding) if encoding else process.stderr.read()
    
    # Return the compiled result dictionary
    return return_dict


def subprocess_call_helper(command, capture_output):
    """
    Helper function to run a command using subprocess.call.
    
    Parameters
    ----------
    command : str | list[str]
        The command to run, either as a string or a list of strings.
    capture_output : bool
        If True, output capturing is requested (not supported by this method).

    Raises
    ------
    ValueError
        If capture_output is set to True, since subprocess.call does not support capturing output.

    Returns:
    --------
    dict
        A dictionary containing the return code of the command execution.
    """
    from subprocess import call
    
    # Validate capture_output (not applicable for subprocess.call)
    if capture_output:
        raise ValueError("subprocess.call does not support capturing output.")
    
    # Execute the command
    return_code = call(command)
    
    # Return the return code
    return dict(return_code=return_code)


def subprocess_run_helper(command, capture_output, encoding, shell, text):
    """
    Helper function to execute a command using subprocess.run.

    Parameters
    ----------
    command : str | list[str]
        The system command to execute.
    capture_output : bool, optional
        If True, captures stdout and stderr.
    encoding : str, optional, default: None
        The encoding to use when decoding stdout and stderr.
    shell : bool, optional
        If True, the command will be executed through the shell.
    text : bool, optional
        If True, stdout and stderr are returned as strings rather than bytes.
        If None, the value is determined by whether encoding is provided.

    Returns
    -------
    dict
        A dictionary containing:
        - 'stdout': The captured standard output (if capture_output=True).
        - 'stderr': The captured standard error (if capture_output=True).
        - 'return_code': The exit code of the command.
        
        Note: This function always returns the result dictionary regardless of the
        return code. The caller should check the 'return_code' field and decide
        how to handle non-zero exit codes.
    """
    from subprocess import run
    
    # Set text parameter (if not provided, use encoding as a fallback)
    text_param = text if text is not None else bool(encoding)
    
    # Execute the command and capture output if requested
    result = run(command, capture_output=capture_output, text=text_param, shell=shell)
    
    # Initialise return dictionary with return code
    return_dict = {"return_code": result.returncode}
    
    # Only process stdout/stderr if they were captured
    if capture_output:
        # Add stdout and stderr to the return dictionary if available
        if hasattr(result, "stdout"):
            return_dict["stdout"] = result.stdout.strip() if result.stdout else ""
        
        if hasattr(result, "stderr"):
            return_dict["stderr"] = result.stderr.strip() if result.stderr else ""
    
    # Always return the result dictionary, regardless of return code
    # Let the caller decide how to handle non-zero return codes
    return return_dict

# %%

# Auxiliary methods #
#-------------------#

def exit_info(process_exit_info_obj, check_stdout=True, check_stderr=True, check_return_code=True):
    """
    Print the exit information of a process along with stdout and stderr based on selected parameters.

    This function checks the exit status of a process represented by the 
    provided `process_exit_info_obj`. If the command string fails to execute,
    it raises a RuntimeError indicating that the command was interpreted 
    as a path. It also outputs stdout and stderr if available and requested.

    Parameters
    ----------
    process_exit_info_obj : dict or subprocess.CompletedProcess
        Either a dictionary containing exit information of the process or
        a CompletedProcess object, typically returned by run_system_command.
    check_stdout : bool, optional
        Whether to check and print stdout if available. Default is True.
        Note: stdout will only be available if capture_output=True was set
        in the original run_system_command call.
    check_stderr : bool, optional
        Whether to check and print stderr if available. Default is True.
        Note: stderr will only be available if capture_output=True was set
        in the original run_system_command call.
    check_return_code : bool, optional
        Whether to check the return code and raise an error if non-zero. Default is True.

    Raises
    ------
    RuntimeError
    - If the command string is interpreted as a path and fails to execute,
      in which case Python would originally rise a FileNotFoundError.
    - If check_return_code is True and the exit status is non-zero.

    Returns
    -------
    bool
        True if the process completed successfully (or if return code checking is disabled).

    Prints
    ------
    A message indicating whether the process completed successfully or 
    details about the non-zero exit status, including the return code 
    and any error message from stderr. Also prints stdout and stderr if available and requested.
    """
    try:
        process_exit_info_obj
    except FileNotFoundError:
        # If a str command fails, bash will usually interpret 
        # that a path is trying to be searched,
        # and if it fails to find, it will raise a Python-equivalent FileNotFoundError.
        raise RuntimeError("Command string interpreted as a path. "
                           "Please check the command.")
    else:
        # Check if we're dealing with a dictionary or a CompletedProcess object
        is_dict = isinstance(process_exit_info_obj, dict)
        
        # Get return code - handle both dict and CompletedProcess objects
        if is_dict:
            return_code = process_exit_info_obj.get("return_code")
            # Check if we have any output information
            has_stdout = "stdout" in process_exit_info_obj
            has_stderr = "stderr" in process_exit_info_obj
        else:
            # Assume it's a CompletedProcess-like object with returncode attribute
            return_code = getattr(process_exit_info_obj, "returncode", None)
            # Check if the object has stdout/stderr attributes
            has_stdout = hasattr(process_exit_info_obj, "stdout")
            has_stderr = hasattr(process_exit_info_obj, "stderr")
        
        # Print stdout if available and requested
        if check_stdout:
            if is_dict and has_stdout and process_exit_info_obj.get("stdout"):
                print(f"STDOUT\n{'='*6}")
                print(process_exit_info_obj["stdout"])
            elif not is_dict and has_stdout and getattr(process_exit_info_obj, "stdout", None):
                print(f"STDOUT\n{'='*6}")
                print(process_exit_info_obj.stdout)
        
        # Print stderr if available and requested
        if check_stderr:
            if is_dict and has_stderr and process_exit_info_obj.get("stderr"):
                print(f"STDERR\n{'='*6}")
                print(process_exit_info_obj["stderr"])
            elif not is_dict and has_stderr and getattr(process_exit_info_obj, "stderr", None):
                print(f"STDERR\n{'='*6}")
                print(process_exit_info_obj.stderr)
        
        # Check return code if requested
        if check_return_code:
            if return_code == 0:
                print("Process completed successfully with return code 0")
                return True
            else:
                # Get error message - handle both dict and CompletedProcess objects
                error_message = "No error output available (capture_output may have been False)"
                
                if is_dict and has_stderr:
                    error_message = process_exit_info_obj.get("stderr") or error_message
                elif not is_dict and has_stderr:
                    error_message = getattr(process_exit_info_obj, "stderr", error_message) or error_message
                
                format_args_error = (return_code, error_message)
                raise RuntimeError("An error occurred during command execution: "
                                   f"{format_string(NONZERO_EXIT_STATUS_TEMPLATE, format_args_error)}")
        
        # If return code checking is disabled, just return True
        return True

# %%

#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported options #
#-------------------#

# Modules #
SYSTEM_COMMAND_MODULES = FILESYSTEM_CONTEXT_MODULES[0::3]

# Command run classes #
CLASS_LIST = ["system", "popen", "Popen", "call", "run"]

# Template strings #
#------------------#

# Errors #
NONZERO_EXIT_STATUS_TEMPLATE = """Process exited with status {} with the following error:\n{}"""

# Switch case dictionaries #
#--------------------------#

# System command run helpers #
COMMAND_HELPERS = {
    ("os", "system"): os_system_helper,
    ("os", "popen"): os_popen_helper,
    ("subprocess", "Popen"): subprocess_popen_helper,
    ("subprocess", "run"): subprocess_run_helper,
    ("subprocess", "call"): subprocess_call_helper
}
