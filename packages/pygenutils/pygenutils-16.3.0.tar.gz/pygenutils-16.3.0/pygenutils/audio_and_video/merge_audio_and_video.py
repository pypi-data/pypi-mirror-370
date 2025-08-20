#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'merge_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from filewise.file_operations.path_utils import find_files
from pygenutils.audio_and_video.audio_and_video_manipulation import merge_media_files

#-------------------#
# Define parameters #
#-------------------#

# Simple data #
#-------------#

# File type delimiters #
AUDIO_DELIMITER = "audio"
VIDEO_DELIMITER = "video"

# File extensions and globstrings #
AUDIO_EXTENSION = "mp3"
AUDIO_FILE_PATTERN = f"_{AUDIO_DELIMITER}.{AUDIO_EXTENSION}"

VIDEO_EXTENSION = "mp4"
VIDEO_FILE_PATTERN = f"_{VIDEO_DELIMITER}.{VIDEO_EXTENSION}"

# Path to walk into for file searching #
SEARCH_PATH = "(default_search_path)"

# Input media #
#-------------#

# Set common keyword arguments #
COMMON_KWARGS = dict(search_path=SEARCH_PATH, match_type="glob_left")

# Find target audio and video files #
INPUT_AUDIO_FILE_LIST = find_files(AUDIO_FILE_PATTERN, **COMMON_KWARGS)
INPUT_VIDEO_FILE_LIST = find_files(VIDEO_FILE_PATTERN, **COMMON_KWARGS)

# Output media #
#--------------#

# Name output file names manually #
"""Taking into account the names of the files, the simplest way to rename them is by removing the item type"""

OUTPUT_FILE_NAME_LIST = [
    f"{input_audio_file.split(AUDIO_DELIMITER)[0][:-1]}.{VIDEO_EXTENSION}"
    for input_audio_file in INPUT_AUDIO_FILE_LIST
]
# OUTPUT_FILE_NAME_LIST = None

# Zero-padding and bitrate fractions #
#-------------------------------------#

ZERO_PADDING = None

# Audio bitrate fraction (multiplied by 32 to get kbps)
# Common ranges: 2-16 for 64-512kbps (speech to high-quality music)
AUDIO_BITRATE_FRACTION = 4

# Video bitrate fraction (multiplied by 32 to get kbps)  
# Common ranges: 31-3125+ for 1-100+Mbps (360p to 4K+)
VIDEO_BITRATE_FRACTION = 4

# Codec settings #
#----------------#

# Video codec to use (None = no re-encoding, "copy" = stream copy, "libx264" = H.264, etc.)
VIDEO_CODEC = None

# Audio codec to use (None = no re-encoding, "copy" = stream copy, "aac" = AAC, etc.)
AUDIO_CODEC = None

# Encoding preset for video codec (only used if video_codec is not None and not "copy")
PRESET = "medium"

# Overwrite existing files #
# If True, uses '-y' flag; if False, uses '-n' flag (will not overwrite)
OVERWRITE = True

# Command execution parameters #
CAPTURE_OUTPUT = True
RETURN_OUTPUT_NAME = False
ENCODING = "utf-8"
SHELL = True

#-------------------#
# Program operation #
#-------------------#

merge_media_files(
    INPUT_AUDIO_FILE_LIST,
    INPUT_VIDEO_FILE_LIST,
    output_file_list=OUTPUT_FILE_NAME_LIST,
    zero_padding=ZERO_PADDING,
    audio_bitrate_fraction=AUDIO_BITRATE_FRACTION,
    video_bitrate_fraction=VIDEO_BITRATE_FRACTION,
    video_codec=VIDEO_CODEC,
    audio_codec=AUDIO_CODEC,
    preset=PRESET,
    overwrite=OVERWRITE,
    capture_output=CAPTURE_OUTPUT,
    return_output_name=RETURN_OUTPUT_NAME,
    encoding=ENCODING,
    shell=SHELL
)