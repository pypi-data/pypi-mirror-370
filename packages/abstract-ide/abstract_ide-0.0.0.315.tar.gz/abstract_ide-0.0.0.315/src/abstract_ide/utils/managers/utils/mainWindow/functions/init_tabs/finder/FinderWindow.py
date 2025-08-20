from .functions import *
from .CollectFilesTab import collectFilesTab
from abstract_paths.content_utils.DiffParserGui.main import diffParserTab
from .DirectoryMapTab import directoryMapTab
from .ExtractImportsTab import extractImportsTab
from .FinderTab import finderTab
class FinderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔎 Finder — Expanded GUI")
        self.resize(1000, 700)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        self.finder = finderTab()
        tabs.addTab(self.finder, "Find Content")
        self.map_tab = directoryMapTab()
        tabs.addTab(self.map_tab, "Directory Map")
        self.collect_tab = collectFilesTab()
        tabs.addTab(self.collect_tab, "Collect Files")
        self.imports_tab = extractImportsTab()
        tabs.addTab(self.imports_tab, "Extract Python Imports")
        self.diff_tab = diffParserTab()
        
        tabs.addTab(self.diff_tab,  "Diff (Repo)")
        layout.addWidget(tabs)
