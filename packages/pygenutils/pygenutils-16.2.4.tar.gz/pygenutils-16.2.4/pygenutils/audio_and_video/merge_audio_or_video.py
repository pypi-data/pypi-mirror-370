#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'merge_individual_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.audio_and_video.audio_and_video_manipulation import merge_individual_media_files

#-------------------#
# Define parameters #
#-------------------#

# Simple data #
#-------------#

OUTPUT_EXT = "mp4"

# Input media #
#-------------#

# Media input can be a list of files or a single file containing file names
MEDIA_INPUT = [
    "media_file_name_1.mp3",
    "media_file_name_2.mp4",
    "media_file_name_3.mp3"
]
# MEDIA_INPUT = "media_name_containing_file.txt"

# Output media #
#--------------#

# Merged media file #
OUTPUT_FILE_NAME = f"merged_media_file.{OUTPUT_EXT}"
# OUTPUT_FILE_NAME = None

# Bitrate fractions #
#-------------------#

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

# Safe mode for ffmpeg #
# If True, ffmpeg runs in safe mode to prevent unsafe file operations
SAFE = True

# Overwrite existing files #
# If True, uses '-y' flag; if False, uses '-n' flag (will not overwrite)
OVERWRITE = True

# Command execution parameters #
CAPTURE_OUTPUT = False
RETURN_OUTPUT_NAME = False
ENCODING = "utf-8"
SHELL = True

#------------#
# Operations #
#------------#

merge_individual_media_files(
    MEDIA_INPUT,
    safe=SAFE,
    output_file_name=OUTPUT_FILE_NAME,
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