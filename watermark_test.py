#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PIL import Image

import watermark
from watermark_config import WatermarkConfig

WATERMARK_FILE = os.path.abspath("./test/watermark_image.png")
TEST_FILE = os.path.abspath("./test/base_image.png")
OUT_DIRECTORY = os.path.abspath("./test/")

def _CreateBaseConfig():
    config = WatermarkConfig()
    config.watermark_file = WATERMARK_FILE
    config.files_to_watermark = [TEST_FILE]
    config.output_folder = OUT_DIRECTORY
    config.watermark_locations = ["top-left", "bottom-right"]
    return config


def test_load_image():
    config = _CreateBaseConfig()
    watermark_image, errors = watermark.load_image(WATERMARK_FILE)
    assert (len(errors) == 0)


def test_ImageResize():
    config = _CreateBaseConfig()
    watermark_image, errors = watermark.load_image(WATERMARK_FILE)
    base_image, errors = watermark.load_image(TEST_FILE)
    watermark.maybe_resize_image(config, base_image, watermark_image)


def test_GetWatermarkPosition():
    config = _CreateBaseConfig()
    watermark_image, errors = watermark.load_image(WATERMARK_FILE)
    base_image, errors = watermark.load_image(TEST_FILE)
    for location in config.watermark_locations:
        positon, errors = watermark.get_watermark_position(
            location, base_image.size, watermark_image.size)
        assert(len(errors) == 0)

def test_ApplyWatermark():
    config = _CreateBaseConfig()
    watermark_image, errors = watermark.load_image(WATERMARK_FILE)
    base_image, errors = watermark.load_image(TEST_FILE)
    output_image, errors = watermark.apply_watermark_to_image(config, watermark_image, base_image)
    assert(len(errors) == 0)
