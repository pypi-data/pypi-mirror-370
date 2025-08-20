from ..imports import *
def _setup_logging(self):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = QTextEditLogger(self.log_output)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s','%H:%M:%S'))
    logger.addHandler(handler)


def logWidgetInit(self,
                  layout,
                  label=None,
                  readOnly=True,
                  minHeight=None,
                  maxHeight=None,
                  Expanding=(True,True),
                  setVisible=False
                  ):
    label = label or "Logs:"
    addLabel(layout,label)
    self.log_output = getOutput(
          label=label,
          readOnly=readOnly,
          minHeight=minHeight,
          maxHeight=maxHeight,
          Expanding=Expanding,
          setVisible=setVisible
        )
    layout.addWidget(self.log_output)
