from __future__ import annotations
import enum
from ..imports import *
import inspect
import PyQt6
from PyQt6 import QtWidgets,QtCore
import inspect


def _build_ui(self):
        layout = QVBoxLayout(self)
        # build UI
        combo = createCombo(
            self,
            label="Base URL:",
            items=PREDEFINED_BASE_URLS,         # e.g. [("http://a", "/api"), ...]
            attr_name="base_combo",
            connect=self._on_base_changed,                 # can also be {'callbacks': on_changed, 'signals': ['currentTextChanged']}
            insertPolicy="NoInsert",
            editable=True
        )
        layout.addWidget(combo)
        # API Prefix
        api_row = make_input_row(
            self,
            QLineEdit,
            label="API Prefix:",
            default_value="/api",
            attr_name="api_prefix_in",
            connect=self._on_api_prefix_changed
        )

        createButton(api_row,
                   widget_cls=QPushButton,
                   label="Detect",
                   connect=self.detect_api_prefix
                   )
        layout.addLayout(api_row)   # ← add ONCE only
        #self.base_combo.currentIndexChanged.connect(self._on_base_changed)

        # Fetch remote endpoints button (label now dynamic)

        createButton(self,
               layout=layout,
               widget_cls=QPushButton,
               label=self._fetch_label(),
               attr_name='fetch_button',
               connect={"callbacks":self.fetch_remote_endpoints,"signals":"clicked"}
               )
        
 
        # Endpoints table


        # Method override selector
        
        createTable(
            self,
            label="Endpoints (select one row):",
            args=[0, 2],
            headers_config={
                    "Endpoint Path":{"horizontalHeader":'ResizeToContents',"ColumnWidth":200},
                    "Methods":{"horizontalHeader":'Interactive',"ColumnWidth":200}
                    },
         
            layout=layout,
            attr_name="endpoints_table",
            # sizing to match your code
            connect={"callbacks": self.on_endpoint_selected,
                     "signals": "cellClicked",
                     "prepend_widget": True},
            setMinimumHeight=420,
            setSelectionBehavior=(QAbstractItemView.SelectionBehavior.SelectRows),
            stretch_last_section=True,
        )
        self.methodComboInit(layout)
        # 4 columns: Use | Key | Value | Modular
        # 2) Headers table (4 columns: Use | Key | Value | Modular)
        rows = len(PREDEFINED_HEADERS) + 1  # +1 blank row
        # seed basic 2 columns; we will insert widgets/checkboxes afterward
        seed = [[ "", "", "", "" ] for _ in range(rows)]
        createTable(
            self,
            headers_config={
                    "Use":{"horizontalHeader":'ResizeToContents',"ColumnWidth":200},
                    "Key":{"horizontalHeader":'Interactive',"ColumnWidth":200},
                    "Value":{"horizontalHeader":'Interactive',"ColumnWidth":200},
                    "Modular":{"horizontalHeader":'Interactive',"ColumnWidth":200}
                    },
            data=seed,
            layout=layout,
            attr_name="headers_table",
            # sizing to match your code
            connect={"callbacks": self._maybe_add_header_row,
                     "signals": "cellChanged",
                     "prepend_widget": True},
            setMinimumHeight=1000,
            alternatingRowColors=True,
            stretch_last_section=False,
        )
        # keep references to row widgets
        self._row_type_boxes = {}
        self._row_value_boxes = {}
        
        # Fill rows
        self._populate_headers_table_rows()
        # add a blank row at the end (optional)
        # blank row
        empty_chk = QTableWidgetItem()
        empty_chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        empty_chk.setCheckState(Qt.CheckState.Unchecked)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 0, empty_chk)
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 1, QTableWidgetItem(""))
        self.headers_table.setItem(len(PREDEFINED_HEADERS), 2, QTableWidgetItem(""))
        self.headers_table.cellChanged.connect(self._maybe_add_header_row)
        # Body / Query-Params table

        createTable(
            self,
            layout=layout,
            label="Body / Query-Params (key → value):",

            headers_config={
                    "Key":{"horizontalHeader":'Interactive',"ColumnWidth":200},
                    "Value":{"horizontalHeader":'Interactive',"ColumnWidth":200},
                    },
            data=[["", ""]],  # initial blank row
            attr_name="body_table",
            setMinimumHeight=400,
            connect={"callbacks": self._maybe_add_body_row,
                     "signals": ["cellChanged"],
                     "prepend_widget": True},
            setSizePolicy = (QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        )
        # initial blank row
        self.body_table.setItem(0, 0, QTableWidgetItem(""))
        self.body_table.setItem(0, 1, QTableWidgetItem(""))
        self.body_table.cellChanged.connect(self._maybe_add_body_row)
        
        # Send button
        createButton(self,
               layout=layout,
               widget_cls=QPushButton,
               label="▶ Send Request",
               attr_name='send_button',
               connect={"callbacks":self.send_request,"signals":"clicked"}
               )
        
        # Response

        createComponent(
            parent=self,
            layout=layout,
            widget_cls=QTextEdit,
            label="Response:",
            attr_name="response_output",
            setReadOnly=True,
            setMinimumHeight=120,        # handled by apply_properties
            setSizePolicy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        )
##        # Append Response
##        # Append Response (mirrors your working code)
##        createCheckBox(
##            parent=self,
##            layout=layout,
##            widget_cls=QCheckBox,
##            label="Append responses",
##            attr_name="append_chk",
##            setChecked=True,        # handled by apply_properties
##        )
##
##        # Logs toggle + area
##        toggle_row = QHBoxLayout()
##
##        createButton(
##            parent=self,                     # IMPORTANT: parent is self, not the layout
##            layout=toggle_row,
##            widget_cls=QPushButton,
##            label="Show Logs",
##            attr_name="toggle_logs",
##            setCheckable=True,
##            setChecked=False,
##            connect={
##                "signals": "toggled",        # your connect_signals should resolve 'toggled'
##                "callbacks": lambda on: (
##                    self.log_output.setVisible(on),
##                    self.toggle_logs.setText("Hide Logs" if on else "Show Logs")
##                ),
##            },
##        )
##        toggle_row.addStretch()
##        layout.addLayout(toggle_row)
##
##
##
##        createComponent(
##            parent=self,
##            layout=layout,
##            widget_cls=QTextEdit,
##            label="Logs:",
##            attr_name="log_output",
##            setReadOnly=True,
##            setMinimumHeight=80,        # handled by apply_properties
##            setVisible=False,
##            setSizePolicy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
##        )
        createCheckBox(
            parent=self,
            layout=layout,
            widget_cls=QCheckBox,
            label="Append responses",
            attr_name="append_chk",
            setChecked=True,        # handled by apply_properties
        )
        # Logs toggle + area
        toggle_row = QHBoxLayout()
        self.toggle_logs = QPushButton("Show Logs")
        self.toggle_logs.setCheckable(True)
        self.toggle_logs.setChecked(False)
        self.toggle_logs.toggled.connect(lambda on: (
            self.log_output.setVisible(on),
            self.toggle_logs.setText("Hide Logs" if on else "Show Logs")
        ))
        toggle_row.addWidget(self.toggle_logs)
        toggle_row.addStretch()
        layout.addLayout(toggle_row)


        createComponent(
            parent=self,
            layout=layout,
            widget_cls=QTextEdit,
            label="Logs:",
            attr_name="log_output",
            setReadOnly=True,
            setMinimumHeight=300,        # handled by apply_properties
            setVisible=True,
            setSizePolicy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        )

        # after you add everything to layout in order, assign stretch:
        # 0..N refer to widgets/layouts in the order you added them
        layout.setStretch(layout.indexOf(self.endpoints_table), 2)
        layout.setStretch(layout.indexOf(self.headers_table),   3)
        layout.setStretch(layout.indexOf(self.body_table),      2)
        layout.setStretch(layout.indexOf(self.response_output), 3)
        layout.setStretch(layout.indexOf(self.log_output),      1)

        # make the light “form” rows not stretch
        layout.setStretch(layout.indexOf(combo),      0)
        layout.setStretch(layout.indexOf(self.fetch_button),    0)
