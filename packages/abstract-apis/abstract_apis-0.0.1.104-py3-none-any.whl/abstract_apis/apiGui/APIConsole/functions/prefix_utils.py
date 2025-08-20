from ..imports import *
import requests

def _normalized_prefix(self) -> str:
    p = self.api_prefix_in.text().strip() or "/api"
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/")

def detect_api_prefix(self):
    """Try to pull static_url_path from a small config endpoint."""
    base = self.base_combo.currentText().rstrip("/")
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

def _fetch_label(self) -> str:
    p = (self.api_prefix or "/api").strip()
    if not p.startswith("/"):
        p = "/" + p
    return f"Fetch {p}/endpoints"

def _on_api_prefix_changed(self, _txt: str):
    try:
        self.api_prefix = self._normalized_prefix()              # ← fixed
        self.fetch_button.setText(self._fetch_label())           # ← fixed
    except Exception as e:
        logger.info(f"**{__name__}** - _on_api_prefix_changed: {e}")
