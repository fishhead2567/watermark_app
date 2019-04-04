"""watermark

Applies a watermark to a set of images. Note: input_images, output_folder 
and "watermark" must be in quotes!

Usage:
  watermark.py <input_images> <output_folder> <watermark> [options]
  
Options:
  --show                    Whether to show each generated image
  --vertical_anchor = [top, bottom, center, random] Where to anchor the watermark vertically
  --horizontal_anchor = [left, right, center, random] where to anchor the watermark horizontally
"""


import glob
import os
import sys

from random import randint
from types import SimpleNamespace

from docopt import docopt

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

VALID_VERTICAL = ['bottom', 'top', 'center', 'random']
VALID_HORIZONTAL = ['right', 'left', 'center', 'random']

def config_from_arguments(arguments):
    config = SimpleNamespace(
        input_file_regex=None,
        output_directory=None,
        watermark_file=None,
        show_images=False,
        vertical_anchor=VALID_VERTICAL[0],
        horizontal_anchor=VALID_HORIZONTAL[0])
    config.input_file_regex = arguments["<input_images>"]
    config.output_directory = arguments["<output_folder>"]
    config.watermark_file = arguments["<watermark>"]
    if arguments["--show"] is not None:
        config.show_images = arguments["--show"]
    if arguments["--vertical_anchor"] in VALID_VERTICAL:
        config.vertical_anchor = arguments["--vertical_anchor"]
    else:
        print("Using default vertical anchor position: %s" % VALID_VERTICAL[0])
    if arguments["--horizontal_anchor"] in VALID_HORIZONTAL:
        config.horizontal_anchor = arguments["--horizontal_anchor"]
    else:
        print("Using default horizontal anchor position: %s" % (
            VALID_HORIZONTAL[0]))
    
    return config

def load_watermark(watermark_image_path):
    watermark = None
    try:
        watermark = Image.open(watermark_image_path)
 
    except:
        print("Watermark failed to load. Is %s a valid file? " % (
            watermark_image_path))
        sys.exit(1)
    return watermark

def _get_watermark_position(image_size, watermark_size, config):
    valid_x_max = image_size[0] - watermark_size[0]
    valid_y_max = image_size[1] - watermark_size[1]
    if valid_x_max < 0 or valid_y_max < 0:
        print("Watermark was bigger than image!")
        print("Image W: %d, H: %d" % (image_size[0], image_size[1]))
        print("WM W: %d, H: %d" % (watermark_size[0], watermark_size[1]))
        sys.exit(1)
    watermark_position = [0,0]
    
    if config.horizontal_anchor == 'right':
        watermark_position[0] = valid_x_max
    elif config.horizontal_anchor == 'center':
        watermark_position[0] = int(float(valid_x_max) / 2.0)
    elif config.horizontal_anchor == 'random':
        watermark_position[0] = randint(0, valid_x_max)
    if config.vertical_anchor == 'bottom':
        watermark_position[1] = valid_y_max
    elif config.vertical_anchor == 'center':
        watermark_position[1] = int(float(valid_y_max) / 2.0)
    elif config.vertical_anchor == 'random':
        watermark_position[1] = randint(0, valid_y_max)
    print(watermark_position)
    return watermark_position


def apply_watermark_to_image(watermark_image, filename_input, filename_output, config):
        print("    %s" % (filename_input))
        image = None
        try:
            image = Image.open(filename_input)
        except Exception as e:
            print("Could not load image: %s. Error was: %s" % (
                filename_input, str(e)))
            raise e
        watermark_position = _get_watermark_position(image.size,
                                                     watermark_image.size,
                                                     config)
        output_image =  Image.new('RGBA', image.size, (0,0,0,0))
        output_image .paste(image, (0,0))
        output_image.paste(watermark, watermark_position, mask=watermark)
        if config.show_images:
            output_image.show()
        output_image.save(filename_output)

def apply_watermark_to_images(watermark_image, images_list,
                              output_directory, config):
    print("Processing Images:")
    for image_path in images_list:
        image_filename = os.path.basename(image_path)
        output_filename = image_filename.split(".")[0] + ".png"
        output_path = os.path.join(output_directory, output_filename)
        apply_watermark_to_image(watermark_image, image_path, output_path,
                                 config)

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
    if os.path.exists(output_folder_path):
        if not os.path.isdir(output_folder_path):
            print("Output path exists and is not a folder.")
            sys.exit(1)
        else:
            return os.path.abspath(output_folder_path)
    
    try:
        os.mkdir(output_folder_path)
    except Exception as e:
        print("Unable to create output path. Error was: %s" % (str(e)))
        raise e

    return os.path.abspath(output_folder_path)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)
    
    # Load config
    config = config_from_arguments(arguments)

    # Load the watermark image
    watermark = load_watermark(config.watermark_file)

    # Load the files to watermark
    image_files = find_files(config.input_file_regex)
    
    # Create output folder
    output_folder = create_folder(config.output_directory)

    # Apply the watermark 
    apply_watermark_to_images(watermark, image_files, output_folder,
                              config)