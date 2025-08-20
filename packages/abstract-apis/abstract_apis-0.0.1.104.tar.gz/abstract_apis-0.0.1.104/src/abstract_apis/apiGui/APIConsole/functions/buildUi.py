from ..imports import *
from PyQt5.QtWidgets import QLineEdit
def _build_ui(self):
    
    try:
        layout = QVBoxLayout(self)
        # Base URL selection (existing)
        layout.addWidget(QLabel("Base URL:"))
        self.base_combo = QComboBox()
        self.base_combo.setEditable(True)
        self.base_combo.addItems(PREDEFINED_BASE_URLS)
        self.base_combo.setInsertPolicy(QComboBox.NoInsert)
        layout.addWidget(self.base_combo)
    except Exception as e:
        logger.info(f"**_build_ui** - Base URL selection (existing): {e}")
    try:
        # NEW: API Prefix
        api_row = QHBoxLayout()
        api_row.addWidget(QLabel("API Prefix:"))
        
        self.api_prefix_in = QLineEdit(self.api_prefix)
        self.api_prefix_in.setPlaceholderText("/api")
        self.api_prefix_in.setClearButtonEnabled(True)
        self.api_prefix_in.textChanged.connect(self._on_api_prefix_changed)
        api_row.addWidget(self.api_prefix_in)
    except Exception as e:
        logger.info(f"**_build_ui** - NEW: API Prefix: {e}")
    try:
        detect_btn = QPushButton("Detect")
        detect_btn.clicked.connect(self.detect_api_prefix)
        api_row.addWidget(detect_btn)
        layout.addLayout(api_row)
    except Exception as e:
        logger.info(f"**_build_ui** - Detect: {e}")
    try:
        # Fetch remote endpoints button (label now dynamic)
        self.fetch_button = QPushButton(self._fetch_label())
        layout.addWidget(self.fetch_button)
        self.fetch_button.clicked.connect(self.fetch_remote_endpoints)
    except Exception as e:
        logger.info(f"**_build_ui** - Fetch remote endpoints button (label now dynamic): {e}")
    try:
        # Endpoints table
        layout.addWidget(QLabel("Endpoints (select one row):"))
        self.endpoints_table = QTableWidget(0, 2)
        self.endpoints_table.setHorizontalHeaderLabels(["Endpoint Path", "Methods"])
        self.endpoints_table.horizontalHeader().setStretchLastSection(True)
        self.endpoints_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.endpoints_table.setFixedHeight(200)
        layout.addWidget(self.endpoints_table)
        self.endpoints_table.cellClicked.connect(self.on_endpoint_selected)
    except Exception as e:
        logger.info(f"**_build_ui** - Endpoints table: {e}")
    try:
        # Method override selector
        row = QHBoxLayout()
        row.addWidget(QLabel("Override Method:"))
        self.method_box = QComboBox()
        self.method_box.addItems(["GET", "POST"])
        row.addWidget(self.method_box)
        layout.addLayout(row)
    except Exception as e:
        logger.info(f"**_build_ui** - Method override selector: {e}")
    try:
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
    except Exception as e:
        logger.info(f"**_build_ui** - Headers table: {e}")
    try:
        # blank row
        empty_chk = QTableWidgetItem()
        empty_chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        empty_chk.setCheckState(Qt.Unchecked)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 0, empty_chk)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 1, QTableWidgetItem(""))
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 2, QTableWidgetItem(""))
        self.headers_table.cellChanged.connect(self._maybe_add_header_row)
    except Exception as e:
        logger.info(f"**_build_ui** - blank row: {e}")
    try:
        # Body / Query-Params table
        layout.addWidget(QLabel("Body / Query-Params (key → value):"))
        self.body_table = QTableWidget(1, 2)
        self.body_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.body_table.setFixedHeight(200)
        layout.addWidget(self.body_table)
    except Exception as e:
        logger.info(f"**_build_ui** - Body / Query-Params table: {e}")
    try:
        # initial blank row
        self.body_table.setItem(0, 0, QTableWidgetItem(""))
        self.body_table.setItem(0, 1, QTableWidgetItem(""))
        self.body_table.cellChanged.connect(self._maybe_add_body_row)
    except Exception as e:
        logger.info(f"**_build_ui** - initial blank row: {e}")
    try:
        # Send button
        self.send_button = QPushButton("▶ Send Request")
        layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_request)
    except Exception as e:
        logger.info(f"**_build_ui** - Send button: {e}")
    try:
        # Response
        layout.addWidget(QLabel("Response:"))
        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setFixedHeight(200)
        layout.addWidget(self.response_output)
    except Exception as e:
        logger.info(f"**_build_ui** - Response: {e}")
    try:
        # Logs
        layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(150)
        layout.addWidget(self.log_output)
    except Exception as e:
        logger.info(f"**_build_ui** - Logs: {e}")
