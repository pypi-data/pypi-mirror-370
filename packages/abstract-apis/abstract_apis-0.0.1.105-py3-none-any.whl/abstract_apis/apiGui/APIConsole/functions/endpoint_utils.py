from ..imports import *
def fetch_remote_endpoints(self):
    try:
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
    except Exception as e:
        logger.info(f"**{__name__}** - fetch_remote_endpoints: {e}")


def on_endpoint_selected(self, row, col):
    try:
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
    except Exception as e:
        logger.info(f"**{__name__}** - on_endpoint_selected: {e}")
def _populate_endpoints(self, lst):
    try:
        self.endpoints_table.clearContents()
        self.endpoints_table.setRowCount(len(lst))
        for i, (path, methods) in enumerate(lst):
            self.endpoints_table.setItem(i, 0, QTableWidgetItem(path))
            self.endpoints_table.setItem(i, 1, QTableWidgetItem(methods))
    except Exception as e:
        logger.info(f"**{__name__}** - _populate_endpoints: {e}")
