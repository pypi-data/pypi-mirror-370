from typing import List

from flake8_plugin_utils import Error

from custom_otello_linter.abstract_checkers import StepsChecker
from custom_otello_linter.errors import (
    MissingMakeScreenshotFuncCallError,
    MissingScreenshotsAllureLabelError
)
from custom_otello_linter.helpers.get_make_screenshot_calls import (
    get_make_screenshot_calls
)
from custom_otello_linter.visitors.scenario_visitor import (
    Context,
    ScenarioVisitor
)


@ScenarioVisitor.register_steps_checker
class ScreenshotsLabelAndFuncChecker(StepsChecker):

    def check_steps(self, context: Context, config) -> List[Error]:
        errors = []

        allure_decorator = self.get_allure_labels_decorator(context.scenario_node)
        has_screenshot_label = False
        has_screenshot_func = False

        # Проверяем, есть ли в списке лейблов SCREENSHOTS
        if allure_decorator:
            allure_tags = self.get_allure_labels_names(allure_decorator)
            has_screenshot_label = "SCREENSHOTS" in allure_tags

        # Проверяем наличие вызова функции make_screenshot_for_comparison
        for step in context.steps:
            if get_make_screenshot_calls(step):
                has_screenshot_func = True
                break

        # Если в тесте есть лейбл, но нет вызова функции – добавляем ошибку
        if has_screenshot_label and not has_screenshot_func:
            errors.append(MissingMakeScreenshotFuncCallError(
                lineno=allure_decorator.lineno,
                col_offset=allure_decorator.lineno))

        # Если в тесте есть вызов функции, но нет лейбла – добавляем ошибку
        if has_screenshot_func and not has_screenshot_label:
            errors.append(MissingScreenshotsAllureLabelError(
                lineno=allure_decorator.lineno,
                col_offset=allure_decorator.col_offset))

        # Возвращаем собранные ошибки после завершения всех шагов
        return errors
