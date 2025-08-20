import sys
import json
import logging,requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QMessageBox,
    QTableWidget, QSizePolicy, QTableWidgetItem, QAbstractItemView, QCheckBox
)
from abstract_utilities import get_logFile
from PyQt5.QtCore import Qt
from abstract_apis import getRequest, postRequest
from typing import Optional
PREDEFINED_BASE_URLS = [
    "https://abstractendeavors.com",
    "https://clownworld.biz",
    "https://typicallyoutliers.com",
    "https://thedailydialectics.com",
]
PREDEFINED_HEADERS = [
    ("Content-Type", "application/json"),
    ("Accept", "application/json"),
    ("Authorization", "Bearer "),
]
logger = get_logFile(__name__)
