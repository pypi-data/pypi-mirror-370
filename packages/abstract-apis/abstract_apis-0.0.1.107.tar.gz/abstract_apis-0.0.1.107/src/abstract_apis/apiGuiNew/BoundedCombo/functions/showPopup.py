from ..imports import QComboBox
def showPopup(self):
    QComboBox.showPopup(self)
    v = self.view()
    v.setMinimumWidth(self.width())
    v.setMaximumWidth(self.width())
