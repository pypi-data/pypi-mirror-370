from ..imports import *
def _setup_logging(self):
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = QTextEditLogger(self.log_output)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s','%H:%M:%S'))
        logger.addHandler(handler)

    except Exception as e:
        logger.info(f"**{__name__}** - _setup_logging: {e}")
