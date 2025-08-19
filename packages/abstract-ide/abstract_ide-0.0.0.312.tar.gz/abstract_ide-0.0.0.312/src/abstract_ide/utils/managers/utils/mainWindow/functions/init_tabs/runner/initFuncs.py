
from ..imports import *
from .functions import (_extract_errors_for_file, _on_map_ready, _parse_item, _pick_build_cmd, _replace_log, _run_build_qprocess, append_log, apply_log_filter, build_warnings_list, clear_ui, getRunner, initializeInit, open_in_editor, scan_functions, set_last_output, show_error_entries, show_error_for_item, show_warning_entries, start_work)

def initFuncs(self):
    try:
        for f in (_extract_errors_for_file, _on_map_ready, _parse_item, _pick_build_cmd, _replace_log, _run_build_qprocess, append_log, apply_log_filter, build_warnings_list, clear_ui, getRunner, initializeInit, open_in_editor, scan_functions, set_last_output, show_error_entries, show_error_for_item, show_warning_entries, start_work):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
