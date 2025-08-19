from ...imports import *
# ── click handlers ───────────────────────────────────────────────────────
def show_error_for_item(self, item: QListWidgetItem):
    info = item.text()
    try:
        path, line, col = self._parse_item(info)
        if self.cb_try_alt_ext.isChecked():
            path = resolve_alt_ext(path, self.path_in.text().strip())
        os.system(f'code -g "{path}:{line}:{col or 1}"')
        snippet = self._extract_errors_for_file(self.last_output, path, self.path_in.text().strip())
        self._replace_log(snippet if snippet else f"(No specific lines found for {path})\n\n{self.last_output}")
    except Exception:
        self.append_log("show_error_for_item error:\n" + traceback.format_exc() + "\n")

def open_in_editor(self, item: QListWidgetItem):
    try:
        text = item.text()
        path, line, col = self._parse_item(text)
        if self.cb_try_alt_ext.isChecked():
            path = resolve_alt_ext(path, self.path_in.text().strip())
        os.system(f'code -g "{path}:{line}:{col or 1}"')
    except Exception:
        self.append_log("open_in_editor error:\n" + traceback.format_exc() + "\n")

