#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""watermark

Applies a watermark to a set of images. Note: input_images, output_folder
and "watermark" must be in quotes!

Usage:
  watermark.py <input_images> <output_folder> <watermark> [options]

Options:
  --show                       Whether to show each generated image
  --vertical_anchor=<string>   [top, bottom, center, random] Where to anchor the watermark vertically
  --horizontal_anchor=<string> [left, right, center, random] where to anchor the watermark horizontally
  --alpha_scale=<int>          scale the transparency of the watermark [default: 1.0]
  --min_horizontal_ratio=<int> Minimum ratio between horizontal sizes of watermark and bas images [default: 0.1]
  --min_vertical_ratio=<int>   Minimum ratio between vertical sizes of watermark and bas images [default: 0.1]
"""

import glob
import os
import sys

from random import randint
from types import SimpleNamespace

from docopt import docopt
from PIL import Image, ImageChops

from watermark_config import WatermarkConfig
from watermark import apply_watermark

VALID_VERTICAL = ['bottom', 'top', 'center', 'random']
VALID_HORIZONTAL = ['right', 'left', 'center', 'random']


def config_from_arguments(arguments):

    config = SimpleNamespace(watermark_config=WatermarkConfig(),
                             input_file_regex=None)
    config.input_file_regex = arguments["<input_images>"]
    config.watermark_config.output_folder = arguments["<output_folder>"]
    config.watermark_config.watermark_file = arguments["<watermark>"]
    if arguments["--show"] is not None:
        config.watermark_config.show_generated_images = arguments["--show"]
    watermark_placement = ["top", "left"]
    if arguments["--vertical_anchor"] in VALID_VERTICAL:
        watermark_placement[0] = arguments["--vertical_anchor"]
    if arguments["--horizontal_anchor"] in VALID_HORIZONTAL:
        watermark_placement[1] = arguments["--horizontal_anchor"]
    config.watermark_config.watermark_locations.append(
        "-".join(watermark_placement))
    print("Using watermark location: ",
          config.watermark_config.watermark_locations[-1])
    try:
        config.watermark_config.alpha_scale = float(arguments["--alpha_scale"])
    except ValueError:
        print("Invalid alpha scale value")
    return config


def find_files(file_search_path):
    file_list = []
    for filename in glob.glob(file_search_path):
        if os.path.isfile(filename):
            file_list.append(filename)

    if len(file_list) == 0:
        print("No files matching pattern: %s" % (file_search_path))
        sys.exit(1)
    else:
        print("will process the following images:")
        for image in file_list:
            print("", image)

    return file_list


def create_folder(output_folder_path):
    # Attempts to create an output folder. Returns any error messages.
    error_messages = []
    if os.path.exists(output_folder_path):
        if not os.path.isdir(output_folder_path):
            error_messages.append("Output path exists and is not a folder.")
            return error_messages
        else:
            return error_messages

    try:
        os.mkdir(output_folder_path)
    except Exception as e:
        error_messages.append("Unable to create output path. Error was: %s" %
                              (str(e)))
    return error_messages


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    # Load config
    config = config_from_arguments(arguments)

    # Load the files to watermark
    config.watermark_config.files_to_watermark = find_files(
        config.input_file_regex)

    # Create output folder
    error_messages = create_folder(config.watermark_config.output_folder)
    if len(error_messages) > 0:
        print("\n".join(error_messages))
        sys.exit(1)

    # Apply the watermark
    apply_watermark(config.watermark_config)
