from ..imports import *
def _collect_table_data(self, table):
    try:
        data = {}
        for r in range(table.rowCount()):
            key_item = table.item(r, 0)
            if not key_item or not key_item.text().strip():
                continue
            val_item = table.item(r, 1)
            data[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return data
    except Exception as e:
        logger.info(f"**{__name__}** - _collect_table_data: {e}")


def _collect_headers(self):
    try:
        headers = {}
        for r in range(self.headers_table.rowCount()):
            chk = self.headers_table.item(r, 0)
            if not chk or chk.checkState() != Qt.Checked:
                continue
            key_item = self.headers_table.item(r, 1)
            val_item = self.headers_table.item(r, 2)
            if key_item and key_item.text().strip():
                headers[key_item.text().strip()] = val_item.text().strip() if val_item else ""
        return headers
    except Exception as e:
        logger.info(f"**{__name__}** - _collect_headers: {e}")

