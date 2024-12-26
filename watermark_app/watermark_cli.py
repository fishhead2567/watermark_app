import argparse
import glob
import os
import sys
from types import SimpleNamespace

from PIL import Image

from watermark_config import WatermarkConfig
from watermark import apply_watermark

VALID_VERTICAL = ["bottom", "top", "center", "random"]
VALID_HORIZONTAL = ["right", "left", "center", "random"]


def config_from_arguments(arguments):
    config = SimpleNamespace(watermark_config=WatermarkConfig(), input_file_regex=None)
    config.input_file_regex = arguments.input_images
    config.watermark_config.output_folder = arguments.output_folder
    if arguments.watermark_image is not None and len(arguments.watermark_image) > 0:
        config.watermark_config.watermark_file = arguments.watermark_image
    if arguments.watermark_text is not None and len(arguments.watermark_text) > 0:
        config.watermark_config.watermark_text = arguments.watermark_text

    config.watermark_config.show_generated_images = arguments.show
    watermark_placement = ["top", "left"]
    if arguments.vertical_anchor in VALID_VERTICAL:
        watermark_placement[0] = arguments.vertical_anchor
    if arguments.horizontal_anchor in VALID_HORIZONTAL:
        watermark_placement[1] = arguments.horizontal_anchor
    config.watermark_config.do_image_scaling = arguments.scale_image
    config.watermark_config.minimal_watermark_height_percentage = arguments.min_vertical_ratio
    config.watermark_config.minimal_watermark_width_percentage = arguments.min_horizontal_ratio
    config.watermark_config.watermark_locations.append("-".join(watermark_placement))
    try:
        config.watermark_config.alpha_scale = float(arguments.alpha_scale)
    except ValueError:
        print("Invalid alpha scale value")
    print(config.watermark_config)
    return config


def is_valid_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False


def find_files(file_search_path):
    file_list = []
    for filename in glob.glob(file_search_path):
        if os.path.isfile(filename):
            if is_valid_image(filename):
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
        os.makedirs(output_folder_path, exist_ok=True)
    except Exception as e:
        error_messages.append("Unable to create output path. Error was: %s" % (str(e)))
    return error_messages


def parse_arguments():
    parser = argparse.ArgumentParser(description="Applies a watermark to a set of images.")
    parser.add_argument("input_images", type=str, help="Input images pattern")
    parser.add_argument("output_folder", type=str, help="Output folder")
    parser.add_argument("--show", action="store_true", help="Whether to show each generated image")
    parser.add_argument(
        "--vertical_anchor", type=str, choices=VALID_VERTICAL, help="Where to anchor the watermark vertically"
    )
    parser.add_argument(
        "--horizontal_anchor", type=str, choices=VALID_HORIZONTAL, help="Where to anchor the watermark horizontally"
    )
    parser.add_argument("--alpha_scale", type=float, default=1.0, help="Scale the transparency of the watermark")
    parser.add_argument(
        "--scale_image",
        action="store_true",
        help="If True, scale the image so that the watermark sizes according to the ratios provided",
    )
    parser.add_argument(
        "--min_horizontal_ratio",
        type=float,
        default=None,
        help="Minimum ratio between horizontal sizes of watermark and base images",
    )
    parser.add_argument(
        "--min_vertical_ratio",
        type=float,
        default=None,
        help="Minimum ratio between vertical sizes of watermark and base images",
    )
    parser.add_argument(
        "--watermark_image", type=str, help="Image watermark to apply. One of image or text must be provided."
    )
    parser.add_argument(
        "--watermark_text", type=str, help="Text watermark to apply. One of image or text must be provided."
    )
    return parser.parse_args()


def main():
    arguments = parse_arguments()

    # Load config
    config = config_from_arguments(arguments)

    # Load the files to watermark
    config.watermark_config.files_to_watermark = find_files(config.input_file_regex)

    # Create output folder
    error_messages = create_folder(config.watermark_config.output_folder)
    if len(error_messages) > 0:
        print("\n".join(error_messages))
        sys.exit(1)

    # Apply the watermark
    error_messages = config.watermark_config.check_valid()
    assert len(error_messages) == 0, f"Config had errors {error_messages}"
    result, errors = apply_watermark(config.watermark_config)
    if len(errors) > 0:
        raise RuntimeError(f"Errors: {errors}")


if __name__ == "__main__":
    main()
