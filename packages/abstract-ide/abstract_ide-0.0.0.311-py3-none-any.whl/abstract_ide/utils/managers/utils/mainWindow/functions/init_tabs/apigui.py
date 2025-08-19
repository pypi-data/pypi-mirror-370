#!/usr/bin/env python3
# temp_py.py — GUI front-end for abstract_apis with dynamic endpoints, headers & params

import sys
import json
import logging,requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QMessageBox,
    QTableWidget, QSizePolicy, QTableWidgetItem, QAbstractItemView, QCheckBox
)
from PyQt5.QtCore import Qt
from abstract_apis import getRequest, postRequest
from typing import Optional

# ─── Configuration ──────────────────────────────────────────────────────
PREDEFINED_BASE_URLS = [
    "https://abstractendeavors.com",
    "https://clownworld.biz",
    "https://typicallyoutliers.com",
    "https://thedailydialectics.com",
]
PREDEFINED_HEADERS = [
    ("Content-Type", "application/json"),
    ("Accept", "application/json"),
    ("Authorization", "Bearer "),
]

# ─── Logging Handler ──────────────────────────────────────────────────────
class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        self.api_prefix = "/api"   # default; will update on detect or user edit
    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.ensureCursorVisible()

# ─── Main GUI ─────────────────────────────────────────────────────────────
class APIConsole(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Console for abstract_apis")
        self.api_prefix = "/api"   # default; will update on detect or user edit
        self.resize(800, 900)
        self.config_cache = {}  # cache per-endpoint settings
        self._build_ui()
        self._setup_logging()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Base URL selection (existing)
        layout.addWidget(QLabel("Base URL:"))
        self.base_combo = QComboBox()
        self.base_combo.setEditable(True)
        self.base_combo.addItems(PREDEFINED_BASE_URLS)
        self.base_combo.setInsertPolicy(QComboBox.NoInsert)
        layout.addWidget(self.base_combo)

        # NEW: API Prefix
        api_row = QHBoxLayout()
        api_row.addWidget(QLabel("API Prefix:"))
        from PyQt5.QtWidgets import QLineEdit
        self.api_prefix_in = QLineEdit(self.api_prefix)
        self.api_prefix_in.setPlaceholderText("/api")
        self.api_prefix_in.setClearButtonEnabled(True)
        self.api_prefix_in.textChanged.connect(self._on_api_prefix_changed)
        api_row.addWidget(self.api_prefix_in)

        detect_btn = QPushButton("Detect")
        detect_btn.clicked.connect(self.detect_api_prefix)
        api_row.addWidget(detect_btn)
        layout.addLayout(api_row)

        # Fetch remote endpoints button (label now dynamic)
        self.fetch_button = QPushButton(self._fetch_label())
        layout.addWidget(self.fetch_button)
        self.fetch_button.clicked.connect(self.fetch_remote_endpoints)

        # Endpoints table
        layout.addWidget(QLabel("Endpoints (select one row):"))
        self.endpoints_table = QTableWidget(0, 2)
        self.endpoints_table.setHorizontalHeaderLabels(["Endpoint Path", "Methods"])
        self.endpoints_table.horizontalHeader().setStretchLastSection(True)
        self.endpoints_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.endpoints_table.setFixedHeight(200)
        layout.addWidget(self.endpoints_table)
        self.endpoints_table.cellClicked.connect(self.on_endpoint_selected)

        # Method override selector
        row = QHBoxLayout()
        row.addWidget(QLabel("Override Method:"))
        self.method_box = QComboBox()
        self.method_box.addItems(["GET", "POST"])
        row.addWidget(self.method_box)
        layout.addLayout(row)

        # Headers table
        layout.addWidget(QLabel("Headers (check to include):"))
        self.headers_table = QTableWidget(len(PREDEFINED_HEADERS)+1, 3)
        self.headers_table.setHorizontalHeaderLabels(["Use", "Key", "Value"])
        self.headers_table.setFixedHeight(200)
        layout.addWidget(self.headers_table)
        for i, (k, v) in enumerate(PREDEFINED_HEADERS):
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Checked)
            self.headers_table.setItem(i, 0, chk)
            self.headers_table.setItem(i, 1, QTableWidgetItem(k))
            self.headers_table.setItem(i, 2, QTableWidgetItem(v))
        # blank row
        empty_chk = QTableWidgetItem()
        empty_chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        empty_chk.setCheckState(Qt.Unchecked)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 0, empty_chk)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 1, QTableWidgetItem(""))
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 2, QTableWidgetItem(""))
        self.headers_table.cellChanged.connect(self._maybe_add_header_row)

        # Body / Query-Params table
        layout.addWidget(QLabel("Body / Query-Params (key → value):"))
        self.body_table = QTableWidget(1, 2)
        self.body_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.body_table.setFixedHeight(200)
        layout.addWidget(self.body_table)
        # initial blank row
        self.body_table.setItem(0, 0, QTableWidgetItem(""))
        self.body_table.setItem(0, 1, QTableWidgetItem(""))
        self.body_table.cellChanged.connect(self._maybe_add_body_row)

        # Send button
        self.send_button = QPushButton("▶ Send Request")
        layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_request)

        # Response
        layout.addWidget(QLabel("Response:"))
        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setFixedHeight(200)
        layout.addWidget(self.response_output)

        # Logs
        layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(150)
        layout.addWidget(self.log_output)
    def _fetch_label(self) -> str:
        p = self.api_prefix.strip() or "/api"
        if not p.startswith("/"):
            p = "/" + p
        return f"Fetch {p}/endpoints"

    def _normalized_prefix(self) -> str:
        p = self.api_prefix_in.text().strip() or "/api"
        if not p.startswith("/"):
            p = "/" + p
        return p.rstrip("/")

    def _on_api_prefix_changed(self, _txt: str):
        self.api_prefix = self._normalized_prefix()
        self.fetch_button.setText(self._fetch_label())

    def detect_api_prefix(self):
        """Try to pull static_url_path from a small config endpoint.
           Expected JSON: {"static_url_path": "/api"}"""
        base = self.base_combo.currentText().rstrip("/")
        # Try a couple of likely config endpoints; add/adjust to your server
        candidates = [f"{base}/config", f"{base}/__config", f"{base}/_meta"]
        found: Optional[str] = None
        for url in candidates:
            try:
                r = requests.get(url, timeout=3)
                if r.ok:
                    j = r.json()
                    val = j.get("static_url_path") or j.get("api_prefix")
                    if isinstance(val, str) and val.strip():
                        found = val.strip()
                        break
            except Exception:
                continue

        self.api_prefix = (found or "/api")
        self.api_prefix_in.setText(self.api_prefix)
        logging.info(f"API prefix set to: {self.api_prefix}")
    def fetch_remote_endpoints(self):
        base = self.base_combo.currentText().rstrip('/')
        prefix = self._normalized_prefix()
        url = f"{base}{prefix}/endpoints"
        self.log_output.clear()
        logging.info(f"Fetching remote endpoints from {url}")
        try:
            data = getRequest(url=url)
            if isinstance(data, list):
                self._populate_endpoints(data)
                logging.info("✔ Remote endpoints loaded")
            else:
                logging.warning(f"{prefix}/endpoints returned non-list, ignoring")
        except Exception as e:
            logging.error(f"Failed to fetch endpoints: {e}")
            QMessageBox.warning(self, "Fetch Error", str(e))


    def _populate_endpoints(self, lst):
        self.endpoints_table.clearContents()
        self.endpoints_table.setRowCount(len(lst))
        for i, (path, methods) in enumerate(lst):
            self.endpoints_table.setItem(i, 0, QTableWidgetItem(path))
            self.endpoints_table.setItem(i, 1, QTableWidgetItem(methods))

    def on_endpoint_selected(self, row, col):
        ep = self.endpoints_table.item(row, 0).text()
        cfg = self.config_cache.get(ep, {})

        # restore override method
        if 'method' in cfg:
            self.method_box.setCurrentText(cfg['method'])

        # restore headers, but only for UNCHECKED rows
        saved_headers = cfg.get('headers', {})
        for r in range(self.headers_table.rowCount()):
            chk_item = self.headers_table.item(r, 0)
            key_item = self.headers_table.item(r, 1)
            val_item = self.headers_table.item(r, 2)

            # if this row is checked, leave key/value as-is (sticky)
            if chk_item and chk_item.checkState() == Qt.Checked:
                continue

            # otherwise pull from this endpoint’s saved headers, or clear
            if key_item:
                key = key_item.text().strip()
                if key and key in saved_headers:
                    chk_item.setCheckState(Qt.Checked)
                    val_item.setText(saved_headers[key])
                else:
                    chk_item.setCheckState(Qt.Unchecked)
                    val_item.setText("")

    def _maybe_add_header_row(self, row, col):
        last = self.headers_table.rowCount() - 1
        if row != last:
            return
        key_item = self.headers_table.item(row, 1)
        val_item = self.headers_table.item(row, 2)
        if (key_item and key_item.text().strip()) or (val_item and val_item.text().strip()):
            self.headers_table.blockSignals(True)
            self.headers_table.insertRow(last+1)
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Unchecked)
            self.headers_table.setItem(last+1, 0, chk)
            self.headers_table.setItem(last+1, 1, QTableWidgetItem(""))
            self.headers_table.setItem(last+1, 2, QTableWidgetItem(""))
            self.headers_table.blockSignals(False)

    def _maybe_add_body_row(self, row, col):
        last = self.body_table.rowCount() - 1
        key_item = self.body_table.item(row, 0)
        val_item = self.body_table.item(row, 1)
        if row == last and ((key_item and key_item.text().strip()) or (val_item and val_item.text().strip())):
            self.body_table.blockSignals(True)
            self.body_table.insertRow(last+1)
            self.body_table.setItem(last+1, 0, QTableWidgetItem(""))
            self.body_table.setItem(last+1, 1, QTableWidgetItem(""))
            self.body_table.blockSignals(False)

    def _setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = QTextEditLogger(self.log_output)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s','%H:%M:%S'))
        logger.addHandler(handler)

    def _collect_table_data(self, table):
        data = {}
        for r in range(table.rowCount()):
            key_item = table.item(r, 0)
            if not key_item or not key_item.text().strip():
                continue
            val_item = table.item(r, 1)
            data[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return data

    def _collect_headers(self):
        headers = {}
        for r in range(self.headers_table.rowCount()):
            chk = self.headers_table.item(r, 0)
            if not chk or chk.checkState() != Qt.Checked:
                continue
            key_item = self.headers_table.item(r, 1)
            val_item = self.headers_table.item(r, 2)
            if key_item and key_item.text().strip():
                headers[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return headers

    def send_request(self):
        sel = self.endpoints_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, "No endpoint", "Please select an endpoint.")
            return
        ep = self.endpoints_table.item(sel[0].row(), 0).text()
        base = self.base_combo.currentText().rstrip('/')
        url = base + ep
        method = self.method_box.currentText()
        headers = self._collect_headers()
        params = self._collect_table_data(self.body_table)
        self.config_cache[ep] = {'headers': headers, 'params': params, 'method': method}
        logging.info(f"➡ {method} {url} | headers={headers} | params={params}")
        self.response_output.clear()
        try:
            if method == "GET":
                res = getRequest(url=url, headers=headers, data=params)
            else:
                res = postRequest(url=url, headers=headers, data=params)
            txt = json.dumps(res, indent=4) if isinstance(res, dict) else str(res)
            self.response_output.setPlainText(txt)
            logging.info("✔ Response displayed")
        except Exception as ex:
            err = f"✖ Error: {ex}"
            self.response_output.setPlainText(err)
            logging.error(err)
