from .imports import QComboBox,QSizePolicy,Qt,QListView
from .initFuncs import initFuncs

# ─── Logging Handler ──────────────────────────────────────────────────────
class BoundedCombo(QComboBox):
    def __init__(self, parent=None, *, editable=False):
        super().__init__(parent)
        self.setEditable(editable)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(0)
        # ⬇⬇⬇ fix is here
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        lv = QListView(self)
        lv.setTextElideMode(Qt.TextElideMode.ElideRight)
        lv.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setView(lv)
BoundedCombo = initFuncs(BoundedCombo)
