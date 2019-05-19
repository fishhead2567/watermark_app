#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject


class WatermarkConfig:
    def __init__(self):
        self.files_to_watermark = []
        self.output_folder = None
        self.watermark_file = None
        self.watermark_locations = []
        self.width_percentage = 0.1
        self.height_percentage = 0.1
        self.alpha_scale = 1.0
        self.show_generated_images = False

    def reset():
        self.files_to_watermark = []
        self.output_folder = None
        self.watermark_file = None
        self.watermark_locations = []
        self.width_percentage = 0.1
        self.height_percentage = 0.1
        self.alpha_scale = 1.0
        self.show_generated_images = False

    def check_valid(self):
        error_messages = []
        if not len(self.files_to_watermark) > 0:
            error_messages.append("You must choose files to watermark")
        if not self.output_folder:
            error_messages.append("You must choose an output folder")
        if not self.watermark_file:
            error_messages.append("You must choose a watermark file")
        if not len(self.watermark_locations) > 0:
            error_messages.append(
                "You must choose at least one location to watermark")
        if not self.width_percentage > 0 and self.width_percentage < 100:
            error_messages.append("width percentage must be between 1 and 100")
        if not self.height_percentage > 0 and self.height_percentage < 100:
            error_messages.append(
                "height percentage must be between 1 and 100")
        return error_messages


class WatermarkConfigQt(QObject):
    def __init__(self):
        super().__init__()
        self.watermark_config = WatermarkConfig()

    def width_changed(self, value):
        print("width changed")
        self.watermark_config.width_percentage = int(value)

    def height_changed(self, value):
        print("height changed")
        self.watermark_config.height_percentage = int(value)

    def watermark_location_changed(self, button, checked):
        value = button.text()
        if not checked and value in self.watermark_config.watermark_locations:
            self.watermark_config.watermark_locations.remove(value)
        elif checked and value not in self.watermark_config.watermark_locations:
            self.watermark_config.watermark_locations.append(value)
        print("VALUE!", value, "state", checked)
