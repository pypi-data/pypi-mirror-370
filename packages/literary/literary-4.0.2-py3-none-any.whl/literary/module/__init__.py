"""# Notebook Modules

Just providing importable notebook modules does not address the full scope of package development. When developing a package, we often want to perform relative imports `from . import x`. This requires that a `__package__` global is set to the name of the current package. Additionally, literary provides tools to make it easier to write literate documents e.g. `patch` which need to be exposed to the end user.
"""
import sys
import warnings
from pathlib import Path
from traitlets import Enum
from traitlets.config import Configurable
from ..config import find_literary_config, load_literary_config
from ..transpile.patch import patch

class NotebookExtension(Configurable):
    package_name_strategy = Enum(['shortest', 'first'], default_value='shortest', help='strategy for resolving package name').tag(config=True)

    def determine_package_name(self, path: Path) -> str:
        """Determine the corresponding importable name for a package directory given by
    a particular file path. Return `None` if path is not contained within `sys.path`.

    :param path: path to package
    :return:
    """
        if not path.is_dir():
            raise ValueError('Expected directory, not file path')
        candidates = []
        for p in sys.path:
            if str(path) == p:
                continue
            try:
                relative_path = path.relative_to(p)
            except ValueError:
                continue
            candidates.append(relative_path)
        if not candidates:
            return
        if self.package_name_strategy == 'shortest':
            best_candidate = min(candidates, key=lambda x: len(x.parts))
        else:
            best_candidate = candidates[0]
        return '.'.join(best_candidate.parts)

def load_ipython_extension(ipython):
    """Build the package-aware namespace for the IPython kernel. 

    If the kernel working directory is located under `sys.path`, 
    the appropriate `__package__` global will be set.

    Additionally, helper utilities like `patch` are installed.

    :param ipython: IPython shell instance
    """
    cwd = Path.cwd()
    config = load_literary_config(find_literary_config(cwd))
    notebook_extension = NotebookExtension(config=config)
    package = notebook_extension.determine_package_name(cwd)
    if package is None:
        warnings.warn(f"Couldn't determine the package name for the current working directory {cwd}. This might be because the current project has not been installed in editable mode.")
        sys.path.append(str(cwd))
    else:
        sys.path = [p for p in sys.path if Path(p).resolve() != cwd]
    ipython.user_ns.update({'__package__': package, 'patch': patch})