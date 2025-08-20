
from ..imports import *
from .functions import (_build_ui, _collect_headers, _collect_table_data, _fetch_label, _make_type_combo, _make_value_combo, _maybe_add_body_row, _maybe_add_header_row, _mime_values_for_category, _normalized_prefix, _on_api_prefix_changed, _on_base_changed, _on_base_text_edited, _on_request_failure, _on_request_success, _populate_headers_table_rows, _on_type_changed, _populate_endpoints, _setup_logging, detect_api_prefix, fetch_remote_endpoints, logWidgetInit, methodComboInit, on_endpoint_selected, send_request)

def initFuncs(self):
    try:
        for f in (_build_ui, _collect_headers, _collect_table_data, _fetch_label, _make_type_combo, _make_value_combo, _maybe_add_body_row, _maybe_add_header_row, _mime_values_for_category, _normalized_prefix, _on_api_prefix_changed, _on_base_changed, _on_base_text_edited, _on_request_failure, _on_request_success, _populate_headers_table_rows, _on_type_changed, _populate_endpoints, _setup_logging, detect_api_prefix, fetch_remote_endpoints, logWidgetInit, methodComboInit, on_endpoint_selected, send_request):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
