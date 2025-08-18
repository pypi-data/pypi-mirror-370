""""""
import typing as tp
from functools import lru_cache
from pathlib import Path
from traitlets.config import Config, ConfigFileNotFound, JSONFileConfigLoader, PyFileConfigLoader
CONFIG_FILE_STEM = 'literary_config'

@lru_cache()
def find_literary_config(path) -> Path:
    """Load the configuration for the current Literary project.

    :return:
    """
    for p in path.glob(f'{CONFIG_FILE_STEM}.*'):
        return p
    if path.parents:
        return find_literary_config(path.parent)
    raise FileNotFoundError("Couldn't find config file")

@lru_cache()
def load_literary_config(path: Path) -> Config:
    """Load a project configuration file

    :param path: configuration file path
    :return:
    """
    for loader_cls in (JSONFileConfigLoader, PyFileConfigLoader):
        loader = loader_cls(path.name, str(path.parent))
        try:
            return loader.load_config()
        except ConfigFileNotFound:
            continue
    raise ValueError(f'{path!r} was not a recognised config file')