#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**

This program is an application of the main module 'audio_and_video_manipulation',
and it relies on the method 'cut_media_files'.
YOU MAY REDISTRIBUTE this program along any other directory,
but keep in mind that the module is designed to work with absolute paths.
"""

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.audio_and_video.audio_and_video_manipulation import cut_media_files

#-------------------#
# Define parameters #
#-------------------#

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
OUTPUT_FILE_LIST = [
    "media_file_name_1_trimmed.mp3",
    "media_file_name_2_trimmed.mp4",
    "media_file_name_3_trimmed.mp3"
]
# OUTPUT_FILE_LIST = None

# Starting and ending times #
START_TIME_LIST = ["start", "00:01:28", "00:02:28.345"]
END_TIME_LIST = ["00:05:21", "end", "00:07:56.851"]

# Zero-padding and bitrate fractions #
#------------------------------------#

ZERO_PADDING = 1

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
CAPTURE_OUTPUT = False
RETURN_OUTPUT_NAME = False
ENCODING = "utf-8"
SHELL = True

#------------#
# Operations #
#------------#

cut_media_files(
    MEDIA_INPUT,
    START_TIME_LIST,
    END_TIME_LIST,
    output_file_list=OUTPUT_FILE_LIST,
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