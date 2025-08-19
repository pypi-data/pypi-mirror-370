from ..functions import *
from .initFuncs import initFuncs
class diffParserTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        # File picker
        h1 = QHBoxLayout()
        self.file_in = QLineEdit()
        btn_browse = QPushButton("Browse File")
        btn_browse.clicked.connect(self.browse_file)
        h1.addWidget(QLabel("File:"))
        h1.addWidget(self.file_in)
        h1.addWidget(btn_browse)
        self.layout().addLayout(h1)
        # Diff paste area
        self.diff_text = QTextEdit()
        self.diff_text.setPlaceholderText("Paste the diff here...")
        self.layout().addWidget(QLabel("Diff:"))
        self.layout().addWidget(self.diff_text, stretch=1)
        # Parse button
        btn_parse = QPushButton("Parse and Preview")
        btn_parse.clicked.connect(self.preview_patch)
        self.layout().addWidget(btn_parse)
        # Preview area
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.layout().addWidget(QLabel("Preview:"))
        self.layout().addWidget(self.preview, stretch=1)
        # Approve save
        btn_save = QPushButton("Approve and Save")
        btn_save.clicked.connect(self.save_patch)
        self.layout().addWidget(btn_save)

diffParserTab = initFuncs(diffParserTab)
