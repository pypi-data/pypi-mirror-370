#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import os

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.operative_systems.os_operations import run_system_command, exit_info
from pygenutils.time_handling.time_formatters import parse_dt_string

#------------------#
# Define functions #
#------------------#

# Internal helpers #
#------------------#



def _load_file_list(files):
    """
    Internal helper to load files from various input formats.
    
    Processes inputs that can be:
    - A direct file path (string)
    - A path to a text file containing a list of files (string)
    - A list of file paths (list)
    - A nested list of file paths for recursive processing (list of lists)
    
    Parameters
    ----------
    files : str | list[str]
        The input to process
        
    Returns
    -------
    list[str]
        A flattened list of file paths
        
    Raises
    ------
    ValueError or RuntimeError
        If the file(s) cannot be read
    TypeError
        If the input is neither a string nor a list
    """
    # Handle nested lists using the robust flatten_list function
    if isinstance(files, list):
        # Check if there are nested lists and flatten if needed
        if any(isinstance(item, list) for item in files):
            files = flatten_list(files)
        return files
        
    # If it's a string, check if it's a direct media file
    if isinstance(files, str):
        # If the file exists and has a recognized media extension, treat as direct file path
        if os.path.exists(files) and (files.endswith(tuple(COMMON_AUDIO_FORMATS)) or 
                                      files.endswith(tuple(COMMON_VIDEO_FORMATS))):
            return [files]  # Return as single-item list
        
        # Otherwise try to read it as a file containing a list
        try:
            with open(files) as f:
                return f.read().splitlines()
        except Exception as e:
            # The original functions use different exception types, so we'll default to ValueError
            # and let the calling function raise its own exception type if needed
            raise ValueError(f"Error reading file '{files}': {e}")
    
    raise TypeError(f"Expected list or string, got {type(files)}")

def _validate_files(file_list: list[str], list_name: str):
    """
    Validates that all files in a list exist.
    
    Parameters
    ----------
    file_list : list[str]
        List of file paths to validate
    list_name : str
        Name of the list for error reporting
        
    Raises
    ------
    FileNotFoundError
        If any file in the list doesn't exist
    """
    for file in file_list:
        if not os.path.exists(file):
            raise FileNotFoundError(f"{list_name}: '{file}' not found.")

def _is_audio_file(file):
    """
    Checks if a file has an audio extension.
    
    Parameters
    ----------
    file : str
        File path to check
        
    Returns
    -------
    bool
        True if the file has an audio extension, False otherwise
    """
    return file.endswith(tuple(COMMON_AUDIO_FORMATS))

def _is_video_file(file):
    """
    Checks if a file has a video extension.
    
    Parameters
    ----------
    file : str
        File path to check
        
    Returns
    -------
    bool
        True if the file has a video extension, False otherwise
    """
    return file.endswith(tuple(COMMON_VIDEO_FORMATS))

# Add a new helper function to handle file path escaping

def _escape_path(file_path):
    """
    Escapes file paths for use in shell commands.
    
    Handles paths containing spaces, parentheses, and other special characters.
    
    Parameters
    ----------
    file_path : str
        The file path to escape
        
    Returns
    -------
    str
        The escaped file path, safe for use in shell commands
    """
    import re
    import shlex
    
    # Use shlex.quote for proper shell escaping
    return shlex.quote(file_path)

# Main functions #
#----------------#

# Merge files #
#~~~~~~~~~~~~~#

# %% 

def merge_media_files(audio_files, 
                      video_files, 
                      output_file_list=None, 
                      zero_padding=1, 
                      audio_bitrate_fraction=5,
                      video_bitrate_fraction=5,
                      video_codec=None,
                      audio_codec=None, 
                      preset="medium",
                      overwrite=True,
                      capture_output=False,
                      return_output_name=False,
                      encoding="utf-8",
                      shell=True):
    """
    Merges audio and video files into a single output file for each pair.

    Parameters
    ----------
    audio_files : str | list[str]
        A list of audio file paths or a path to a text file containing audio file names.
        Can also be a nested list for recursive processing.
    video_files : str | list[str]
        A list of video file paths or a path to a text file containing video file names.
        Can also be a nested list for recursive processing.
    output_file_list : list[str] | None, optional
        A list of output file names. If not provided, default names will be generated.
    zero_padding : int | None, optional
        Zero-padding to apply to the output file numbers. 
        Must be greater than or equal to 1, or None to disable padding.
        Only used when output_file_list is None.
    audio_bitrate_fraction : int | None, optional
        Audio bitrate fraction (multiplied by 32 to get kbps). Default is 5.
        Common ranges: 2-16 for 64-512kbps (speech to high-quality music).
        Set to None to skip audio bitrate specification.
    video_bitrate_fraction : int | None, optional
        Video bitrate fraction (multiplied by 32 to get kbps). Default is 5.
        Common ranges: 31-3125+ for 1-100+Mbps (360p to 4K+).
        Set to None to skip video bitrate specification.
    video_codec : str | None, optional
        Video codec to use. Options: "copy", "libx264", "libx265", etc. Default is None (no re-encoding).
    audio_codec : str | None, optional
        Audio codec to use. Options: "copy", "aac", "mp3", "ac3", etc. Default is None (no re-encoding).
    preset : str, optional
        Encoding preset for video codec. Options: "ultrafast", "superfast", "veryfast", 
        "faster", "fast", "medium", "slow", "slower", "veryslow". Default is "medium".
    video_bitrate : int | None, optional
        Video bitrate in kbps. If None, ffmpeg will choose based on codec defaults.
    overwrite : bool, optional
        Whether to overwrite existing output files. Default is True.
        If True, uses '-y' flag; if False, uses '-n' flag.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Raises
    ------
    ValueError
        If the lengths of the audio and video file lists do not match,
        or if any parameter is invalid.

    Returns
    -------
    None
    """
    
    # Validations #
    #-#-#-#-#-#-#-#
    
    # Load the file lists, automatically detecting whether input is file or list
    try:
        audio_file_list = _load_file_list(audio_files)
        video_file_list = _load_file_list(video_files)
    except ValueError as e:
        raise ValueError(f"Error loading files: {e}")
    
    # Validate lists are of the same length
    if len(video_file_list) != len(audio_file_list):
        raise ValueError("Input audio and video file lists must have the same length.")
        
    # Output file list length
    if output_file_list is not None:
        if len(output_file_list) != len(video_file_list):
            raise ValueError("Output file name list must match the length of input lists.")
        
    # Get all arguments #
    param_keys = get_caller_args()
    zero_pad_pos = param_keys.index("zero_padding")
        
    # Zero-padding
    if zero_padding is not None and (not isinstance(zero_padding, int) or zero_padding < 1):
        raise ValueError(f"'zero_padding' (number {zero_pad_pos}) "
                         f"must be an integer >= 1 or None, got {zero_padding}.")
        
    # Audio bitrate fraction validation
    if audio_bitrate_fraction is not None and (not isinstance(audio_bitrate_fraction, int) or audio_bitrate_fraction < 1):
        raise ValueError("'audio_bitrate_fraction' must be a positive integer or None.")
        
    # Video bitrate fraction validation
    if video_bitrate_fraction is not None and (not isinstance(video_bitrate_fraction, int) or video_bitrate_fraction < 1):
        raise ValueError("'video_bitrate_fraction' must be a positive integer or None.")
    
    # Video codec validation
    if video_codec is not None and not isinstance(video_codec, str):
        raise ValueError("'video_codec' must be a string or None.")
        
    # Audio codec validation
    if audio_codec is not None and not isinstance(audio_codec, str):
        raise ValueError("'audio_codec' must be a string or None.")
        
    # Preset validation
    valid_presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", 
                     "medium", "slow", "slower", "veryslow"]
    if preset not in valid_presets:
        raise ValueError(f"'preset' must be one of {valid_presets}, got '{preset}'.")
        
    # Overwrite validation
    if not isinstance(overwrite, bool):
        raise ValueError("'overwrite' must be a boolean value.")
    
    # File existence validation
    _validate_files(video_file_list, "Video file list (arg number 0)")
    _validate_files(audio_file_list, "Audio file list (arg number 1)")
    
    # Program progression #
    #-#-#-#-#-#-#-#-#-#-#-#
    
    # Generate default output file names if not provided
    if output_file_list is None:
        if zero_padding is None:
            # No padding when zero_padding is None
            output_file_list = [
                f"merged_video_{i + 1}"
                for i in range(len(video_file_list))
            ]
        else:
            output_file_list = [
                f"merged_video_{str(i + 1).zfill(zero_padding)}"
                for i in range(len(video_file_list))
            ]
    
    # Set overwrite flag
    overwrite_flag = "-y" if overwrite else "-n"
    
    # Try multiple ffmpeg merge template strings with different variations to handle errors
    for i, (audio_file, video_file, output_file) in enumerate(zip(audio_file_list,
                                                   video_file_list,
                                                   output_file_list)):
        # Create a list of ffmpeg commands to try using the templates
        audio_bitrate = audio_bitrate_fraction * 32 if audio_bitrate_fraction is not None else None
        video_bitrate = video_bitrate_fraction * 32 if video_bitrate_fraction is not None else None
        
        # Print status message
        print(f"Creating merged file {i+1}/{len(audio_file_list)}: {output_file} from audio '{audio_file}' and video '{video_file}'")
        
        # Build a single ffmpeg command with user-specified parameters
        ffmpeg_command = f"ffmpeg {overwrite_flag} -i {_escape_path(audio_file)} -i {_escape_path(video_file)}"
        
        # Add video codec
        if video_codec is not None:
            if video_codec != "copy":
                ffmpeg_command += f" -c:v {video_codec}"
                # Add preset only if not using copy codec
                ffmpeg_command += f" -preset {preset}"
                # Add video bitrate if specified
                if video_bitrate is not None:
                    ffmpeg_command += f" -b:v {video_bitrate}k"
            else:
                ffmpeg_command += f" -c:v copy"
        
        # Add audio codec and bitrate
        if audio_codec is not None:
            if audio_codec != "copy":
                ffmpeg_command += f" -c:a {audio_codec}"
                # Add audio bitrate if specified
                if audio_bitrate is not None:
                    ffmpeg_command += f" -b:a {audio_bitrate}k"
            else:
                ffmpeg_command += f" -c:a copy"
        
        # Add output file
        ffmpeg_command += f" {_escape_path(output_file)}"
        
        ffmpeg_commands_to_try = [ffmpeg_command]
        
        # Add fallback commands using templates with user parameters
        # Prepare conditional arguments
        video_bitrate_arg = f" -b:v {video_bitrate}k" if video_bitrate is not None and video_codec is not None and video_codec != "copy" else ""
        preset_arg = f" -preset {preset}" if video_codec is not None and video_codec != "copy" else ""
        
        for template in FFMPEG_MERGE_CMD_TEMPLATES:
            fallback_command = template.format(
                overwrite_flag=overwrite_flag,
                audio_file=_escape_path(audio_file),
                video_file=_escape_path(video_file),
                video_codec=video_codec,
                audio_codec=audio_codec,
                audio_bitrate=audio_bitrate or "",
                video_bitrate_arg=video_bitrate_arg,
                preset_arg=preset_arg,
                output_file=_escape_path(output_file)
            )
            ffmpeg_commands_to_try.append(fallback_command)

        # Try each command until one succeeds for this file pair
        success = False
        for ffmpeg_command in ffmpeg_commands_to_try:
            try:
                process_exit_info = run_system_command(
                    ffmpeg_command,
                    capture_output=capture_output,
                    return_output_name=return_output_name,
                    encoding=encoding,
                    shell=shell
                )
                # Call exit_info with parameters based on capture_output
                exit_info(
                    process_exit_info,
                    check_stdout=capture_output,
                    check_stderr=capture_output,
                    check_return_code=True
                )
                success = True
                break  # Exit the inner loop if successful
            except RuntimeError:
                continue  # Try the next command variation
        
        if not success:
            print(f"Warning: Failed to process {audio_file} + {video_file}")

# %%
def merge_individual_media_files(media_inputs,
                                 safe=True, 
                                 output_file_name=None,
                                 audio_bitrate_fraction=5,
                                 video_bitrate_fraction=5,
                                 video_codec=None,
                                 audio_codec=None,
                                 preset="medium",
                                 overwrite=True,
                                 capture_output=False,
                                 return_output_name=False,
                                 encoding="utf-8",
                                 shell=True):
    """
    Merges either audio or video files into a single output file.

    Parameters
    ----------
    media_inputs : str | list[str]
        A list of file paths (either audio or video) or a path to a text file 
        containing file names. Can also be a nested list for recursive processing.
    safe : bool, optional
        If True, ffmpeg runs in safe mode to prevent unsafe file operations.
        Default is True.
    output_file_name : str | None, optional
        The name of the output file. If not provided, a default name will be used.
    audio_bitrate_fraction : int | None, optional
        Audio bitrate fraction (multiplied by 32 to get kbps). Default is 5.
        Common ranges: 2-16 for 64-512kbps (speech to high-quality music).
        Set to None to skip audio bitrate specification.
    video_bitrate_fraction : int | None, optional
        Video bitrate fraction (multiplied by 32 to get kbps). Default is 5.
        Common ranges: 31-3125+ for 1-100+Mbps (360p to 4K+).
        Set to None to skip video bitrate specification.
    video_codec : str | None, optional
        Video codec to use. Options: "copy", "libx264", "libx265", etc. Default is None (no re-encoding).
    audio_codec : str | None, optional
        Audio codec to use. Options: "copy", "aac", "mp3", "ac3", etc. Default is None (no re-encoding).
    preset : str, optional
        Encoding preset for video codec. Options: "ultrafast", "superfast", "veryfast", 
        "faster", "fast", "medium", "slow", "slower", "veryslow". Default is "medium".
    video_bitrate : int | None, optional
        Video bitrate in kbps. If None, ffmpeg will choose based on codec defaults.
    overwrite : bool, optional
        Whether to overwrite existing output files. Default is True.
        If True, uses '-y' flag; if False, uses '-n' flag.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Raises
    ------
    ValueError
        If both audio and video files are provided in the input,
        or if any parameter is invalid.

    Returns
    -------
    None
    """
    
    # Validations #
    #-#-#-#-#-#-#-#
    
    # Audio bitrate fraction validation
    if audio_bitrate_fraction is not None and (not isinstance(audio_bitrate_fraction, int) or audio_bitrate_fraction < 1):
        raise ValueError("'audio_bitrate_fraction' must be a positive integer or None.")
        
    # Video bitrate fraction validation
    if video_bitrate_fraction is not None and (not isinstance(video_bitrate_fraction, int) or video_bitrate_fraction < 1):
        raise ValueError("'video_bitrate_fraction' must be a positive integer or None.")
        
    # Video codec validation
    if video_codec is not None and not isinstance(video_codec, str):
        raise ValueError("'video_codec' must be a string or None.")
        
    # Audio codec validation
    if audio_codec is not None and not isinstance(audio_codec, str):
        raise ValueError("'audio_codec' must be a string or None.")
        
    # Preset validation
    valid_presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", 
                     "medium", "slow", "slower", "veryslow"]
    if preset not in valid_presets:
        raise ValueError(f"'preset' must be one of {valid_presets}, got '{preset}'.")
        
    # Overwrite validation
    if not isinstance(overwrite, bool):
        raise ValueError("'overwrite' must be a boolean value.")

    # Load the file list, automatically detecting whether input is file or list
    try:
        file_list = _load_file_list(media_inputs)
    except ValueError as e:
        raise ValueError(f"Error loading files: {e}")

    # Check if all files are either audio or video, not both #
    audio_files = [file for file in file_list if _is_audio_file(file)]
    video_files = [file for file in file_list if _is_video_file(file)]
    
    if audio_files and video_files:
        raise ValueError("Input list contains both audio and video files. "
                         "Only one type is allowed.")
    
    # Program progression #
    #-#-#-#-#-#-#-#-#-#-#-#
    
    # Generate default output file names if not provided #
    if not output_file_name:
        output_file_name = "out_file"
    
    # Set overwrite flag
    overwrite_flag = "-y" if overwrite else "-n"
    
    # Print status message
    if isinstance(media_inputs, list):
        # Show total file count instead of truncating after 3 files
        file_type = "audio" if audio_files else "video"
        print(f"Creating merged file {output_file_name}.mp4 from {len(file_list)} {file_type} files")
    else:
        print(f"Creating merged file {output_file_name}.mp4 from files listed in '{media_inputs}'")
    
    # Attempt multiple ffmpeg commands to handle potential errors
    # For input_str, we need to escape each path before joining
    escaped_file_list = [_escape_path(file) for file in file_list]
    input_str = '|'.join(escaped_file_list)
    audio_bitrate = audio_bitrate_fraction * 32 if audio_bitrate_fraction is not None else None
    video_bitrate = video_bitrate_fraction * 32 if video_bitrate_fraction is not None else None
    
    # Build primary ffmpeg command with user-specified parameters
    ffmpeg_command = f"ffmpeg {overwrite_flag} -i 'concat:{input_str}'"
    
    # Add video codec
    if video_files and video_codec is not None:  # Only add video options if we have video files and codec is specified
        if video_codec != "copy":
            ffmpeg_command += f" -c:v {video_codec}"
            # Add preset only if not using copy codec
            ffmpeg_command += f" -preset {preset}"
            # Add video bitrate if specified
            if video_bitrate is not None:
                ffmpeg_command += f" -b:v {video_bitrate}k"
        else:
            ffmpeg_command += f" -c:v copy"
    
    # Add audio codec and bitrate
    if audio_codec is not None:
        if audio_codec != "copy":
            ffmpeg_command += f" -c:a {audio_codec}"
            # Add audio bitrate if specified
            if audio_bitrate is not None:
                ffmpeg_command += f" -b:a {audio_bitrate}k"
        else:
            ffmpeg_command += f" -c:a copy"
    
    # Add output file
    ffmpeg_command += f" {_escape_path(output_file_name)}.mp4"
    
    ffmpeg_commands_to_try = [ffmpeg_command]
    
    # Add fallback commands using templates with user parameters
    # Prepare conditional arguments
    video_bitrate_arg = f" -b:v {video_bitrate}k" if video_bitrate is not None and video_codec is not None and video_codec != "copy" else ""
    preset_arg = f" -preset {preset}" if video_codec is not None and video_codec != "copy" else ""
    
    for template in FFMPEG_INDIVIDUAL_MERGE_CMD_TEMPLATES:
        fallback_command = template.format(
            overwrite_flag=overwrite_flag,
            input_str=input_str,
            input_file=_escape_path(media_inputs) if isinstance(media_inputs, str) else media_inputs,
            safe=int(safe),
            video_codec=video_codec,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate or "",
            video_bitrate_arg=video_bitrate_arg,
            preset_arg=preset_arg,
            output_file=_escape_path(output_file_name)
        )
        ffmpeg_commands_to_try.append(fallback_command)

    # Try each command until one succeeds or all fail
    for ffmpeg_command in ffmpeg_commands_to_try:
        try:
            process_exit_info = run_system_command(
                ffmpeg_command,
                capture_output=capture_output,
                return_output_name=return_output_name,
                encoding=encoding,
                shell=shell
            )
            # Call exit_info with parameters based on capture_output
            exit_info(
                process_exit_info,
                check_stdout=capture_output,
                check_stderr=capture_output,
                check_return_code=True
            )
            break  # Exit loop if successful
        except RuntimeError:
            pass  # Continue with the next ffmpeg command if there's an error

# %%

# Cut files #
#-----------#

def cut_media_files(media_inputs, 
                    start_time_list,
                    end_time_list, 
                    output_file_list=None,
                    zero_padding=1,
                    audio_bitrate_fraction=5,
                    video_bitrate_fraction=5,
                    video_codec=None,
                    audio_codec=None,
                    preset="medium",
                    overwrite=True,
                    capture_output=False,
                    return_output_name=False,
                    encoding="utf-8",
                    shell=True):
    """
    Cuts media files (audio or video) based on specified start and end times.

    Parameters
    ----------
    media_inputs : str | list[str]
        A list of media file paths or a path to a text file containing file names.
        Can also be a nested list for recursive processing.
    start_time_list : str | list[str]
        The start time in the format '%T' or '%T.%f'. 
        If any set to 'start', cutting starts from the beginning.
    end_time_list : str | list[str]
        The end time in the format '%T' or '%T.%f'.
        If any set to 'end', cutting proceeds until the end of the file.
    output_file_list : list[str] | None, optional
        A list of output file names. If not provided, default names will be generated.
    zero_padding : int | None, optional
        Zero-padding to apply to the output file numbers. 
        Must be greater than or equal to 1, or None to disable padding.
        Only used when output_file_list is None.
    audio_bitrate_fraction : int | None, optional
        Audio bitrate fraction (multiplied by 32 to get kbps). Default is 5.
        Common ranges: 2-16 for 64-512kbps (speech to high-quality music).
        Set to None to skip audio bitrate specification.
    video_bitrate_fraction : int | None, optional
        Video bitrate fraction (multiplied by 32 to get kbps). Default is 5.
        Common ranges: 31-3125+ for 1-100+Mbps (360p to 4K+).
        Set to None to skip video bitrate specification.
    video_codec : str | None, optional
        Video codec to use. Options: "copy", "libx264", "libx265", etc. Default is None (no re-encoding).
    audio_codec : str | None, optional
        Audio codec to use. Options: "copy", "aac", "mp3", "ac3", etc. Default is None (no re-encoding).
    preset : str, optional
        Encoding preset for video codec. Options: "ultrafast", "superfast", "veryfast", 
        "faster", "fast", "medium", "slow", "slower", "veryslow". Default is "medium".
    overwrite : bool, optional
        Whether to overwrite existing output files. Default is True.
        If True, uses '-y' flag; if False, uses '-n' flag.
    capture_output : bool, optional
        Whether to capture the command output. Default is False.
    return_output_name : bool, optional
        Whether to return file descriptor names. Default is False.
    encoding : str, optional
        Encoding to use when decoding command output. Default is "utf-8".
    shell : bool, optional
        Whether to execute the command through the shell. Default is True.

    Raises
    ------
    RuntimeError
        If a file is passed as an input argument, when for some reason 
        Python is unable to read it.
    ValueError
        - If any start and end is set to default values
        - If any parameter is invalid.
        - If the lengths of the start and end time lists do not match,

    Returns
    -------
    None
    
    Notes
    -----
    For arg 'media_inputs', note that if a single file is passed, 
    it must be enclosed in a list, otherwise the function will interpret it
    as being a file, which Python will almost surely unable to read it.
    """
    
    def validate_time_format(time_str):
        try:
            for time_fmt in TIME_FMT_STR_LIST:
                parse_dt_string(time_str, time_fmt)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. "
                             f"Expected one from {TIME_FMT_STR_LIST}")
            
    # Load the file list, automatically detecting whether input is file or list
    try:
        file_list = _load_file_list(media_inputs)
    except ValueError as e:
        raise RuntimeError(f"Error loading files: {e}")

    # Validate lists of start and end times are of the same length
    if len(start_time_list) != len(end_time_list):
        raise ValueError("Start and end time lists must have the same length.")

    # Validate start and end times
    for start_time, end_time in zip(start_time_list, end_time_list):
        if (start_time, end_time) == ('start', 'end'):
            raise ValueError("Both start and end cannot be default values.")
        else:
            if start_time != 'start':
                validate_time_format(start_time)
            if end_time != 'end':
                validate_time_format(end_time)

    # Zero-padding
    if zero_padding is not None and (not isinstance(zero_padding, int) or zero_padding < 1):
        raise ValueError(f"zero_padding must be an integer >= 1 or None, got {zero_padding}.")
        
    # Audio bitrate fraction validation
    if audio_bitrate_fraction is not None and (not isinstance(audio_bitrate_fraction, int) or audio_bitrate_fraction < 1):
        raise ValueError("'audio_bitrate_fraction' must be a positive integer or None.")
        
    # Video bitrate fraction validation
    if video_bitrate_fraction is not None and (not isinstance(video_bitrate_fraction, int) or video_bitrate_fraction < 1):
        raise ValueError("'video_bitrate_fraction' must be a positive integer or None.")
    
    # Video codec validation
    if video_codec is not None and not isinstance(video_codec, str):
        raise ValueError("'video_codec' must be a string or None.")
        
    # Audio codec validation
    if audio_codec is not None and not isinstance(audio_codec, str):
        raise ValueError("'audio_codec' must be a string or None.")
        
    # Preset validation
    valid_presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", 
                     "medium", "slow", "slower", "veryslow"]
    if preset not in valid_presets:
        raise ValueError(f"'preset' must be one of {valid_presets}, got '{preset}'.")
        
    # Overwrite validation
    if not isinstance(overwrite, bool):
        raise ValueError("'overwrite' must be a boolean value.")
        
    # Program progression #
    #---------------------#
    
    # If output file list is not provided, create default names
    if output_file_list is None:
        if zero_padding is None:
            # No padding when zero_padding is None
            output_file_list = [f"cut_file_{i + 1}.mp4" 
                               for i in range(len(file_list))]
        else:
            output_file_list = [f"cut_file_{str(i + 1).zfill(zero_padding)}.mp4" 
                               for i in range(len(file_list))]
    
    # Set overwrite flag
    overwrite_flag = "-y" if overwrite else "-n"
    
    # Try multiple ffmpeg cut commands with different variations to handle errors
    for i, (input_file, output_file, start_time, end_time) in enumerate(zip(file_list, 
                                                             output_file_list,
                                                             start_time_list,
                                                             end_time_list)):
        audio_bitrate = audio_bitrate_fraction * 32 if audio_bitrate_fraction is not None else None
        video_bitrate = video_bitrate_fraction * 32 if video_bitrate_fraction is not None else None
        
        # Print status message
        start_desc = start_time if start_time != 'start' else 'the beginning'
        end_desc = end_time if end_time != 'end' else 'the end'
        print(f"Creating cut file {i+1}/{len(file_list)}: {output_file} from '{input_file}' (from {start_desc} to {end_desc})")
        
        # Prepare time arguments
        start_time_arg = f" -ss {start_time}" if start_time != 'start' else ""
        end_time_arg = f" -to {end_time}" if end_time != 'end' else ""
        
        # Build primary ffmpeg command with user-specified parameters
        ffmpeg_command = f"ffmpeg {overwrite_flag} -i {_escape_path(input_file)}{start_time_arg}{end_time_arg}"
        
        # Determine if input is video file
        is_video = _is_video_file(input_file)
        
        # Add video codec (only for video files)
        if is_video and video_codec is not None:
            if video_codec != "copy":
                ffmpeg_command += f" -c:v {video_codec}"
                # Add preset only if not using copy codec
                ffmpeg_command += f" -preset {preset}"
                # Add video bitrate if specified
                if video_bitrate is not None:
                    ffmpeg_command += f" -b:v {video_bitrate}k"
            else:
                ffmpeg_command += f" -c:v copy"
        
        # Add audio codec and bitrate
        if audio_codec is not None:
            if audio_codec != "copy":
                ffmpeg_command += f" -c:a {audio_codec}"
                # Add audio bitrate if specified
                if audio_bitrate is not None:
                    ffmpeg_command += f" -b:a {audio_bitrate}k"
            else:
                ffmpeg_command += f" -c:a copy"
        
        # Add output file
        ffmpeg_command += f" {_escape_path(output_file)}"
        
        ffmpeg_commands_to_try = [ffmpeg_command]
        
        # Add fallback commands using templates with user parameters
        # Prepare conditional arguments
        video_bitrate_arg = f" -b:v {video_bitrate}k" if video_bitrate is not None and video_codec is not None and video_codec != "copy" and is_video else ""
        preset_arg = f" -preset {preset}" if video_codec is not None and video_codec != "copy" and is_video else ""
        
        for template in FFMPEG_CUT_CMD_TEMPLATES:
            fallback_command = template.format(
                overwrite_flag=overwrite_flag,
                input_file=_escape_path(input_file),
                start_time_arg=start_time_arg,
                end_time_arg=end_time_arg,
                video_codec=video_codec,
                audio_codec=audio_codec,
                audio_bitrate=audio_bitrate or "",
                video_bitrate_arg=video_bitrate_arg,
                preset_arg=preset_arg,
                output_file=_escape_path(output_file)
            )
            ffmpeg_commands_to_try.append(fallback_command)

        # Try each command until one succeeds for this file
        success = False
        for ffmpeg_command in ffmpeg_commands_to_try:
            try:
                process_exit_info = run_system_command(
                    ffmpeg_command,
                    capture_output=capture_output,
                    return_output_name=return_output_name,
                    encoding=encoding,
                    shell=shell
                )
                # Call exit_info with parameters based on capture_output
                exit_info(
                    process_exit_info,
                    check_stdout=capture_output,
                    check_stderr=capture_output,
                    check_return_code=True
                )
                success = True
                break  # Exit the inner loop if successful
            except RuntimeError:
                continue  # Try the next command variation
        
        if not success:
            print(f"Warning: Failed to process {input_file}")


# %%

#--------------------------#
# Parameters and constants #
#--------------------------#

# Supported options #
#-------------------#

# Time format strings #
TIME_FMT_STR_LIST = ['%T', '%T.%f']

# Common audio and video formats #
COMMON_AUDIO_FORMATS = ('.mp3', '.aac', '.wav')
COMMON_VIDEO_FORMATS = ('.mp4', '.avi', '.mkv')

# FFMPEG command templates with user-configurable parameters #
FFMPEG_MERGE_CMD_TEMPLATES = [
    "ffmpeg {overwrite_flag} -i {audio_file} -i {video_file} -c:v {video_codec} -c:a {audio_codec} -b:a {audio_bitrate}k{video_bitrate_arg}{preset_arg} {output_file}",
    "ffmpeg {overwrite_flag} -i {audio_file} -i {video_file} -c:v copy -c:a {audio_codec} -b:a {audio_bitrate}k {output_file}",
    "ffmpeg {overwrite_flag} -i {audio_file} -i {video_file} -c:v {video_codec} -c:a copy{video_bitrate_arg}{preset_arg} {output_file}"
]

FFMPEG_INDIVIDUAL_MERGE_CMD_TEMPLATES = [
    "ffmpeg {overwrite_flag} -i 'concat:{input_str}' -c:v {video_codec} -c:a {audio_codec} -b:a {audio_bitrate}k{video_bitrate_arg}{preset_arg} {output_file}.mp4",
    "ffmpeg {overwrite_flag} -safe {safe} -f concat -i {input_file} -c:v {video_codec} -c:a {audio_codec} -b:a {audio_bitrate}k{video_bitrate_arg}{preset_arg} {output_file}.mp4",
    "ffmpeg {overwrite_flag} -i 'concat:{input_str}' -c copy {output_file}.mp4"
]

FFMPEG_CUT_CMD_TEMPLATES = [
    "ffmpeg {overwrite_flag} -i {input_file}{start_time_arg}{end_time_arg} -c:v {video_codec} -c:a {audio_codec} -b:a {audio_bitrate}k{video_bitrate_arg}{preset_arg} {output_file}",
    "ffmpeg {overwrite_flag} -i {input_file}{start_time_arg}{end_time_arg} -c copy {output_file}"
]
