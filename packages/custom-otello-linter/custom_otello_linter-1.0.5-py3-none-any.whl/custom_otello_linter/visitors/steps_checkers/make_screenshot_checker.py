from typing import List

from flake8_plugin_utils import Error

from custom_otello_linter.abstract_checkers import StepsChecker
from custom_otello_linter.errors import MultipleScreenshotsError
from custom_otello_linter.helpers.get_make_screenshot_calls import (
    get_make_screenshot_calls
)
from custom_otello_linter.visitors.scenario_visitor import (
    Context,
    ScenarioVisitor
)


@ScenarioVisitor.register_steps_checker
class MakeScreenshotChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []

        # Проверяем каждый шаг в сценарии
        for step in context.steps:
            if (
                    step.name.startswith('then')
                    or step.name.startswith('and')
                    or step.name.startswith('but')
            ):
                screenshot_calls = get_make_screenshot_calls(step)

                # Если вызовов функции больше одного, добавляем ошибку
                if len(screenshot_calls) > 1:
                    for screenshot_call in screenshot_calls[1:]:  # Начинаем со второго вызова
                        errors.append(MultipleScreenshotsError(
                            lineno=screenshot_call.lineno,
                            col_offset=screenshot_call.col_offset,
                            step_name=step.name))

        # Возвращаем собранные ошибки после завершения всех шагов
        return errors
