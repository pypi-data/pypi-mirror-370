import ast
from typing import List

from custom_otello_linter.abstract_checkers import StepsChecker
from custom_otello_linter.errors import MissingPlatformArgError
from custom_otello_linter.helpers.get_init_step import get_init_step, is_platform_param_present
from custom_otello_linter.visitors import ScenarioVisitor, Context
from flake8_plugin_utils import Error


@ScenarioVisitor.register_steps_checker
class PlatformParamsChecker(StepsChecker):

    def check_steps(self, context: Context, *args) -> List[Error]:
        if (init_step := get_init_step(context)) is None:
            return []

        if not is_platform_param_present(init_step):
            return []

        for step in context.steps:
            # Проверяем, что шаг начинается с 'given' или 'when'
            if step.name.startswith('given') or step.name.startswith('when'):
                # Среди действий в шаге ищем присвоение с await методом, например:
                # self.page = await opened_dashboard()
                for element in ast.walk(step):
                    if (
                            isinstance(element, ast.Assign)
                            and isinstance(element.value, ast.Await)
                            and isinstance(element.value.value, ast.Call)
                            and isinstance(element.value.value.func, ast.Name)
                            and element.value.value.func.id.startswith('opened')
                    ):
                        # Проверяем, что в теле шага есть вызов функции с keyword параметром platform
                        for kw_arg in element.value.value.keywords:
                            if kw_arg.arg == 'platform':
                                return []
                        # Если не нашли keyword = platform, проверяем наличие позиционного аргумента
                        for param in ast.walk(element.value):
                            # Ищем атрибут без вложенности, только self.platform
                            if isinstance(param, ast.Attribute) and isinstance(param.value, ast.Name):
                                if param.value.id == 'self' and param.attr == 'platform':
                                    return []
                        # Если не нашли вызов функции с параметром platform, возвращаем ошибку
                        col_offset = element.value.value.func.col_offset
                        return [MissingPlatformArgError(lineno=element.lineno, col_offset=col_offset)]

        return []
