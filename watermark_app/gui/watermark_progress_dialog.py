from PyQt5 import QtCore, QtGui, QtWidgets

import watermark

from gui.watermark_progress_ui import Ui_Dialog


class ProgressDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, watermark_config, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.watermark_config = watermark_config
        self.watermark_thread = None
        self.files_processed = 0
        self.totalItems.setText("%d" % len(self.watermark_config.files_to_watermark))
        self.doneButton.clicked.connect(self.accept)

    def exec_(self):
        self.begin_watermarks()
        QtWidgets.QDialog.exec_(self)

    def begin_watermarks(self):
        self.watermark_thread = WatermarkThread(self.watermark_config)
        self.watermark_thread.signal.connect(self.update_gui)
        self.watermark_thread.start()

    def update_gui(self, status, progress):
        self.statusLabel.setText(status)
        self.files_processed = progress
        self.completedItems.setText("%d" % progress)
        self.itemProgress.setProperty("value", progress / len(self.watermark_config.files_to_watermark) * 100)
        if self.files_processed >= len(self.watermark_config.files_to_watermark):
            self.doneButton.setEnabled(True)


class WatermarkThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str, int, name="StatusChange")

    def __init__(self, watermark_config):
        QtCore.QThread.__init__(self)
        self.watermark_config = watermark_config
        self.step_text = ""
        self.files_processed = 0

    def __del__(self):
        self.wait()

    def set_run_status(self, status, completed_files):
        self.step_text = status
        self.signal.emit(status, completed_files)

    def run(self):
        self.set_run_status("Loading watermark", 0)
        watermark_image, errors = watermark.load_watermark_image_and_text(self.watermark_config)

        if len(errors) > 0:
            # return (False, errors)
            pass

        for image in self.watermark_config.files_to_watermark:
            self.set_run_status("processing %s" % image, self.files_processed)
            print("processing %s" % image)
            base_image, errors = watermark.load_image(image)
            if len(errors) > 0:
                # return (False, errors)
                pass

            output_image, errors = watermark.apply_watermark_to_image(
                self.watermark_config, watermark_image, base_image
            )
            if len(errors) > 0:
                # return (False, errors)
                pass
            self.files_processed += 1
        self.set_run_status("Done", self.files_processed)
