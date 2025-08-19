from ..functions import *
# — UI helpers —
def browse_dir(self):
    d = QFileDialog.getExistingDirectory(self, "Choose directory", self.dir_in.text() or os.getcwd())
    if d:
        self.dir_in.setText(d)
def make_params(self):
    directory = self.dir_in.text().strip()
    if not directory or not os.path.isdir(directory):
        raise ValueError("Directory is missing or not a valid folder.")
    recursive = self.chk_recursive.isChecked()
    # For python, exts='.py'
    cfg = define_defaults(allowed_exts=['.py'])
    return directory, cfg, recursive
def start_extract(self):
    self.log.clear()
    self.btn_run.setEnabled(False)
    try:
        directory, cfg, recursive = self.make_params()
    except Exception as e:
        QMessageBox.critical(self, "Bad input", str(e))
        self.btn_run.setEnabled(True)
        return
    class ExtractWorker(QThread):
        log = pyqtSignal(str)
        done = pyqtSignal(tuple)
        def __init__(self, directory, cfg, recursive):
            super().__init__()
            self.directory = directory
            self.cfg = cfg
            self.recursive = recursive # note: collect_filepaths is recursive by default
        def run(self):
            try:
                py_files = collect_filepaths([self.directory], self.cfg)
                module_paths, imports = get_py_script_paths(py_files)
                self.done.emit((module_paths, imports))
            except Exception:
                self.log.emit(traceback.format_exc())
                self.done.emit(([], []))
    self.worker = ExtractWorker(directory, cfg, recursive)
    self.worker.log.connect(self.append_log)
    self.worker.done.connect(self.display_imports)
    self.worker.finished.connect(lambda: self.btn_run.setEnabled(True))
    self.worker.start()
def append_log(self, text: str):
    self.log.moveCursor(self.log.textCursor().End)
    self.log.insertPlainText(text)
def display_imports(self, result: tuple):
    module_paths, imports = result
    if not imports:
        self.append_log("✅ No imports found.\n")
        return
    output = "Module Paths:\n" + "\n".join(module_paths) + "\n\nImports:\n" + "\n".join(imports)
    self.log.setPlainText(output)
