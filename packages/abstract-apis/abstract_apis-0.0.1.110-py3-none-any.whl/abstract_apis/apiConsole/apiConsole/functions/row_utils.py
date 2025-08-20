from ..imports import *
def qt_full_type_name(obj):
    """Return the full module path + class name."""
    if obj is None:
        return "<None>"
    cls = type(obj)
    return f"{cls.__module__}.{cls.__name__}"
def getRowInputs(*args,**kwargs):
    types_js = {'widget':('PyQt6'), 'row':(int,str), 'col':(int,str)}
    found_types_js = {}
    for key,value in kwargs.items():
        typeKey = types_js.get(key)
        if typeKey and value and key not in found_types_js:
            found_types_js[key] = value
    found_args = []
    for i,arg in enumerate(list(args)):
        if i not in found_args:
            for key,types in types_js.items():
                if key not in found_types_js:
                    for typ in types:
                        if isinstance(typ,str):
                            if 'widget' in str(qt_full_type_name(arg)).lower():
                                found_types_js[key] = arg
                                found_args.append(i)
                                break
                        elif isinstance(arg,typ):
                            found_types_js[key] = arg
                            found_args.append(i)
                            break
                if i in found_args:
                    break
    for key,types in types_js.items():
        if key not in found_types_js:
            for i,arg in enumerate(list(args)):
                input(arg)
                if i not in found_args:
                    for typ in types:
                        if isinstance(typ,str):
                            if 'widget' in str(qt_full_type_name(arg)).lower():
                                found_types_js[key] = arg
                                found_args.append(i)
                                break
                        elif isinstance(arg,typ):
                            found_types_js[key] = arg
                            found_args.append(i)
                            break
                if i in found_args:
                    break
    widget,row,col = found_types_js.get('widget'),found_types_js.get('row'),found_types_js.get('col')
    return widget,row,col
def _maybe_add_header_row(self, *args,**kwargs):
    widget, row, col = getRowInputs(*args,**kwargs)
    widget = widget or self.headers_table
    last = widget.rowCount() - 1
    if row != last:
        return
    key_item = widget.item(row, 1)
    val_item = widget.item(row, 2)
    if (key_item and key_item.text().strip()) or (val_item and val_item.text().strip()):
        widget.blockSignals(True)
        widget.insertRow(last+1)
        chk = QTableWidgetItem()
        chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chk.setCheckState(Qt.CheckState.Unchecked)
        widget.setItem(last+1, 0, chk)
        widget.setItem(last+1, 1, QTableWidgetItem(""))
        widget.setItem(last+1, 2, QTableWidgetItem(""))
        widget.blockSignals(False)

def _maybe_add_body_row(self, *args,**kwargs):

    widget, row, col = getRowInputs(*args,**kwargs)
    widget = widget or self.headers_table

    last = widget.rowCount() - 1
    key_item = widget.item(row, 0)
    val_item = widget.item(row, 1)
    if row == last and ((key_item and key_item.text().strip()) or (val_item and val_item.text().strip())):
        widget.blockSignals(True)
        widget.insertRow(last+1)
        widget.setItem(last+1, 0, QTableWidgetItem(""))
        widget.setItem(last+1, 1, QTableWidgetItem(""))
        widget.blockSignals(False)
