from ..imports import *
def _on_request_success(self, txt):
    try:
        if not self.append_chk.isChecked():
            self.response_output.clear()
        self.response_output.moveCursor(QTextCursor.MoveOperation.End)
        self.response_output.insertPlainText(f"✔ {self._current_method} {self._current_url}\n{txt}\n")
        logging.info(f"✔ {self._current_method} {self._current_url}")
    except Exception:
        logging.exception("Error handling success slot")
    finally:
        self.send_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._active_thread = None
        self._active_worker = None

def _on_request_failure(self, err):
    try:
        if not self.append_chk.isChecked():
            self.response_output.clear()
        self.response_output.moveCursor(QTextCursor.MoveOperation.End)
        self.response_output.insertPlainText(err + "\n")
        logging.error(err)
    except Exception:
        logging.exception("Error handling failure slot")
    finally:
        self.send_button.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._active_thread = None
        self._active_worker = None


def send_request(self,*args,**kwargs):
    print([args,kwargs])
    try:
        sel = self.endpoints_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, "No endpoint", "Please select an endpoint.")
            return
        try:

            ep = self.endpoints_table.item(sel[0].row(), 0).text()
            base = self.base_combo.currentText().rstrip('/')
            url = base + ep
            method = self.method_box.currentText()
            headers = self._collect_headers()
            params = self._collect_table_data(self.body_table)
            # remember per-endpoint config
            self.config_cache[ep] = {'headers': headers, 'params': params, 'method': method}
            logging.info(f"➡ {method} {url} | headers={headers} | params={params}")
            # status line; keep previous response visible
            self.response_output.moveCursor(QTextCursor.MoveOperation.End)
            self.response_output.insertPlainText(f"\n⏳ {method} {url} …\n")
            # spin up background worker
            self.send_button.setEnabled(False)
            QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
            thread = QThread(self)
            worker = RequestWorker(method, url, headers, params)
            worker.moveToThread(thread)
            # store for slots
            self._current_method = method
            self._current_url = url
            # wiring
            thread.started.connect(worker.run)
            worker.success.connect(self._on_request_success)
            worker.failure.connect(self._on_request_failure)
            worker.success.connect(thread.quit)
            worker.failure.connect(thread.quit)
            thread.finished.connect(worker.deleteLater)
            thread.finished.connect(lambda: (
                self.send_button.setEnabled(True),
                QApplication.restoreOverrideCursor()
            ))
            # keep refs so GC doesn’t kill them mid-flight
            self._active_thread = thread
            self._active_worker = worker
            thread.start()
        except Exception as e:
            logging.info(f"{e}")
    except Exception as e:
            logging.info(f"{e}")

