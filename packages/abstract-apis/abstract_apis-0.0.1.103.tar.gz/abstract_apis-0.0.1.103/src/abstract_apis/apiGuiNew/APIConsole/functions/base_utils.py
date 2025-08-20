from ..imports import *
from ...imports.constants import _norm_prefix
def _on_base_changed(self,widget, *args):
    
    pref = get_combo_value(widget) # whatever you stored as userData
    if isinstance(pref, str) and pref.strip():
        self.api_prefix_in.setText(_norm_prefix(pref))
    else:
        # fall back if no userData
        self.api_prefix_in.setText(_norm_prefix("/api"))

def _on_base_text_edited(self, text: str):
    # Only react if the user typed (i.e., not selecting an item).
    # If the current index matches an item, _on_base_changed already ran.
    idx = self.base_combo.currentIndex()
    if idx == -1: # free-typed URL
        # choose behavior: keep user’s current prefix, or reset to default
        if not self.api_prefix_in.text().strip():
            self.api_prefix_in.setText(_norm_prefix("/api"))
        # else: leave as-is
