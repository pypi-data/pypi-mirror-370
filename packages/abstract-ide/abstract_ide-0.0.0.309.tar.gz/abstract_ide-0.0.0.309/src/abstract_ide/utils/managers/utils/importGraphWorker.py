from ..imports import *
from abstract_paths import build_graph_all
class ImportGraphWorker(QThread):
    log = pyqtSignal(str)
    ready = pyqtSignal(dict, dict)

    def __init__(self, project_root: str, scope: str = 'all', entries=None):
        super().__init__()
        self.project_root = project_root
        self.scope = scope
        self.entries = entries or ["index", "main"]  # GUI can override

    def run(self):
        try:
            root = Path(self.project_root).resolve()
            self.log.emit(f"[map] scanning {root} (scope={self.scope})\n")
            if self.scope == "reachable":
                entry = find_entry(root, self.entries)
                self.log.emit(f"[map] entry={entry}\n")
                graph = build_graph_reachable(entry, root)
            else:
                graph = build_graph_all(root)

            func_map = invert_to_function_map(graph)
            self.log.emit(f"[map] files={len(graph['nodes'])} edges={len(graph['edges'])} functions={len(func_map)}\n")
            self.ready.emit(graph, func_map)
        except Exception as e:
            self.log.emit(f"[map] error: {e}\n{traceback.format_exc()}\n")
            self.ready.emit({}, {})
