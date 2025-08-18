"""# Literary Application
"""
from copy import deepcopy
from importlib import import_module
from inspect import getmembers
from pathlib import Path
from traitlets import List, Unicode, default, observe, validate
from traitlets.config import Application, Configurable, catch_config_error
from ..config import find_literary_config, load_literary_config
from .trait import Path as PathTrait

class LiteraryApp(Application):
    name = 'literary'
    description = 'A Literary application'
    aliases = {**Application.aliases, 'config-file': 'LiteraryApp.config_file'}
    config_file = PathTrait(help='Literary project configuration file').tag(config=True)
    project_path = PathTrait(help='Path to Literary project top-level directory').tag(config=True)
    packages_dir = Unicode('src', help='Path to Literary packages top-level directory').tag(config=True)
    classes = List()

    @default('classes')
    def _classes_default(self):
        modules = [import_module(f'..transpile.{n}', __package__) for n in ('exporter', 'preprocessor', 'syntax')]
        return [cls for m in modules for _, cls in getmembers(m) if isinstance(cls, type) and issubclass(cls, Configurable)]

    @catch_config_error
    def initialize(self, argv=None):
        self.parse_command_line(argv)
        argv_config = deepcopy(self.config)
        self.load_app_config_file()
        self.update_config(argv_config)

    def load_app_config_file(self):
        config = load_literary_config(self.config_file)
        self.update_config(config)

    @default('config_file')
    def _config_file_default(self):
        return find_literary_config(Path.cwd())

    @default('project_path')
    def _project_path_default(self):
        return self.config_file.parent

    def resolve_path(self, path):
        return self.project_path / path

    @property
    def packages_path(self) -> Path:
        return self.resolve_path(self.packages_dir)