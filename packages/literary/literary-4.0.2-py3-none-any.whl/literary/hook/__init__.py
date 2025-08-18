""""""
import sys
import traceback
from .finder import extend_file_finder, install_ipykernel_restrictor

def noop_loader(fullname, path):
    return None

def notebook_loader_factory(fullname, path):
    try:
        get_loader = notebook_loader_factory.get_loader
    except AttributeError:
        notebook_loader_factory.get_loader = noop_loader
        from .importer import get_loader
        notebook_loader_factory.get_loader = get_loader
    return get_loader(fullname, path)

def install_import_hook(set_except_hook=True, restrict_ipykernel_path=True):
    if restrict_ipykernel_path:
        install_ipykernel_restrictor()
    extend_file_finder((notebook_loader_factory, ['.ipynb']))
    if set_except_hook:
        sys.excepthook = traceback.print_exception