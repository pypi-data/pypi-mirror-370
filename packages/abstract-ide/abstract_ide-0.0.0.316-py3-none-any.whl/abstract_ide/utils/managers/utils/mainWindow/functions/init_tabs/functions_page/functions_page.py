# functions_console.py
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit, QPushButton,
    QListWidget, QButtonGroup, QRadioButton, QComboBox, QLabel, QTextEdit,
    QSizePolicy, QLayout
)
import os

# --- FlowLayout (chips that wrap) -------------------------------------------
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, hspacing=8, vspacing=6):
        super().__init__(parent)
        self._items = []; self._h = hspacing; self._v = vspacing
        self.setContentsMargins(margin, margin, margin, margin)
    def addItem(self, item): self._items.append(item)
    def addWidget(self, w): super().addWidget(w)
    def count(self): return len(self._items)
    def itemAt(self, i): return self._items[i] if 0 <= i < len(self._items) else None
    def takeAt(self, i): return self._items.pop(i) if 0 <= i < len(self._items) else None
    def expandingDirections(self): return Qt.Orientations(0)
    def hasHeightForWidth(self): return True
    def heightForWidth(self, w): return self._doLayout(QRect(0,0,w,0), True)
    def setGeometry(self, r): super().setGeometry(r); self._doLayout(r, False)
    def sizeHint(self): return self.minimumSize()
    def minimumSize(self):
        s = QSize()
        for it in self._items: s = s.expandedTo(it.minimumSize())
        m = self.contentsMargins()
        s += QSize(m.left()+m.right(), m.top()+m.bottom())
        return s
    def _doLayout(self, rect, test):
        x = rect.x(); y = rect.y(); lineH = 0
        m = self.contentsMargins()
        x += m.left(); y += m.top(); right = rect.right() - m.right()
        for it in self._items:
            sz = it.sizeHint(); w = sz.width(); h = sz.height()
            if x + w > right and lineH > 0:
                x = rect.x() + m.left(); y += lineH + self._v; lineH = 0
            if not test: it.setGeometry(QRect(QPoint(x, y), sz))
            x += w + self._h; lineH = max(lineH, h)
        return y + lineH + m.bottom() - rect.y()

# --- Console ---------------------------------------------------------------
class FunctionConsole(QWidget):
    functionSelected = pyqtSignal(str)
    scanRequested = pyqtSignal(str)  # scope string ("all" | "reachable")

    def __init__(self, parent=None, use_flow=True):
        super().__init__(parent)
        self.func_map = {}
        self.fn_filter_mode = "io"
        self.current_fn = None
        self._build_ui(use_flow)

    # ---- public API --------------------------------------------------------
    def setData(self, func_map: dict):
        """Provide/refresh the function index."""
        self.func_map = func_map or {}
        self._rebuild_fn_buttons(self.func_map.keys())

    def appendLog(self, text: str):
        """Append text to the console log."""
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)
        self.log_view.insertPlainText(text)

    # ---- UI ---------------------------------------------------------------
    def _build_ui(self, use_flow: bool):
        root = QHBoxLayout(self)

        # left panel
        left = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Scope:"))
        self.scope_combo = QComboBox(); self.scope_combo.addItems(["all", "reachable"])
        row.addWidget(self.scope_combo)
        left.addLayout(row)

        self.btn_scan = QPushButton("Scan Project Functions")
        left.addWidget(self.btn_scan)

        self.search_fn = QLineEdit(); self.search_fn.setPlaceholderText("Filter functions…")
        left.addWidget(self.search_fn)

        self.rb_fn_source = QRadioButton("Function")
        self.rb_fn_io = QRadioButton("Import/Export"); self.rb_fn_io.setChecked(True)
        self.rb_fn_all = QRadioButton("All")
        self.fn_filter_group = QButtonGroup(self)
        for rb in (self.rb_fn_source, self.rb_fn_io, self.rb_fn_all):
            self.fn_filter_group.addButton(rb); left.addWidget(rb)

        # scroll area for function "chips"
        self.fn_scroll = QScrollArea(); self.fn_scroll.setWidgetResizable(True)
        self.fn_container = QWidget()
        if use_flow:
            self.fn_layout = FlowLayout(self.fn_container, hspacing=8, vspacing=6)
            self.fn_container.setLayout(self.fn_layout)
        else:
            # fallback: vertical list aligned left
            box = QVBoxLayout(self.fn_container); box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.fn_layout = box
        self.fn_scroll.setWidget(self.fn_container)
        left.addWidget(self.fn_scroll)

        # right panel
        right = QVBoxLayout()
        right.addWidget(QLabel("Exported In"))
        self.exporters_list = QListWidget(); right.addWidget(self.exporters_list)
        right.addWidget(QLabel("Imported In"))
        self.importers_list = QListWidget(); right.addWidget(self.importers_list)
        right.addWidget(QLabel("Log"))
        self.log_view = QTextEdit(); self.log_view.setReadOnly(True); right.addWidget(self.log_view)

        root.addLayout(left, 1)
        root.addLayout(right, 2)

        # wire signals
        self.btn_scan.clicked.connect(lambda: self.scanRequested.emit(self.scope_combo.currentText()))
        self.search_fn.textChanged.connect(self._filter_fn_buttons)
        self.rb_fn_source.toggled.connect(lambda _: self._on_filter_mode_changed())
        self.rb_fn_io.toggled.connect(lambda _: self._on_filter_mode_changed())
        self.rb_fn_all.toggled.connect(lambda _: self._on_filter_mode_changed())
        # double-click to open in VS Code (optional)
        self.exporters_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))
        self.importers_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))

    # ---- internals --------------------------------------------------------
    def _add_fn_button(self, name: str):
        btn = QPushButton(name)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.clicked.connect(lambda _, n=name: self._on_function_clicked(n))
        # FlowLayout supports addWidget; QVBoxLayout does too
        self.fn_layout.addWidget(btn)

    def _clear_fn_buttons(self):
        while self.fn_layout.count():
            it = self.fn_layout.takeAt(0)
            w = it.widget()
            if w: w.deleteLater()

    def _rebuild_fn_buttons(self, names_iterable):
        self._clear_fn_buttons()
        names = sorted(n for n in names_iterable if n and n != '<reexport>')
        for name in names:
            self._add_fn_button(name)

    def _filter_fn_buttons(self, text: str):
        t = (text or '').strip().lower()
        if not self.func_map:
            return
        if not t:
            self._rebuild_fn_buttons(self.func_map.keys())
        else:
            match = [n for n in self.func_map.keys() if t in n.lower()]
            self._rebuild_fn_buttons(match)

    def _on_filter_mode_changed(self):
        self.fn_filter_mode = "source" if self.rb_fn_source.isChecked() else ("all" if self.rb_fn_all.isChecked() else "io")
        if self.current_fn:
            self._render_fn_lists_for(self.current_fn)

    def _on_function_clicked(self, fn_name: str):
        self.current_fn = fn_name
        self.functionSelected.emit(fn_name)
        self._render_fn_lists_for(fn_name)

    def _render_fn_lists_for(self, fn_name: str):
        self.exporters_list.clear()
        self.importers_list.clear()
        data = self.func_map.get(fn_name, {'exported_in': [], 'imported_in': []})

        exported_in, imported_in = [], []
        if isinstance(data, dict):
            exported_in = list(dict.fromkeys(data.get('exported_in', [])))
            imported_in = list(dict.fromkeys(data.get('imported_in', [])))
        elif isinstance(data, list):
            for d in data:
                if isinstance(d, dict):
                    exported_in += d.get('exported_in', [])
                    imported_in += d.get('imported_in', [])
                elif isinstance(d, str):
                    exported_in.append(d); imported_in.append(d)
            exported_in = list(dict.fromkeys(exported_in))
            imported_in = list(dict.fromkeys(imported_in))

        mode = self.fn_filter_mode
        if mode == "source":
            for f in sorted(exported_in): self.exporters_list.addItem(f)
        elif mode == "io":
            for f in sorted(exported_in): self.exporters_list.addItem(f)
            for f in sorted(imported_in): self.importers_list.addItem(f)
        else:  # all
            union = sorted(set(exported_in) | set(imported_in))
            for f in union: self.exporters_list.addItem(f)

    def _start_func_scan(self, scope: str):
            path = self.path_in.text().strip()
            if not path or not os.path.isdir(path):
                QMessageBox.critical(self, "Error", "Invalid project path.")
                return
            self.func_console.appendLog(f"[map] starting scan ({scope})\n")

            entries = ["index", "main"]
            self.map_worker = ImportGraphWorker(path, scope=scope, entries=entries)
            self.map_worker.log.connect(self.func_console.appendLog)
            self.map_worker.ready.connect(self._on_map_ready)
            self.map_worker.finished.connect(lambda: self.func_console.appendLog("[map] done.\n"))
            self.map_worker.start()

    def _on_map_ready(self, graph: dict, func_map: dict):
            self.graph = graph or {}
            self.func_map = func_map or {}
            self.func_console.setData(self.func_map)
    def create_radio_group(self, labels, default_index=0, slot=None):
            """
            Create a QButtonGroup with QRadioButtons for the given labels.

            Args:
                self: parent widget (e.g. 'self' inside a class)
                labels (list[str]): button labels
                default_index (int): which button to check by default
                slot (callable): function to connect all toggled signals to
            Returns:
                (QButtonGroup, list[QRadioButton])
            """
            group = QButtonGroup(self)
            buttons = []

            for i, label in enumerate(labels):
                rb = QRadioButton(label)
                if i == default_index:
                    rb.setChecked(True)
                group.addButton(rb)
                buttons.append(rb)
                if slot:
                    rb.toggled.connect(slot)

            return group, buttons

