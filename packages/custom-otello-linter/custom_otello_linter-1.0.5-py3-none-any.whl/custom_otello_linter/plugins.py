import argparse
import ast
from typing import Callable, List, Optional

from flake8.options.manager import OptionManager
from flake8_plugin_utils import Plugin, Visitor

from custom_otello_linter.visitors import ScenarioVisitor

from .config import Config


def str_to_bool(string):
    return string.lower() in ('true', 'yes', 't', '1')


class PluginWithFilename(Plugin):
    def __init__(self, tree: ast.AST, filename: str, *args, **kwargs):
        super().__init__(tree)
        self.filename = filename

    def run(self):
        for visitor_cls in self.visitors:
            visitor = self._create_visitor(visitor_cls, filename=self.filename)
            visitor.visit(self._tree)
            for error in visitor.errors:
                yield self._error(error)

    @classmethod
    def _create_visitor(cls, visitor_cls: Callable, filename: Optional[str] = None) -> Visitor:
        if cls.config is None:
            return visitor_cls(filename=filename)
        return visitor_cls(config=cls.config, filename=filename)


class OtelloQAStylePlugin(PluginWithFilename):
    name = 'custom_otello_linter'
    version = '1.0.5'
    visitors = [
        ScenarioVisitor,
    ]

    def __init__(self, tree: ast.AST, filename: str, *args, **kwargs):
        super().__init__(tree, filename)

    @classmethod
    def add_options(cls, option_manager: OptionManager):
        pass

    @classmethod
    def parse_options_to_config(
        cls, option_manager: OptionManager, options: argparse.Namespace, args: List[str]
    ) -> Config:
        return Config()
