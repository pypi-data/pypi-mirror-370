"""# Package Generation
"""
import shutil
from pathlib import Path
import nbformat
from nbconvert import Exporter
from traitlets import Bool, Instance, List, Type, Unicode, default
from traitlets.config import Config, Configurable
from ..transpile.exporter import LiteraryExporter
from .app import LiteraryApp
DEFAULT_IGNORE_PATTERNS = ('.ipynb_checkpoints', '__pycache__', '.*')

class LiteraryBuildApp(LiteraryApp):
    """Project operator which builds a Literary package from a set of notebook directories."""
    description = 'Build a pure-Python package from a set of Jupyter notebooks'
    exporter = Instance(Exporter)
    exporter_class = Type(LiteraryExporter).tag(config=True)
    generated_dir = Unicode('lib', help='Path to generated packages top-level directory').tag(config=True)
    ignore_patterns = List(Unicode(), help='List of patterns to ignore from source tree').tag(config=True)
    clear_generated = Bool(False, help='Clear generated directory before building, otherwise raise an Exception if non-empty.').tag(config=True)
    aliases = {**LiteraryApp.aliases, 'ignore': 'LiteraryBuildApp.ignore_patterns', 'output': 'LiteraryBuildApp.generated_dir', 'packages': 'LiteraryBuildApp.packages_dir'}
    flags = {'clear': ({'LiteraryBuildApp': {'clear_generated': True}}, 'Clear generated directory before building.')}

    @default('exporter')
    def _exporter_default(self):
        return self.exporter_class(parent=self, config=self.config)

    @property
    def generated_path(self) -> Path:
        return self.resolve_path(self.generated_dir)

    @default('ignore_patterns')
    def _ignore_patterns_default(self):
        return list(DEFAULT_IGNORE_PATTERNS)

    def _build_package_component(self, source_dir_path: Path, dest_dir_path: Path):
        """Recursively build a pure-Python package from a source tree

    :param source_dir_path: path to current source directory
    :param dest_dir_path: path to current destination directory
    :return:
    """
        dest_dir_path.mkdir(parents=True, exist_ok=True)
        for path in source_dir_path.iterdir():
            if any((path.match(p) for p in self.ignore_patterns)):
                continue
            if path == self.generated_dir:
                continue
            relative_path = path.relative_to(source_dir_path)
            mirror_path = dest_dir_path / relative_path
            if path.match('*.ipynb'):
                source, _ = self.exporter.from_notebook_node(nbformat.read(path, as_version=nbformat.NO_CONVERT))
                mirror_path.with_suffix('.py').write_text(source)
            elif path.is_dir():
                self._build_package_component(path, mirror_path)
            else:
                mirror_path.write_bytes(path.read_bytes())

    def _build_packages(self):
        """Build the packages contained in `packages_path`."""
        self._build_package_component(self.packages_path, self.generated_path)

    def _clear_generated_path(self):
        """Clear the contents of `generated_path`."""
        for p in self.generated_path.iterdir():
            if not self.clear_generated:
                raise ValueError('Generated directory is not empty, and `clear_generated` is not set.')
            if p.is_file():
                p.unlink()
            else:
                shutil.rmtree(p)

    def start(self):
        """Build a pure-Python package from a literary source tree."""
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self._clear_generated_path()
        if not self.packages_path.exists():
            raise FileNotFoundError(f'Source path {self.packages_path!r} does not exist')
        self._build_packages()