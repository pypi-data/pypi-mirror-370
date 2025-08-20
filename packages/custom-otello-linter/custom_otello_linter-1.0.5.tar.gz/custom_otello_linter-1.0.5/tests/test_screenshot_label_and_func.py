from flake8_plugin_utils import assert_error, assert_not_error

from custom_otello_linter.errors import (
    MissingMakeScreenshotFuncCallError,
    MissingScreenshotsAllureLabelError
)
from custom_otello_linter.visitors import ScenarioVisitor
from custom_otello_linter.visitors.scenario_and_steps_checkers.screenshot_label_and_func_checker import (
    ScreenshotsLabelAndFuncChecker
)


def test_screenshot_label_with_make_screenshot_func():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    @allure_labels(SCREENSHOTS)
    class Scenario:
        def when(): pass
        def then():
            photos.make_screenshot_for_comparison()
    """
    assert_not_error(ScenarioVisitor, code)


def test_screenshot_label_without_make_screenshot_func():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    @allure_labels(SCREENSHOTS)
    class Scenario:
        def when(): pass
        def then(): pass
    """
    assert_error(ScenarioVisitor, code, MissingMakeScreenshotFuncCallError)


def test_make_screenshot_func_without_screenshots_label():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    @allure_labels(MANUAL, Priority.P0)
    class Scenario:
        def when(): pass
        def then():
            self.page.make_screenshot_for_comparison()
    """
    assert_error(ScenarioVisitor, code, MissingScreenshotsAllureLabelError)


def test_other_labels_without_make_screenshot_func():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    @allure_labels(MANUAL, Feature.One)
    class Scenario:
        def when(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_multiple_labels_with_make_screenshot_func():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    @allure_labels(MANUAL, Feature.One, SCREENSHOTS)
    class Scenario:
        def when(): pass
        def then():
            self.page.make_screenshot_for_comparison()
    """
    assert_not_error(ScenarioVisitor, code)


def test_screenshot_label_and_make_screenshot_func_with_parameter():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    @allure_labels(MANUAL, Feature.One, SCREENSHOTS)
    class Scenario:
        def when(): pass
        def then():
            self.page.make_screenshot_for_comparison(focus_on=self.page.payment.applied_discounts.locator)
    """
    assert_not_error(ScenarioVisitor, code)


def test_no_labels_no_make_screenshot_func():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(ScreenshotsLabelAndFuncChecker)
    code = """
    class Scenario:
        def when(): pass
        def then(): pass
    """
    assert_not_error(ScenarioVisitor, code)
