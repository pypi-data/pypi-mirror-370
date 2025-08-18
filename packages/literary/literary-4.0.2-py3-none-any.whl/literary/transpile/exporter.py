"""# Exporter
"""
import ast
import sys
from nbconvert.exporters import PythonExporter
from traitlets import List, default, import_item
from traitlets.config import Config
from .filter import escape_triple_quotes
from .preprocessor import TagAllowListPreprocessor

class LiteraryExporter(PythonExporter):

    def __init__(self, *args, **kwargs):
        """
        Public constructor

        Parameters
        ----------
        config : ``traitlets.config.Config``
            User configuration instance.
        `**kw`
            Additional keyword arguments passed to parent __init__

        """
        super().__init__(*args, **kwargs)
        self._init_transformers()
    transformers = List(default_value=['literary.transpile.syntax.PatchTransformer', 'literary.transpile.syntax.IPythonTransformer']).tag(config=True)

    def _init_transformers(self):
        self._transformers = []
        for value in self.transformers:
            if isinstance(value, str):
                value = import_item(value)
            self._transformers.append(value(parent=self.parent))

    @default('template_name')
    def _template_name_default(self):
        return 'literary'

    @default('default_preprocessors')
    def _default_preprocessors_default(self):
        return [TagAllowListPreprocessor]

    @default('exclude_input_prompt')
    def _exclude_input_prompt_default(self):
        return True

    @property
    def default_config(self):
        c = Config({'TagAllowListPreprocessor': {'enabled': True}})
        c.merge(super().default_config)
        return c

    def default_filters(self):
        yield from super().default_filters()
        yield ('escape_triple_quotes', escape_triple_quotes)

    def from_notebook_node(self, nb, resources=None, **kwargs):
        body, resources = super().from_notebook_node(nb, resources, **kwargs)
        node = ast.parse(body)
        try:
            for transformer in self._transformers:
                node = transformer.visit(node)
        except Exception as err:
            raise RuntimeError(f'An error occurred during AST transforming: {body}') from err
        return (ast.unparse(node), resources)