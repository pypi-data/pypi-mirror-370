"""# Testing
"""
import logging
import typing as tp
from concurrent import futures
from operator import methodcaller
from pathlib import Path
import nbclient
import nbformat
from traitlets import Bool, Int, List, Type, Unicode, default
from .app import LiteraryApp
DEFAULT_IGNORE_PATTERNS = ('.ipynb_checkpoints', '__pycache__', '.*')

class LiteraryTestApp(LiteraryApp):
    """Test the current project notebooks, with various failure strategies."""
    client_class = Type(nbclient.NotebookClient, help='Class for the notebook client').tag(config=True)
    extra_sources = List(Unicode(), help='List of paths to extra sources to be tested').tag(config=True)

    @property
    def extra_paths(self) -> tp.List[Path]:
        return [self.resolve_path(p) for p in self.extra_sources]
    fail_fast = Bool(default_value=True, help='Fail as soon as one client fails').tag(config=True)
    ignore_patterns = List(Unicode(), help='List of patterns to ignore from sources').tag(config=True)

    @default('ignore_patterns')
    def _ignore_patterns_default(self):
        return list(DEFAULT_IGNORE_PATTERNS)
    jobs = Int(allow_none=True, default_value=None, help='number of parallel jobs to run').tag(config=True)
    aliases = {**LiteraryApp.aliases, 'jobs': 'LiteraryTestApp.jobs'}
    flags = {'fail-fast': ({'LiteraryTestApp': {'fail_fast': True}}, 'Stop for first failing test.')}

    def _execute_notebook(self, path: Path):
        """Execute the notebook with the given path.

    :param path: path to notebook
    """
        nb = nbformat.read(path, as_version=nbformat.NO_CONVERT)
        client = self.client_class(nb, resources={'metadata': {'path': path.parent}}, parent=self)
        return client.execute()

    def _find_notebooks(self, dir_path: Path):
        """Find notebooks given by a particular path.

    If the path is a directory, yield from the result of calling find_notebooks` with
    the directory path.
    If the path is a notebook file path, yield the path directly

    :param path: path to a file or directory
    :param ignore_patterns: set of patterns to ignore during recursion
    :return:
    """
        for path in dir_path.iterdir():
            if any((path.match(p) for p in self.ignore_patterns)):
                continue
            if path.is_dir():
                yield from self._find_notebooks(path)
            elif path.match('*.ipynb'):
                yield path

    def _visit_and_flatten_paths(self, paths: tp.Iterable[str]):
        """Flatten an iterable of directory and file paths into file paths.
    Directories will be visited and any notebook paths that are not ignored will be yielded.

    :param paths: iterable of paths
    """
        for p in paths:
            if p.is_dir():
                yield from self._find_notebooks(p)
            else:
                yield p

    def start(self):
        """Run the tracked notebooks in a process pool."""
        sources = [Path(p) for p in [self.packages_path] + self.extra_paths]
        paths = [*self._visit_and_flatten_paths(sources)]
        paths.sort()
        return_when = futures.FIRST_EXCEPTION if self.fail_fast else futures.ALL_COMPLETED
        with futures.ProcessPoolExecutor(max_workers=self.jobs) as executor:
            tasks = [executor.submit(self._execute_notebook, p) for p in paths]
            done, not_done = futures.wait(tasks, return_when=return_when)
            for path, task in zip(paths, done):
                task.result()
                self.log.info(f'{path} executed successfully')