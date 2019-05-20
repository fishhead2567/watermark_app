#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt5 import QtWidgets

from gui.watermark_progress_dialog import ProgressDialog
from gui.watermark_window_ui import Ui_MainWindow
from watermark_config import WatermarkConfigQt


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.watermark_config = WatermarkConfigQt()
        self.checkboxes = {}

        # Add Checkboxes for watermark pairings
        self.checkbox_button_group = QtWidgets.QButtonGroup(
            self.ui.centralwidget)
        self.checkbox_button_group.setExclusive(False)
        self.checkbox_button_group.buttonToggled.connect(
            self.watermark_config.watermark_location_changed)
        # self.ui.CheckBoxContainer.addWidget(self.checkbox_button_group)
        for box_vertical in ["top", "bottom"]:
            for box_horizontal in ["left", "right"]:
                opts = [box_vertical, box_horizontal]
                key = "-".join(opts)
                self.checkboxes[key] = [
                    QtWidgets.QCheckBox(self.ui.centralwidget), opts
                ]
                self.checkboxes[key][0].setObjectName(key)
                self.ui.CheckBoxContainer.addWidget(self.checkboxes[key][0])
                self.checkbox_button_group.addButton(self.checkboxes[key][0])
                self.checkboxes[key][0].setText(key)
                # self.checkboxes[key][0].toggled.connect(self.watermark_config.watermark_location_changed)

        # Hookup Config Params
        self.ui.widthScale.textEdited.connect(
            self.watermark_config.width_changed)
        self.ui.heightScale.textEdited.connect(
            self.watermark_config.height_changed)

        #Hookup dialogs
        self.ui.toWatermarkButton.clicked.connect(self.SetFilesToWatermark)
        self.ui.waterMarkFileButton.clicked.connect(self.SetWatermarkToApply)
        self.ui.outputFolderButton.clicked.connect(self.SetOutputFolder)
        self.ui.watermarkButton.clicked.connect(self.DoWatermarks)

    def SetFilesToWatermark(self):
        dlg = QtWidgets.QFileDialog()
        # dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        filenames = []

        if dlg.exec_():
            print("files chosen")
            filenames = dlg.selectedFiles()
            self.watermark_config.watermark_config.files_to_watermark = filenames
            self.ui.toWatermarkList.clear()
            for item in self.watermark_config.watermark_config.files_to_watermark:
                self.ui.toWatermarkList.addItem(item)

    def SetWatermarkToApply(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        filenames = []

        if dlg.exec_():
            print("file chosen")
            filename = dlg.selectedFiles()[0]
            self.watermark_config.watermark_config.watermark_file = filename
            self.ui.watermarkFile.setText(
                self.watermark_config.watermark_config.watermark_file)

    def SetOutputFolder(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        # dlg.setFilter("Text files (*.txt)")
        directory_name = None

        if dlg.exec_():
            print("dir chosen")
            directory_name = dlg.selectedFiles()
            self.watermark_config.watermark_config.output_folder = directory_name[
                0]
            self.ui.outputFolder.setText(
                self.watermark_config.watermark_config.output_folder)

    def ErrorDialog(self, messages):
        print("errors", "\n".join(messages))
        error_box = QtWidgets.QMessageBox()
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setText("Errors Detected!")
        error_box.setInformativeText("\n".join(messages))
        error_box.setWindowTitle("Doh!")
        error_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = error_box.exec_()

    def DoWatermarks(self):
        error_messages = self.watermark_config.watermark_config.check_valid()
        if len(error_messages) == 0:
            print("Valid")
        else:
            self.ErrorDialog(error_messages)
            return

        # Create the watermark dialog and configure it
        progress_dialog = ProgressDialog(
            self.watermark_config.watermark_config)
        progress_dialog.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = ApplicationWindow()
    application.show()
    sys.exit(app.exec_())
