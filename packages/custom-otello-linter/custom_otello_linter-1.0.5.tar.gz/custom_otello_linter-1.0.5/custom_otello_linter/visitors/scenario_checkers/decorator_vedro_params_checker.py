import ast
from typing import List

from flake8_plugin_utils import Error

from custom_otello_linter.abstract_checkers import ScenarioChecker
from custom_otello_linter.errors import DecoratorVedroParams
from custom_otello_linter.visitors.scenario_visitor import (
    Context,
    ScenarioVisitor
)


@ScenarioVisitor.register_scenario_checker
class VedroParamsChecker(ScenarioChecker):

    def check_scenario(self, context: Context, *args) -> List[Error]:
        # Проходим по всем шагам в контексте
        for step in context.steps:
            # Проходим по списку декораторов каждого шага
            for decorator in step.decorator_list:
                # Проверка вызова функции vedro.params (если декоратор вида vedro.params())
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                    if (
                        isinstance(decorator.func.value, ast.Name)
                        and decorator.func.value.id == 'vedro'
                        and decorator.func.attr == 'params'
                    ):
                        # Если найден vedro.params, возвращаем ошибку
                        return [DecoratorVedroParams(decorator.lineno, decorator.col_offset)]

                # Проверка вызова params, если он импортирован напрямую (например, @params())
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'params':
                        # Проверка, что params импортирован из vedro
                        for import_from in context.import_from_nodes:
                            if import_from.module == 'vedro':
                                for name in import_from.names:
                                    if name.name == 'params':
                                        # Если найден params, возвращаем ошибку
                                        return [DecoratorVedroParams(decorator.lineno, decorator.col_offset)]

        return []
