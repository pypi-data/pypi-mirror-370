from flake8_plugin_utils import assert_error, assert_not_error

from custom_otello_linter.errors import MultipleScreenshotsError
from custom_otello_linter.visitors import ScenarioVisitor
from custom_otello_linter.visitors.steps_checkers import MakeScreenshotChecker


def test_two_funcs_make_screenshot_in_step_then():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MakeScreenshotChecker)
    code = """
    class Scenario:
        def when(): pass
        def then():
            self.page.make_screenshot_for_comparison()
            self.page.make_screenshot_for_comparison()
    """
    assert_error(ScenarioVisitor, code, MultipleScreenshotsError, step_name='then')


def test_one_func_make_screenshot_in_step_then():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MakeScreenshotChecker)
    code = """
    class Scenario:
        def when(): pass
        def then():
            self.page.make_screenshot_for_comparison()
    """
    assert_not_error(ScenarioVisitor, code)


def test_two_func_make_screenshot_with_another_obj():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MakeScreenshotChecker)
    code = """
    class Scenario:
        def when(): pass
        def then():
            photos.make_screenshot_for_comparison()
            photos.make_screenshot_for_comparison()
    """
    assert_error(ScenarioVisitor, code, MultipleScreenshotsError, step_name='then')


def test_two_func_make_screenshot_in_step_and():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MakeScreenshotChecker)
    code = """
    class Scenario:
        def when(): pass
        def and_():
            self.page.make_screenshot_for_comparison()
            self.page.make_screenshot_for_comparison()
    """
    assert_error(ScenarioVisitor, code, MultipleScreenshotsError, step_name='and_')


def test_two_func_make_screenshot_in_step_but():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(MakeScreenshotChecker)
    code = """
    class Scenario:
        def when(): pass
        def but():
            self.page.make_screenshot_for_comparison()
            self.page.make_screenshot_for_comparison()
    """
    assert_error(ScenarioVisitor, code, MultipleScreenshotsError, step_name='but')
