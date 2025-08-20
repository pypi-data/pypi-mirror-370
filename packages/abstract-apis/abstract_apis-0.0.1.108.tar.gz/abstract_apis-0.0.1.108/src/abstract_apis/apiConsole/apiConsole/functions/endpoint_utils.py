from ..imports import *
def fetch_remote_endpoints(self,widgit,value,**kwargs):
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
def _populate_headers_table_rows(self):
    table = self.headers_table
    table.blockSignals(True)

    for i, (k, v,w) in enumerate(PREDEFINED_HEADERS):
        # Use (checkbox)
        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk.setCheckState(Qt.CheckState.Checked)
        table.setItem(i, 0, chk)

        # key
        table.setItem(i, 1, QTableWidgetItem(k))

        # value/modular widgets or literal Authorization value
        if k != "Authorization":
            value_cb = self._make_value_combo(i)  # your existing helper
            type_cb  = self._make_type_combo(i)   # your existing helper
            table.setCellWidget(i, 2, value_cb)
            table.setCellWidget(i, 3, type_cb)
            self._row_value_boxes[i] = value_cb
            self._row_type_boxes[i]  = type_cb
        else:
            table.setItem(i, 2, QTableWidgetItem(v))

    # blank row at the end (optional)
    last = len(PREDEFINED_HEADERS)
    empty_chk = QTableWidgetItem()
    empty_chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
    empty_chk.setCheckState(Qt.CheckState.Unchecked)
    table.setItem(last, 0, empty_chk)
    table.setItem(last, 1, QTableWidgetItem(""))
    table.setItem(last, 2, QTableWidgetItem(""))

    table.blockSignals(False)
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
        if chk_item and chk_item.checkState() == Qt.CheckState.Checked:
            continue
        key_item = self.headers_table.item(r, 1)
        key = key_item.text().strip() if key_item else ""
        val_item = self.headers_table.item(r, 2)
        if key and key in saved_headers:
            chk_item.setCheckState(Qt.CheckState.Checked)
            val = saved_headers[key]
            if self.headers_table.cellWidget(r, 2):
                self.headers_table.cellWidget(r, 2).setCurrentText(val)
            elif val_item:
                val_item.setText(val)
        else:
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            if self.headers_table.cellWidget(r, 2):
                self.headers_table.cellWidget(r, 2).setCurrentText("")
            elif val_item:
                val_item.setText("")

def methodComboInit(self,layout):
    # Method override selector
    method_row = QHBoxLayout()
    method_row.addWidget(QLabel("Override Method:"))
    self.method_box = QComboBox()
    self.method_box.addItems(["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    method_row.addWidget(self.method_box)
    layout.addLayout(method_row)
