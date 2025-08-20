from ..imports import *

def detect_api_prefix(self):
    """
    Initiates a request to detect the API prefix by probing configuration endpoints.
    Uses a separate thread to avoid blocking the GUI.
    """
    try:
        base = self.base_combo.currentText().rstrip("/")
        logging.debug(f"Starting API prefix detection for base URL: {base}")
        thread = requestThread("GET", base, {}, {}, is_detect=True)
        thread.response_signal.connect(self._on_detect_response)
        thread.error_signal.connect(self._on_detect_error)
        thread.start()
    except Exception as e:
        logger.exception(f"Error in detect_api_prefix: {e}")

def _on_detect_response(self, found: str, log_msg: str):
    """
    Handles successful API prefix detection response.
    
    Args:
        found (str): Detected API prefix or default "/api".
        log_msg (str): Log message to display.
    """
    try:
        self.api_prefix = found or "/api"
        self.api_prefix_in.setText(self.api_prefix)
        logging.info(log_msg)
    except Exception as e:
        logger.exception(f"Error in _on_detect_response: {e}")

def _on_detect_error(self, err: str):
    """
    Handles errors during API prefix detection.
    
    Args:
        err (str): Error message to display.
    """
    try:
        logging.error(err)
        QMessageBox.warning(self, "Detect Error", f"Failed to detect API prefix: {err}")
        self.api_prefix = "/api"
        self.api_prefix_in.setText(self.api_prefix)
    except Exception as e:
        logger.exception(f"Error in _on_detect_error: {e}")
