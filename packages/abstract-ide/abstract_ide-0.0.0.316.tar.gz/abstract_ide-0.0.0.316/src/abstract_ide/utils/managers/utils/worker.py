from ..imports import *
class Worker(QThread):
    """Runs build in background, emits logs and parsed error entries."""
    log_line = pyqtSignal(str)

    # full combined tsc+build (stripped ANSI)
    build_output = pyqtSignal(str)

    # severity-specific text
    errors_output = pyqtSignal(str)
    warnings_output = pyqtSignal(str)

    # severity-specific entries [(path, line, col)]
    error_entries_found = pyqtSignal(list)
    warn_entries_found = pyqtSignal(list)

    def __init__(self, user: str, project_path: str):
        super().__init__()
        self.user = (user or "").strip()          # blank → local mode
        self.project_path = project_path

    def run(self):
        try:
           
            mode = "SSH" if self.user else "local"
     
            if self.user:
                self.log_line.emit(f">>> Running {mode} build in {self.project_path}\nremotely")
                raw = run_ssh_cmd(self.user, COMMAND, self.project_path)
            else:
                self.log_line.emit(f">>> Running {mode} build in {self.project_path}\n locally")
                raw = run_local_cmd(COMMAND, self.project_path)

            # stream raw output lines to the log pane
            for ln in (raw or "").splitlines():
                self.log_line.emit(ln + "\n")

            text_tsc, text_build = split_sections(raw)
            combined = f"{text_tsc}\n{text_build}".strip()
            self.build_output.emit(combined)

            self.log_line.emit("\n── Build (yarn build) ──\n")
            for ln in (text_build or "").splitlines():
                self.log_line.emit(ln + "\n")

            # severity splits
            errs_text, warns_text = split_by_severity(combined)
            self.errors_output.emit(errs_text)
            self.warnings_output.emit(warns_text)

            # entries per severity
            err_entries = get_entries_for(errs_text, self.project_path)
            warn_entries = get_entries_for(warns_text, self.project_path)

            # Grep fallback for errors only (can mirror for warnings if desired)
            if not err_entries and 'use' in combined:
                grep_results = grep_use_imports(self.project_path)
                if grep_results:
                    self.log_line.emit("\n🔍 Grep hits for 'use' imports:\n")
                    for path, line, _ in grep_results:
                        self.log_line.emit(f"{path}:{line}\n")
                    err_entries = grep_results

            self.error_entries_found.emit(err_entries)
            self.warn_entries_found.emit(warn_entries)

        except Exception:
            self.log_line.emit("\n❌ Exception in Worker:\n" + traceback.format_exc() + "\n")
            self.error_entries_found.emit([])
            self.warn_entries_found.emit([])
