from ..functions import *
from .initFuncs import initFuncs
# New Tab: Directory Map
class directoryMapTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)
        # Allowed Extensions (comma-separated)
        self.allowed_exts_in = QLineEdit("ts,tsx,js,jsx,css")
        self.allowed_exts_in.setPlaceholderText("ts,tsx,js,jsx,css")
        # Unallowed Extensions (comma-separated)
        self.unallowed_exts_in = QLineEdit("")
        self.unallowed_exts_in.setPlaceholderText("pdf,docx")
        # Exclude Types (comma-separated)
        self.exclude_types_in = QLineEdit("")
        self.exclude_types_in.setPlaceholderText("image,video,audio")
        # Exclude Dirs (comma-separated)
        self.exclude_dirs_in = QLineEdit("")
        self.exclude_dirs_in.setPlaceholderText("")
        # Exclude Patterns (comma-separated)
        self.exclude_patterns_in = QLineEdit("")
        self.exclude_patterns_in.setPlaceholderText("")
        # Prefix
        self.prefix_in = QLineEdit("")
        self.prefix_in.setPlaceholderText("Optional prefix")
        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)
        self.chk_include_files = QCheckBox("Include Files"); self.chk_include_files.setChecked(True)
        self.chk_add = QCheckBox("Add to defaults"); self.chk_add.setChecked(False)
        # Run
        self.btn_run = QPushButton("Get Directory Map")
        self.btn_run.clicked.connect(self.start_map)
        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
        grid.addWidget(QLabel("Allowed Exts"), r, 0); grid.addWidget(self.allowed_exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Unallowed Exts"), r, 0); grid.addWidget(self.unallowed_exts_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Types"), r, 0); grid.addWidget(self.exclude_types_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Dirs"), r, 0); grid.addWidget(self.exclude_dirs_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Exclude Patterns"), r, 0); grid.addWidget(self.exclude_patterns_in, r, 1, 1, 2); r+=1
        grid.addWidget(QLabel("Prefix"), r, 0); grid.addWidget(self.prefix_in, r, 1, 1, 2); r+=1
        flag_row = QHBoxLayout()
        flag_row.addWidget(self.chk_recursive)
        flag_row.addWidget(self.chk_include_files)
        flag_row.addWidget(self.chk_add)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1
        self.layout().addLayout(grid)
        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        self.layout().addLayout(cta)
        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Directory Map"))
        self.layout().addWidget(self.log, stretch=2)

directoryMapTab = initFuncs(directoryMapTab)
