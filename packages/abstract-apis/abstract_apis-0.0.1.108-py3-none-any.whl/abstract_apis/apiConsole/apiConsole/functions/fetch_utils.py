from ..imports import *

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

def detect_api_prefix(self,widgit,value,**kwargs):
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
    self.api_prefix = (found or get_combo_value(self.base_combo,base) or "/api")
    if not self.api_prefix.startswith('/'):
        self.api_prefix = f"/{self.api_prefix}"
    self.api_prefix_in.setText(self.api_prefix)
    logging.info(f"API prefix set to: {self.api_prefix}")
