import ast
from typing import List

from custom_otello_linter.helpers.get_full_func_name import get_full_func_name
from custom_otello_linter.types import FuncType


def get_make_screenshot_calls(step: FuncType) -> List[ast.Call]:
    """
    Проверяет наличие вызовов функции make_screenshot_for_comparison в шаге.
    Возвращает список узлов AST, соответствующих этим вызовам
    """
    make_screenshot_calls = []

    # Проходим через каждый элемент в теле функции (step.body)
    for stmt in step.body:
        # Применяем ast.walk к каждому выражению в теле функции
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                func_name = get_full_func_name(node.func)

                # Проверяем вызов функции make_screenshot_for_comparison
                if func_name.endswith('make_screenshot_for_comparison'):
                    make_screenshot_calls.append(node)

    return make_screenshot_calls
