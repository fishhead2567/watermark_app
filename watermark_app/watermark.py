import os
from random import randint
from tempfile import TemporaryDirectory

from PIL import Image, ImageChops
from PIL import ImageDraw, ImageFont
from pillow_heif import register_heif_opener

register_heif_opener()

from watermark_config import WatermarkConfig

VALID_VERTICAL = ["bottom", "top", "center", "random"]
VALID_HORIZONTAL = ["right", "left", "center", "random"]


def load_image(image_path: str):
    # Loads the watermark image.
    image = None
    error_messages = []
    try:
        image = Image.open(image_path)
    except:
        error_messages.append("Image failed to load. Is %s a valid file? " % (image_path))
        return (None, error_messages)
    return (image, error_messages)


def maybe_resize_image(watermark_config: WatermarkConfig, input_image: Image, watermark_image: Image = None):
    """
    Resize the input image to ensure the watermark meets a desired size ratio if needed.

    The watermark should be at-least the specified ratio of the input image. If resize is needed, do so.
    Args:
        watermark_config (WatermarkConfig): Configuration object containing watermark settings, including whether
            scaling is enabled and the width and height percentages.
        input_image (Image): The input image to potentially resize.
        watermark_image (Image): The watermark image used to determine if resizing is necessary.

    Returns:
        tuple: A tuple containing the potentially resized input image and an empty list.
    """

    if not watermark_config.do_image_scaling or watermark_image is None:
        return (input_image, [])

    scaling_needed = False
    minimal_ratio = 1.0
    watermark_x_ratio = watermark_image.size[1] / input_image.size[1]
    watermark_y_ratio = watermark_image.size[0] / input_image.size[0]
    if (
        watermark_config.minimal_watermark_width_percentage is not None
        and watermark_x_ratio < watermark_config.minimal_watermark_width_percentage
    ):
        scaling_needed = True
        x_target = watermark_image.size[1] / watermark_config.minimal_watermark_width_percentage
        x_scaling = x_target / input_image.size[1]
        if x_scaling < minimal_ratio:
            minimal_ratio = x_scaling
    if (
        watermark_config.minimal_watermark_height_percentage is not None
        and watermark_y_ratio < watermark_config.minimal_watermark_height_percentage
    ):
        scaling_needed = True
        y_target = watermark_image.size[0] / watermark_config.minimal_watermark_height_percentage
        y_scaling = y_target / input_image.size[0]
        if y_scaling < minimal_ratio:
            minimal_ratio = y_scaling
    if scaling_needed:
        print("scaling image", minimal_ratio)
        new_image_size = (int(input_image.size[0] * minimal_ratio), int(input_image.size[1] * minimal_ratio))
        output_image = input_image.resize(new_image_size)
        return (output_image, [])
    return (input_image, [])


def get_watermark_position(anchor: str, image_size: tuple, watermark_size: tuple):
    vertical_anchor, horizontal_anchor = anchor.split("-")

    error_messages = []
    valid_x_max = image_size[0] - watermark_size[0]
    valid_y_max = image_size[1] - watermark_size[1]
    if valid_x_max < 0 or valid_y_max < 0:
        error_messages += [
            "Watermark was bigger than image!",
            "Image W: %d, H: %d" % (image_size[0], image_size[1]),
            "WM W: %d, H: %d" % (watermark_size[0], watermark_size[1]),
        ]
        return (None, error_messages)
    watermark_position = [0, 0]

    if horizontal_anchor == "right":
        watermark_position[0] = valid_x_max
    elif horizontal_anchor == "center":
        watermark_position[0] = int(float(valid_x_max) / 2.0)
    elif horizontal_anchor == "random":
        watermark_position[0] = randint(0, valid_x_max)
    if vertical_anchor == "bottom":
        watermark_position[1] = valid_y_max
    elif vertical_anchor == "center":
        watermark_position[1] = int(float(valid_y_max) / 2.0)
    elif vertical_anchor == "random":
        watermark_position[1] = randint(0, valid_y_max)
    return (watermark_position, [])


def create_text_layer(
    watermark_text: str,
    image_size: tuple,
    text_color: tuple = (255, 255, 255, 128),
    width_ratio: float = None,
    height_ratio: float = None,
):
    if watermark_text is None:
        return None, ["No text specified"]

    if os.name == "nt":
        font_path = "c:\WINDOWS\Fonts\ARIALBD.TTF"
    else:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    if width_ratio is None and height_ratio is None:
        font_size = 36
    else:
        target_height = image_size[0]
        target_width = image_size[1]
        if width_ratio is not None:
            target_width = int(float(image_size[0]) * width_ratio)

        if height_ratio is not None:
            target_height = int(float(image_size[1]) * height_ratio)
        font_size = min(target_width // len(watermark_text) * 2, target_height)

    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = font.getbbox(watermark_text)[2:]
    text_layer = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))

    draw = ImageDraw.Draw(text_layer)
    draw.text((0, 0), watermark_text, font=font, fill=text_color)
    return text_layer, []


def composite_sidebyside(left: Image, right: Image):
    new_width = left.width + right.width
    new_height = max(left.height, right.height)
    new_image = Image.new("RGBA", (new_width, new_height), (0, 0, 0, 0))
    new_image.paste(left, (0, 0))
    new_image.paste(right, (left.width, 0))
    return new_image


def apply_watermark_to_image(
    watermark_config: WatermarkConfig,
    base_image: Image,
    watermark_image: Image = None,
    text_image: Image = None,
    text: str = None,
):
    # Applies the watermark to base_image in the locations specified by watermark_config.
    # with TemporaryDirectory() as temp_dir:
    # ... do something with temp_dir
    base_filename = base_image.filename
    base_exif = base_image.getexif()

    # Resize the image if necessary based on the watermark_image file.
    base_image, errors = maybe_resize_image(watermark_config, base_image, watermark_image)
    output_image = Image.new("RGBA", base_image.size, (0, 0, 0, 0))

    # If we don't have a text layer, we must compute it now.
    if text_image is None and text is not None:
        text_image, errors = create_text_layer(
            text,
            base_image.size,
            text_color=watermark_config.watermark_text_color,
            width_ratio=watermark_config.minimal_watermark_width_percentage,
            height_ratio=watermark_config.minimal_watermark_height_percentage,
        )
        if watermark_image:
            watermark_image = composite_sidebyside(watermark_image, text_image)
        else:
            watermark_image = text_image

    if len(errors) > 0:
        return None, errors

    if watermark_image is None:
        return None, ["Watermark was None. Either no image or no text specified"]

    alpha_scale_value = int(255 * watermark_config.alpha_scale)
    watermark_alpha = watermark_image.split()[-1]
    alpha_scale = ImageChops.constant(watermark_alpha, alpha_scale_value)
    if alpha_scale_value < 255:
        watermark_alpha = ImageChops.multiply(watermark_alpha, alpha_scale)
    for anchor in watermark_config.watermark_locations:
        watermark_position, errors = get_watermark_position(anchor, base_image.size, watermark_image.size)
        output_image.paste(watermark_image, watermark_position, mask=watermark_alpha)
    output_image = Image.alpha_composite(base_image.convert("RGBA"), output_image)
    if watermark_config.show_generated_images:
        output_image.show()
    output_filename = ".".join(os.path.basename(base_filename).split(".")[:-1])
    output_filename = os.path.join(watermark_config.output_folder, "%s_watermarked.png" % (output_filename))
    output_filename = os.path.splitext(output_filename)[0] + ".png"
    output_image.save(output_filename, format="png", optimize=True, exif=base_exif)
    return (output_filename, [])


def preload_watermark_and_text_images(watermark_config):
    watermark_image = None
    text_image = None
    errors = []
    text = watermark_config.watermark_text

    if watermark_config.watermark_file is not None:
        watermark_image, errors = load_image(watermark_config.watermark_file)

    if len(errors) > 0:
        return None, None, None, errors

    if watermark_image is not None and watermark_config.watermark_text_to_image_ratio is not None:
        # We can take the easy path and load both images at the same time. No further text computation will be needed.
        text_image, errors = create_text_layer(
            watermark_config,
            image_size=watermark_image.size,
            text_color=watermark_config.watermark_text_color,
            minimal_width_ratio=watermark_config.watermark_text_to_image_ratio,
            minimal_height_ratio=watermark_config.watermark_text_to_image_ratio,
        )
        if len(errors) > 0:
            return (None, None, None, errors)

        # Composite the watermark and text.
        watermark_image = composite_sidebyside(watermark_image, text_image)
        text_image = None
        text = None
    return watermark_image, text_image, text, errors


def apply_watermark(watermark_config: WatermarkConfig):
    watermark_image, text_image, text, errors = preload_watermark_and_text_images(watermark_config)

    if len(errors) > 0:
        return (False, errors)

    for image in watermark_config.files_to_watermark:
        print("processing: %s" % image)
        base_image, errors = load_image(image)
        if len(errors) > 0:
            return (False, errors)

        output_image, errors = apply_watermark_to_image(
            watermark_config,
            base_image,
            watermark_image,
            text_image,
            text=watermark_config.watermark_text if text_image is None else None,
        )
        if len(errors) > 0:
            return (False, errors)
    return True, []
