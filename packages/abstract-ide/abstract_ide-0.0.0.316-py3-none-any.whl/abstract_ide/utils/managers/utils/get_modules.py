import os
# Assuming other necessary imports like json if used in missing functions
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QScrollArea, QLineEdit, QComboBox, QPushButton, QCheckBox, QTextEdit, QListWidget, QFileDialog, QMessageBox, QLabel
# Assume missing functions like get_dev_status_js, get_file_associations, get_all_choice_tags, list_all_directories, check_all_files, get_readme, create_classifiers, get_installed_versions, scan_folder_for_required_modules, write_to_file, get_fun, upload_main, return_opposite_bool, licenses, create_setup_cfg, create_toml, create_setup, create_init, get_main_py, parse_setup are defined elsewhere and remain the same.

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("create module")
        self.resize(800, 600)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        self.widgets = {}
        self.folder_bridge = {"MODULE_NAV_HISTORY": [], "MODULE_FOLDER": None}
        descriptions = self.get_descriptions_layout()
        main_layout.addWidget(descriptions)
        top_layout = QVBoxLayout()
        self.listbox = QListWidget()
        self.listbox.addItems(os.listdir(os.getcwd()))
        self.listbox.setObjectName("-DIRECTORY_LIST-")
        self.listbox.itemClicked.connect(self.on_directory_selected)
        self.listbox.setFixedWidth(200)
        self.listbox.setFixedHeight(300)
        back_btn = QPushButton("<-")
        back_btn.setObjectName("<-")
        forward_btn = QPushButton("->")
        forward_btn.setObjectName("->")
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(back_btn)
        buttons_layout.addWidget(forward_btn)
        listbox_layout = QVBoxLayout()
        listbox_layout.addWidget(self.listbox)
        listbox_layout.addLayout(buttons_layout)
        listbox_column = QWidget()
        listbox_column.setLayout(listbox_layout)
        check_marks = self.create_check_marks()
        choice_tag = self.create_choice_tag_layout()
        dev_status = self.create_dev_status()
        status_layout = QVBoxLayout()
        status_layout.addWidget(check_marks)
        status_layout.addWidget(choice_tag)
        status_layout.addWidget(dev_status)
        status_column = QWidget()
        status_column.setLayout(status_layout)
        top_row = QHBoxLayout()
        top_row.addWidget(listbox_column)
        top_row.addWidget(status_column)
        top_widget = QWidget()
        top_widget.setLayout(top_row)
        top_layout.addWidget(top_widget)
        module_browser = self.get_module_folder_browser()
        top_layout.addWidget(module_browser)
        upload_btn = QPushButton("dev_status")
        upload_btn.setObjectName("-UPLOAD_MODULE-")
        top_layout.addWidget(upload_btn)
        top_frame = QGroupBox("")
        top_frame.setLayout(top_layout)
        main_layout.addWidget(top_frame)
        self.collect_widgets(self)
        for key, widget in self.widgets.items():
            if isinstance(widget, QPushButton):
                widget.clicked.connect(self.on_button_clicked)
            if isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.on_checkbox_changed)
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.on_input_changed)
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self.on_combo_changed)

    def collect_widgets(self, widget):
        for child in widget.children():
            if child.objectName():
                self.widgets[child.objectName()] = child
            self.collect_widgets(child)

    def get_values(self):
        try:
            values = {}
            for key, widget in self.widgets.items():
                if isinstance(widget, QLineEdit):
                    values[key] = widget.text()
                elif isinstance(widget, QComboBox):
                    values[key] = widget.currentText()
                elif isinstance(widget, QCheckBox):
                    values[key] = widget.isChecked()
                elif isinstance(widget, QTextEdit):
                    values[key] = widget.toPlainText()
                elif isinstance(widget, QListWidget):
                    values[key] = [item.text() for item in widget.selectedItems()]
            return values
        except:
            return {}

    def update_values(self, key, args):
        if key in self.widgets:
            widget = self.widgets[key]
            if "value" in args:
                if isinstance(widget, QLineEdit):
                    widget.setText(str(args["value"]))
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(str(args["value"]))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(args["value"])
                elif isinstance(widget, QTextEdit):
                    widget.setPlainText(str(args["value"]))
                elif isinstance(widget, QListWidget):
                    widget.clear()
                    widget.addItems(args["values"])
            if "disabled" in args:
                widget.setEnabled(not args["disabled"])

    def browse_folder(self, input_widget):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder", input_widget.text())
        if directory:
            input_widget.setText(directory)

    def browse_file(self, input_widget):
        file = QFileDialog.getOpenFileName(self, "Select File", input_widget.text())[0]
        if file:
            input_widget.setText(file)

    def create_dev_status(self):
        layout = QGridLayout()
        dev_status_json = get_dev_status_js()
        row, col = 0, 0
        for each in dev_status_json.keys():
            dev_status_value = dev_status_json[each]
            lay = QHBoxLayout()
            if each == "Programming Language":
                combo = QComboBox()
                combo.addItems(dev_status_value)
                combo.setCurrentText(dev_status_value[0])
                combo.setObjectName("-DEV_STATUS_" + each + '-')
                combo.setFixedSize(90, 20)
                lay.addWidget(combo)
                input_v = QLineEdit("version")
                input_v.setObjectName("-VERSION_PY_" + each + "-")
                input_v.setFixedSize(40, 20)
                lay.addWidget(input_v)
            else:
                combo = QComboBox()
                combo.addItems(dev_status_value)
                combo.setCurrentText(dev_status_value[0])
                combo.setObjectName("-DEV_STATUS_" + each + '-')
                combo.setFixedSize(150, 20)
                lay.addWidget(combo)
            btn = QPushButton("+")
            btn.setObjectName("-DEV_STATUS_" + each + "_BUTTON-")
            lay.addWidget(btn)
            frame = QGroupBox(each)
            frame.setObjectName("-COLUMN_" + each + "-")
            frame.setLayout(lay)
            layout.addWidget(frame, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
        outer_frame = QGroupBox("Choose Dev Status")
        outer_frame.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidget(outer_frame)
        scroll.setWidgetResizable(True)
        scroll.setFixedSize(200, 200)
        return scroll

    def create_check_marks(self):
        file_associations = get_file_associations()
        check_list = file_associations.keys()
        layout = QGridLayout()
        row, col = 0, 0
        for i, each in enumerate(check_list):
            check = QCheckBox(file_associations[each]["file"])
            check.setChecked(True)
            check.setObjectName(each[:-1] + '_CHECK-')
            layout.addWidget(check, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1
        create_btn = QPushButton("Create Files")
        create_btn.setObjectName("Create Files")
        layout.addWidget(create_btn, row, 0)
        create_module_btn = QPushButton("Create Module")
        create_module_btn.setObjectName("-CREATE_FOLDER-")
        layout.addWidget(create_module_btn, row, 1)
        frame = QGroupBox("File Checklist")
        frame.setLayout(layout)
        return frame

    def create_inputs(self, string):
        lay = QHBoxLayout()
        lay.addWidget(QLabel(string + ':'))
        if string == "long_description":
            le = QLineEdit(os.getcwd())
            le.setObjectName(string)
            lay.addWidget(le)
            btn = QPushButton("Browse")
            btn.clicked.connect(lambda: self.browse_file(le))
            lay.addWidget(btn)
        elif string == "version":
            for j in range(4):
                le = QLineEdit("0")
                le.setObjectName(string + '_' + str(j))
                le.setFixedSize(20, 20)
                lay.addWidget(le)
                if j < 3:
                    lay.addWidget(QLabel('.'))
        elif string == "description":
            ml = QTextEdit()
            ml.setObjectName(string)
            lay.addWidget(ml)
        else:
            le = QLineEdit()
            le.setObjectName(string)
            le.setFixedSize(200, 20)
            lay.addWidget(le)
        widget = QWidget()
        widget.setLayout(lay)
        return widget

    def create_choice_tag_layout(self):
        lay = QVBoxLayout()
        choice_tags = get_all_choice_tags()
        for each in choice_tags:
            if each not in ["description", "long_description"]:
                lay.addWidget(self.create_inputs(each))
        frame = QGroupBox("Choice Tags")
        frame.setLayout(lay)
        return frame

    def get_descriptions_layout(self):
        lay = QVBoxLayout()
        description_list = ["description", "long_description"]
        for each in description_list:
            lay.addWidget(self.create_inputs(each))
        frame = QGroupBox("Descriptions")
        frame.setLayout(lay)
        return frame

    def get_module_folder_browser(self, initial_folder="/home/john-putkey/Documents/modules/abstract_audio"):
        frame_lay = QHBoxLayout()
        permenant = QLineEdit(initial_folder)
        permenant.setObjectName("-MODULE_PERMENANT_PATH-")
        frame_lay.addWidget(permenant)
        folder = QLineEdit(initial_folder)
        folder.setObjectName("-MODULE_FOLDER_PATH-")
        frame_lay.addWidget(folder)
        browse = QPushButton("Browse")
        browse.setObjectName("-MODULE_FOLDER_BROWSER-")
        frame_lay.addWidget(browse)
        check = QCheckBox("choose folder")
        check.setChecked(False)
        check.setObjectName("-LOCK_CHECKBOX-")
        frame_lay.addWidget(check)
        frame = QGroupBox("Choose Module Directory")
        frame.setLayout(frame_lay)
        return frame

    def new_layout(self, key, i):
        dev_status_json = get_dev_status_js()
        value = dev_status_json[key]
        lay = QHBoxLayout()
        combo = QComboBox()
        combo.setObjectName("-DEV_STATUS_" + key + str(i) + '-')
        combo.addItems(value)
        combo.setCurrentText(value[0])
        lay.addWidget(combo)
        if key == "Programming Language":
            input_v = QLineEdit("version")
            input_v.setObjectName("-VERSION_PY_" + key + str(i) + "-")
            lay.addWidget(input_v)
        widget = QWidget()
        widget.setLayout(lay)
        return widget

    def on_button_clicked(self):
        sender = self.sender()
        event = sender.objectName()
        values = self.get_values()
        if event == "-UPLOAD_MODULE-":
            upload_main(project_dir=values["-MODULE_PERMENANT_PATH-"])
        elif event == "Create Files":
            self.on_create_files()
        elif event == "-CREATE_FOLDER-":
            self.on_create_folder()
        elif event == "-MODULE_FOLDER_BROWSER-":
            self.browse_folder(self.widgets["-MODULE_FOLDER_PATH-"])
        elif "-DEV_STATUS_" in event and event.endswith("_BUTTON-"):
            key = event[len("-DEV_STATUS_") : -len("_BUTTON-")]
            self.on_add_dev_status(key)

    def on_create_files(self):
        values = self.get_values()
        args = {"readme_path": values["long_description"],
                'README.md': values["long_description"],
                "license": values["-DEV_STATUS_License-"],
                "package_name": values["package_name"],
                "version": values["version_0"] + '.' + values["version_1"] + '.' + values["version_2"] + '.' + values["version_3"],
                "author": values["author"],
                "author_email": values["author_email"],
                "description": values["description"],
                "url": values["url"],
                "classifiers": create_classifiers(),
                "install_requires": get_installed_versions(scan_folder_for_required_modules(values["-MODULE_PERMENANT_PATH-"], "src"))[0]}
        file_associations = get_file_associations()
        for each in file_associations.keys():
            if values[each[:-1] + '_CHECK-']:
                contents = get_fun({"args": args, "global": globals(), "name": file_associations[each]["function"]})
                if contents is not None:
                    file_path = os.path.join(values["-MODULE_PERMENANT_PATH-"], file_associations[each]["directory"], file_associations[each]["file"])
                    write_to_file(filepath=file_path, contents=contents)

    def on_create_folder(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("please choose a folder name and path")
        lay = QVBoxLayout()
        lay.addWidget(QLabel('Enter the new folder name:'))
        new_folder_name = QLineEdit()
        lay.addWidget(new_folder_name)
        lay.addWidget(QLabel('Select Parent Directory:'))
        parent_dir = QLineEdit(self.get_values()["-MODULE_PERMENANT_PATH-"])
        lay.addWidget(parent_dir)
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self.browse_folder(parent_dir))
        lay.addWidget(browse)
        buttons = QHBoxLayout()
        create = QPushButton("Create")
        cancel = QPushButton("Cancel")
        buttons.addWidget(create)
        buttons.addWidget(cancel)
        lay.addLayout(buttons)
        dialog.setLayout(lay)
        create.clicked.connect(dialog.accept)
        cancel.clicked.connect(dialog.reject)
        if dialog.exec() == QDialog.Accepted:
            values = {"-NEW_FOLDER_NAME-": new_folder_name.text(), "-PARENT_DIR-": parent_dir.text()}
            if values['-NEW_FOLDER_NAME-'] and values['-PARENT_DIR-']:
                folder_path = os.path.join(values['-PARENT_DIR-'], values['-NEW_FOLDER_NAME-'])
                os.makedirs(folder_path, exist_ok=True)
                self.update_values("-MODULE_FOLDER_PATH-", {"value": folder_path})
                self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(folder_path)})

    def on_add_dev_status(self, key):
        i = 0
        while "-DEV_STATUS_" + key + str(i) + '-' in self.widgets:
            i += 1
        new = self.new_layout(key, i)
        frame = self.widgets["-COLUMN_" + key + "-"]
        frame.layout().addWidget(new)
        for child in new.findChildren(QWidget):
            if child.objectName():
                self.widgets[child.objectName()] = child
                if isinstance(child, QComboBox):
                    child.currentIndexChanged.connect(self.on_combo_changed)
                # Add other connections if needed

    def on_checkbox_changed(self, state):
        sender = self.sender()
        event = sender.objectName()
        if event == "-LOCK_CHECKBOX-":
            values = self.get_values()
            if not values["-LOCK_CHECKBOX-"]:
                self.update_values("-MODULE_PERMENANT_PATH-", {"disabled": False})
                self.folder_bridge["MODULE_FOLDER"] = None
            else:
                self.update_values("-MODULE_PERMENANT_PATH-", {"value": values["-MODULE_FOLDER_PATH-"]})
                self.update_values("-MODULE_PERMENANT_PATH-", {"disabled": True})
                self.folder_bridge["MODULE_FOLDER"] = values["-MODULE_PERMENANT_PATH-"]
                check_all_files(self.folder_bridge["MODULE_FOLDER"])

    def on_input_changed(self):
        sender = self.sender()
        event = sender.objectName()
        if event == "-MODULE_FOLDER_PATH-":
            values = self.get_values()
            if os.path.exists(values["-MODULE_FOLDER_PATH-"]):
                self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(values["-MODULE_FOLDER_PATH-"])})
                folder = values["-MODULE_FOLDER_PATH-"]
                if folder:
                    self.update_values("-MODULE_FOLDER_PATH-", {"value": folder})
                    if not values["-LOCK_CHECKBOX-"]:
                        self.update_values("-MODULE_PERMENANT_PATH-", {"value": folder})

    def on_combo_changed(self, index):
        sender = self.sender()
        event = sender.objectName()
        # Add handling if needed for specific combos

    def on_directory_selected(self, item):
        values = self.get_values()
        chosen_folder = item.text()
        chosen_path = os.path.join(values["-MODULE_FOLDER_PATH-"], chosen_folder) if values["-MODULE_FOLDER_PATH-"] else None
        if chosen_path and os.path.isdir(chosen_path):
            self.update_values("-MODULE_FOLDER_PATH-", {"value": chosen_path})
            self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(chosen_path)})
            if not values["-LOCK_CHECKBOX-"]:
                self.update_values("-MODULE_PERMENANT_PATH-", {"value": chosen_path})
            self.folder_bridge["MODULE_FOLDER"] = chosen_path
        else:
            QMessageBox.warning(self, "warning", f"{chosen_folder} is not a directory.")

    def on_back(self):
        values = self.get_values()
        current_folder = values["-MODULE_FOLDER_PATH-"]
        parent_folder = os.path.dirname(current_folder) if current_folder else None
        if parent_folder:
            if self.folder_bridge["MODULE_FOLDER"] is not None:
                all_dirs = list_all_directories(self.folder_bridge["MODULE_FOLDER"])
                if parent_folder in all_dirs:
                    self.update_values("-MODULE_FOLDER_PATH-", {"value": parent_folder})
                    self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(parent_folder)})
            elif os.path.exists(parent_folder):
                self.update_values("-MODULE_FOLDER_PATH-", {"value": parent_folder})
                self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(parent_folder)})
                self.folder_bridge["MODULE_NAV_HISTORY"].append(current_folder)

    def on_forward(self):
        if self.folder_bridge["MODULE_NAV_HISTORY"]:
            next_folder = self.folder_bridge["MODULE_NAV_HISTORY"].pop()
            if self.folder_bridge["MODULE_FOLDER"] is not None:
                all_dirs = list_all_directories(self.folder_bridge["MODULE_FOLDER"])
                if next_folder in all_dirs:
                    self.update_values("-MODULE_FOLDER_PATH-", {"value": next_folder})
                    self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(next_folder)})
            elif os.path.exists(next_folder):
                self.update_values("-MODULE_FOLDER_PATH-", {"value": next_folder})
                self.update_values("-DIRECTORY_LIST-", {"values": os.listdir(next_folder)})

# The rest of the functions remain the same, as they do not involve GUI elements.

# To run the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
