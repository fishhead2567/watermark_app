#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QObject


class WatermarkConfig:
    def __init__(self):
        self.files_to_watermark = []
        self.output_folder = None
        self.watermark_file = None
        self.watermark_text = None
        self.watermark_text_color = (220, 220, 34, 255)
        self.watermark_locations = []
        self.width_percentage = 0.1
        self.height_percentage = 0.1
        self.do_image_scaling = True
        self.alpha_scale = 1.0
        self.show_generated_images = False

    def reset(self):
        self.files_to_watermark = []
        self.output_folder = None
        self.watermark_file = None
        self.watermark_text = None
        self.watermark_locations = []
        self.width_percentage = 0.1
        self.height_percentage = 0.1
        self.do_image_scaling = True
        self.alpha_scale = 1.0
        self.show_generated_images = False

    def check_valid(self):
        error_messages = []
        if not len(self.files_to_watermark) > 0:
            error_messages.append("You must choose files to watermark")
        if not self.output_folder:
            error_messages.append("You must choose an output folder")
        if self.watermark_file is None and self.watermark_text is None:
            error_messages.append("You must choose a watermark file or set text to apply")
        if not len(self.watermark_locations) > 0:
            error_messages.append("You must choose at least one location to watermark")
        if self.do_image_scaling:
            if not self.width_percentage > 0 and self.width_percentage < 100:
                error_messages.append("width percentage must be between 1 and 100")
            if not self.height_percentage > 0 and self.height_percentage < 100:
                error_messages.append("height percentage must be between 1 and 100")
        return error_messages

    def __str__(self):
        return (
            "WaterMarkConfig:\n"
            f"-files_to_watermark: {self.files_to_watermark}\n"
            f"-output_folder: {self.output_folder}\n"
            f"-watermark_file: {self.watermark_file}\n"
            f"-watermark_text: {self.watermark_text}\n"
            f"-watermark_text_color: {self.watermark_text_color}\n"
            f"-watermark_locations: {self.watermark_locations}\n"
            f"-width_percentage: {self.width_percentage}\n"
            f"-height_percentage: {self.height_percentage}\n"
            f"-do_image_scaling: {self.do_image_scaling}\n"
            f"-alpha_scale: {self.alpha_scale}\n"
            f"-show_generated_images: {self.show_generated_images}"
        )

class WatermarkConfigQt(QObject):
    def __init__(self):
        super().__init__()
        self.watermark_config = WatermarkConfig()

    def width_changed(self, value):
        try:
            self.watermark_config.width_percentage = float(value) / 100.0
            print(f"width changed {self.watermark_config.width_percentage}")
        except ValueError:
            pass

    def height_changed(self, value):
        try:
            self.watermark_config.height_percentage = float(value) / 100.0
            print(f"height changed {self.watermark_config.height_percentage}")
        except ValueError:
            pass

    def watermark_location_changed(self, button, checked):
        value = button.text()
        if not checked and value in self.watermark_config.watermark_locations:
            self.watermark_config.watermark_locations.remove(value)
        elif checked and value not in self.watermark_config.watermark_locations:
            self.watermark_config.watermark_locations.append(value)
        print("VALUE!", value, "state", checked)

    def text_changed(self, value):
        print(f"text changed {value}")
        if len(value) == 0:
            self.watermark_config.watermark_text = None
        else:
            self.watermark_config.watermark_text = value

    def do_image_scale_changed(self, checked):
        self.watermark_config.do_image_scaling = checked == 2
        print(f"Scaling changed {self.watermark_config.do_image_scaling}")
