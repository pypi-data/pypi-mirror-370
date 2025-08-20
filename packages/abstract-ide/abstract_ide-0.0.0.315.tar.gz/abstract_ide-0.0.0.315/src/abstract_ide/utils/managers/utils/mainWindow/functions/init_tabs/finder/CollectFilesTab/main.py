from ..functions import *
from .initFuncs import initFuncs
# New Tab: Directory Map
# New Tab: Collect Files
class collectFilesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)
        # Extensions (comma-separated)
        self.exts_in = QLineEdit("ts,tsx,js,jsx,css")
        self.exts_in.setPlaceholderText("ts,tsx,js,jsx,css")
        # Optional: restrict to a sub-path (regex or boolean True)
        self.paths_in = QLineEdit("")
        self.paths_in.setPlaceholderText("True (all) or regex like ^src/")
        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)
        # Run + Open in editor
        self.btn_run = QPushButton("Collect Files")
        self.btn_run.clicked.connect(self.start_collect)
        self.btn_open_all = QPushButton("Open all files in VS Code")
        self.btn_open_all.clicked.connect(self.open_all_hits)
        self.btn_open_all.setEnabled(False)
        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
        grid.addWidget(QLabel("Extensions"),r, 0); grid.addWidget(self.exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Paths"), r, 0); grid.addWidget(self.paths_in, r, 1, 1, 2); r+=1
        flag_row = QHBoxLayout()
        flag_row.addWidget(self.chk_recursive)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1
        self.layout().addLayout(grid)
        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        cta.addStretch(1)
        cta.addWidget(self.btn_open_all)
        self.layout().addLayout(cta)
        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Results"))
        self.layout().addWidget(self.log, stretch=2)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.open_one)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []


collectFilesTab = initFuncs(collectFilesTab)
