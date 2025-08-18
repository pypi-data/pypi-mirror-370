"""# Notebook Modules

Just providing importable notebook modules does not address the full scope of package development. When developing a package, we often want to perform relative imports `from . import x`. This requires that a `__package__` global is set to the name of the current package. Additionally, literary provides tools to make it easier to write literate documents e.g. `patch` which need to be exposed to the end user.
"""
import sys
from pathlib import Path
from ..config import find_literary_config, load_literary_config
from ..transpile.patch import patch

def load_ipython_extension(ipython):
    """Build the namespace for the IPython kernel. 

    Exposes helper utilities like `patc.h`.

    :param ipython: IPython shell instance
    """
    cwd = Path.cwd()
    config = load_literary_config(find_literary_config(cwd))
    sys.path.append(str(cwd))
    ipython.user_ns.update({'patch': patch})