"""# Notebook Finder
"""
import os
import sys
from importlib.machinery import FileFinder, PathFinder
from inspect import getclosurevars

def extend_file_finder(*loader_details):
    """Inject a set of loaders into a list of path hooks

    :param path_hooks: list of path hooks
    :param loader_details: FileFinder loader details
    :return:
    """
    for i, hook in enumerate(sys.path_hooks):
        try:
            namespace = getclosurevars(hook)
        except TypeError as err:
            continue
        try:
            details = namespace.nonlocals['loader_details']
        except KeyError as err:
            continue
        break
    else:
        raise ValueError
    sys.path_hooks[i] = FileFinder.path_hook(*details, *loader_details)
    sys.path_importer_cache.clear()

class IPyKernelPathRestrictor:
    ...

    @classmethod
    def remove_cwd_from_sys_path(cls):
        cwd = os.path.realpath(os.getcwd())
        sys.path = [p for p in sys.path if os.path.realpath(p) != cwd]

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        if '.' in fullname:
            return None
        name = fullname.split('.', 1)[0]
        if name == 'ipykernel':
            cls.remove_cwd_from_sys_path()
        return None

def install_ipykernel_restrictor():
    for i, finder in enumerate(sys.meta_path):
        if finder is PathFinder:
            break
    else:
        return
    sys.meta_path.insert(i, IPyKernelPathRestrictor)