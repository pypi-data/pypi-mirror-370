""""""
import pathlib
import traitlets

class Path(traitlets.TraitType):
    """A pathlib.Path trait class"""

    def validate(self, obj, value):
        try:
            return pathlib.Path(value)
        except TypeError:
            self.error(obj, value)