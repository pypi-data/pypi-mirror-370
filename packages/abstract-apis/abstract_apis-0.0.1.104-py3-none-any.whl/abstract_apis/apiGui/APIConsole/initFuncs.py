from ..QTextEditLogger import QTextEditLogger
from ..imports import *
from .functions import (_build_ui, _collect_headers, _collect_table_data, _fetch_label, _maybe_add_body_row, _maybe_add_header_row, _normalized_prefix, _on_api_prefix_changed, _on_send_error, _on_send_response, _populate_endpoints, _probe_session, _setup_logging, canonicalize_slash, clean_text, detect_api_prefix, fetch_remote_endpoints, fix_file, main, on_endpoint_selected, sanitize_bytes, send_request)

def initFuncs(self):
    try:
        for f in (_build_ui, _collect_headers, _collect_table_data, _fetch_label, _maybe_add_body_row, _maybe_add_header_row, _normalized_prefix, _on_api_prefix_changed, _on_send_error, _on_send_response, _populate_endpoints, _probe_session, _setup_logging, canonicalize_slash, clean_text, detect_api_prefix, fetch_remote_endpoints, fix_file, main, on_endpoint_selected, sanitize_bytes, send_request):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
