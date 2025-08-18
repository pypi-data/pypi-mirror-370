""""""
from nbconvert.preprocessors import Preprocessor
from traitlets import Set, Unicode

class TagAllowListPreprocessor(Preprocessor):
    allow_cell_tags = Set(Unicode(), default_value={'export', 'docstring'})

    def check_cell_conditions(self, cell, resources: dict, index: int) -> bool:
        tags = cell.metadata.get('tags', [])
        return bool(self.allow_cell_tags.intersection(tags))

    def preprocess(self, nb, resources: dict):
        nb.cells = [self.preprocess_cell(cell, resources, i)[0] for i, cell in enumerate(nb.cells) if self.check_cell_conditions(cell, resources, i)]
        return (nb, resources)

    def preprocess_cell(self, cell, resources: dict, index: int):
        return (cell, resources)