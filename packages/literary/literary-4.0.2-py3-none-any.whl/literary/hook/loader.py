"""# Notebook Loader
"""
import linecache
from importlib.machinery import SourcelessFileLoader
import nbformat

class NotebookLoader(SourcelessFileLoader):
    """Sourceless Jupyter Notebook loader"""

    def __init__(self, fullname: str, path: str, exporter):
        super().__init__(fullname, path)
        self._exporter = exporter

    def _update_linecache(self, path: str, source: str):
        linecache.cache[path] = (len(source), None, source.splitlines(keepends=True), path)

    def get_code(self, fullname: str):
        path = self.get_filename(fullname)
        body = self.get_transpiled_source(path)
        self._update_linecache(path, body)
        return compile(body, path, 'exec')

    def get_transpiled_source(self, path: str):
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        body, resources = self._exporter.from_notebook_node(nb)
        return body