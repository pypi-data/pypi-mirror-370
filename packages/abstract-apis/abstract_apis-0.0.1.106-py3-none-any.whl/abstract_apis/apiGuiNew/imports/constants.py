from abstract_utilities.type_utils import MIME_TYPES
# ─── Configuration ──────────────────────────────────────────────────────
PREDEFINED_BASE_URLS = [
    ("https://abstractendeavors.com",'api'),
    ("https://clownworld.biz",'media'),
    ("https://typicallyoutliers.com",'api'),
    ("https://thedailydialectics.com",'api'),
]
def _norm_prefix(p: str) -> str:
    p = (p or "/api").strip()
    if not p.startswith("/"):
        p = "/" + p
    return p.rstrip("/")
PREDEFINED_HEADERS = [
    ("Content-Type", "application/json","document"),
    ("Accept", "application/json","document"),
    ("Authorization", "Bearer ",""),
]
MIME_TYPES_HEADERS = MIME_TYPES
