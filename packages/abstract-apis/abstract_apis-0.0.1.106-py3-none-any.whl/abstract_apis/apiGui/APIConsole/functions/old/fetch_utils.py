from ..imports import *
def _on_fetch_response(self, txt: str, log_msg: str):
    try:
        data = json.loads(txt)
        self._populate_endpoints(data)
        logging.info(log_msg)
    except Exception as e:
        logger.info(f"**{__name__}** - _on_fetch_response: {e}")

def _on_fetch_error(self, err: str):
    try:
        logging.error(err)
        QMessageBox.warning(self, "Fetch Error", err)
    except Exception as e:
        logger.info(f"**{__name__}** - _on_fetch_error: {e}")

def _fetch_label(self) -> str:
    try:
        p = self.api_prefix.strip() or "/api"
        if not p.startswith("/"):
            p = "/" + p
        return f"Fetch {p}/endpoints"
    except Exception as e:
        logger.info(f"**{__name__}** - _fetch_label: {e}")
