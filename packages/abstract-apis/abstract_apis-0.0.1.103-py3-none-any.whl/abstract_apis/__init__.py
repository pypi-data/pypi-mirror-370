from .make_request import *
from .async_make_request import *
from apiGuiNew import startGui,APIConsole
def get_api_gui():
    from .apiGuiNew import run_abstract_api_gui
    startGui()
