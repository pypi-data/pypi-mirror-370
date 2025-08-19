from ..functions import *
# — UI helpers —
def browse_file(self):
    f = QFileDialog.getOpenFileName(self, "Select File")[0]
    if f:
        self.file_in.setText(f)
def preview_patch(self):
    file_path = self.file_in.text().strip()
    if not file_path or not os.path.isfile(file_path):
        QMessageBox.critical(self, "Error", "Invalid file.")
        return
    diff = self.diff_text.toPlainText().strip()
    if not diff:
        QMessageBox.critical(self, "Error", "No diff provided.")
        return
    try:
        with open(file_path, 'r') as f:
            original = f.read()
        patched = apply_custom_diff(original.splitlines(), diff.splitlines())
        self.preview.setPlainText(patched)
    except ValueError as e:
        QMessageBox.critical(self, "Error", str(e))
def save_patch(self):
    file_path = self.file_in.text().strip()
    patched = self.preview.toPlainText()
    if patched:
        with open(file_path, 'w') as f:
            f.write(patched + '\n')
        QMessageBox.information(self, "Success", "File saved.")
    else:
        QMessageBox.warning(self, "Warning", "No preview to save.")


