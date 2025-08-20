import ast
from typing import List, Optional, Type

from custom_otello_linter.abstract_checkers import (
    ScenarioChecker,
    ScenarioHelper,
    StepsChecker
)
from custom_otello_linter.config import Config
from custom_otello_linter.types import FuncType
from custom_otello_linter.visitors._visitor_with_filename import (
    VisitorWithFilename
)


class Context:
    def __init__(self, steps: List[FuncType], scenario_node: ast.ClassDef,
                 import_from_nodes: List[ast.ImportFrom],
                 filename: str):
        self.steps = steps
        self.scenario_node = scenario_node
        self.import_from_nodes = import_from_nodes
        self.filename = filename


class ScenarioVisitor(VisitorWithFilename):
    scenarios_checkers: List[ScenarioChecker] = []
    steps_checkers: List[StepsChecker] = []
    import_from_nodes: List[ast.ImportFrom] = []

    def __init__(self, config: Optional[Config] = None,
                 filename: Optional[str] = None) -> None:
        super().__init__(config, filename)
        self.import_from_nodes = []

    @property
    def config(self):
        return self._config

    @classmethod
    def register_steps_checker(cls, checker: Type[StepsChecker]):
        cls.steps_checkers.append(checker())
        return checker

    @classmethod
    def register_scenario_checker(cls, checker: Type[ScenarioChecker]):
        cls.scenarios_checkers.append(checker())
        return checker

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """
        Save all imports from scenario (for validation ImportedInterfaceInWrongStep)
        """
        self.import_from_nodes.append(node)

    @classmethod
    def deregister_all(cls):
        cls.steps_checkers = []
        cls.scenarios_checkers = []

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name == 'Scenario':
            context = Context(steps=ScenarioHelper().get_all_steps(node),
                              scenario_node=node,
                              import_from_nodes=self.import_from_nodes,
                              filename=self.filename)
            try:
                for checker in self.steps_checkers:
                    self.errors.extend(checker.check_steps(context, self.config))
                for checker in self.scenarios_checkers:
                    self.errors.extend(checker.check_scenario(context, self.config))
            except Exception as e:
                print(f'Linter failed: checking {context.filename} with {checker.__class__}.\n'
                      f'Exception: {e}')
