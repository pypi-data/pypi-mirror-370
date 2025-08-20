def emit(self, record):
    msg = self.format(record)
    self.widget.append(msg)
    self.widget.ensureCursorVisible()
