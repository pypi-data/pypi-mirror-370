from ..imports import *
from ...RequestThread.main import requestThread

def send_request(self):
    try:
        sel = self.endpoints_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, "No endpoint", "Please select an endpoint.")
            return
        ep = self.endpoints_table.item(sel[0].row(), 0).text()
        base = self.base_combo.currentText().rstrip('/')
        url = base + ep
        method  = self.method_box.currentText()
        headers = self._collect_headers()
        params  = self._collect_table_data(self.body_table)

        self.config_cache[ep] = {'headers': headers, 'params': params, 'method': method}
        logging.info(f"➡ {method} {url} | headers={headers} | params={params}")

        self.response_output.clear()
        self.send_button.setEnabled(False)

        # keep a reference so the thread isn't GC'd
        self._thread = requestThread(method, url, headers, params, timeout=12)
        self._thread.response_signal.connect(self._on_send_response)
        self._thread.error_signal.connect(self._on_send_error)
        self._thread.finished.connect(lambda: self.send_button.setEnabled(True))
        self._thread.start()
    except Exception as e:
        logger.info(f"**{__name__}** - send_request: {e}")

def _on_send_response(self, txt: str, log_msg: str):
    try:
        self.response_output.setPlainText(txt)
        logging.info(log_msg)
    finally:
        self._thread = None

def _on_send_error(self, err: str):
    try:
        self.response_output.setPlainText(err)
        logging.error(err)
    finally:
        self._thread = None
