"""# Import Hook
"""
from functools import lru_cache
from pathlib import Path
from nbconvert import Exporter
from traitlets import Instance, Type, default
from traitlets.config import Configurable
from ..config import find_literary_config, load_literary_config
from ..transpile.exporter import LiteraryExporter
from .loader import NotebookLoader

class NotebookImporter(Configurable):
    exporter = Instance(Exporter)
    exporter_class = Type(LiteraryExporter, help='exporter class used for module source generation').tag(config=True)

    @default('exporter')
    def _exporter_default(self):
        return self.exporter_class(parent=self)

    def get_loader(self, fullname, path):
        exporter = self.exporter_class(parent=self)
        return NotebookLoader(fullname, path, exporter=self.exporter)

def get_loader(fullname, path):
    try:
        config_path = find_literary_config(Path(path))
    except FileNotFoundError:
        return None
    importer = NotebookImporter(config=load_literary_config(config_path))
    return importer.get_loader(fullname, path)