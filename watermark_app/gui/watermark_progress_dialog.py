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

    def update_gui(self, status, progress, errors):
        self.statusLabel.setText(status)
        self.files_processed = progress
        self.completedItems.setText("%d" % progress)
        self.itemProgress.setProperty("value", progress / len(self.watermark_config.files_to_watermark) * 100)
        if self.files_processed >= len(self.watermark_config.files_to_watermark) or len(errors) > 0:
            self.doneButton.setEnabled(True)
        if len(errors) > 0:
            self.ErrorDialog(errors)

    def ErrorDialog(self, messages):
        print("errors", "\n".join(messages))
        error_box = QtWidgets.QMessageBox()
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setText("Errors Detected!")
        error_box.setInformativeText("\n".join(messages))
        error_box.setWindowTitle("Doh!")
        error_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = error_box.exec_()


class WatermarkThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str, int, list, name="StatusChange")

    def __init__(self, watermark_config):
        QtCore.QThread.__init__(self)
        self.watermark_config = watermark_config
        self.step_text = ""
        self.files_processed = 0
        self.errors = []

    def __del__(self):
        self.wait()

    def set_run_status(self, status, completed_files, errors):
        self.step_text = status
        self.signal.emit(status, completed_files, errors)

    def run(self):
        self.set_run_status("Loading watermark", 0, self.errors)
        watermark_image, errors = watermark.load_watermark_image_and_text(self.watermark_config)

        if len(errors) > 0:
            self.errors += errors

        for image in self.watermark_config.files_to_watermark:
            if len(self.errors) > 0:
                break

            self.set_run_status("processing %s" % image, self.files_processed, self.errors)
            print("processing %s" % image)
            base_image, errors = watermark.load_image(image)
            if len(errors) > 0:
                self.errors += errors

            output_image, errors = watermark.apply_watermark_to_image(
                self.watermark_config, watermark_image, base_image
            )
            if len(errors) > 0:
                self.errors += errors
                pass
            self.files_processed += 1
        if len(self.errors) == 0:
            self.set_run_status("Done", self.files_processed, self.errors)
        else:
            self.set_run_status("Error", self.files_processed, self.errors)
