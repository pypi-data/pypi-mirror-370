from ..functions import *
from .initFuncs import initFuncs
class extractImportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        # Directory picker
        self.dir_in = QLineEdit(os.getcwd())
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.browse_dir)
        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)
        # Run
        self.btn_run = QPushButton("Extract Imports")
        self.btn_run.clicked.connect(self.start_extract)
        # Layout form
        r = 0
        grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(self.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
        flag_row = QHBoxLayout()
        flag_row.addWidget(self.chk_recursive)
        grid.addLayout(flag_row, r, 0, 1, 3); r+=1
        self.layout().addLayout(grid)
        cta = QHBoxLayout()
        cta.addWidget(self.btn_run)
        self.layout().addLayout(cta)
        # Output area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.layout().addWidget(QLabel("Extracted Imports"))
        self.layout().addWidget(self.log, stretch=2)

extractImportsTab = initFuncs(extractImportsTab)
