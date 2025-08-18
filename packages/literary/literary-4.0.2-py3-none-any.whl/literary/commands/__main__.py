"""# Commandline Application
"""
import sys
from traitlets import default
from traitlets.config import Application
from .build import LiteraryBuildApp
from .test import LiteraryTestApp

class LiteraryLauncher(Application):
    description = 'Work with literate notebooks'
    subcommands = {'build': (LiteraryBuildApp, 'Build a package from a series of notebooks'), 'test': (LiteraryTestApp, 'Run a series of notebook tests')}

    def start(self):
        """Perform the App's actions as configured"""
        super().start()
        if self.subapp is None:
            sub_commands = ', '.join(sorted(self.subcommands))
            sys.exit('Please supply at least one subcommand: {}'.format(sub_commands))
launch_new_instance = LiteraryLauncher.launch_instance
if __name__ == '__main__' and (not LiteraryLauncher.initialized()):
    launch_new_instance()