from flake8_plugin_utils import assert_error, assert_not_error

from custom_otello_linter.errors import MissingPlatformArgError
from custom_otello_linter.visitors import ScenarioVisitor
from custom_otello_linter.visitors.steps_checkers.platform_usage_checker import PlatformParamsChecker


def test_scenario_with_platform_param_used_as_kw_arg_in_mocked_context():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params[allure_labels(AllureID('808960'))](Platforms.DESKTOP)
        @params[allure_labels(AllureID('808961'))](Platforms.MOBILE)
        def __init__(self, platform):
            pass

        async def given_opened_page(self):
            with mocked_page():
                self.page = await opened_page(booking=self.booking, platform=self.platform)
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_platform_param_used_as_pos_arg():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params[allure_labels(AllureID('808960'))](Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass

        def given_opened_page(self):
            self.page = await opened_page(self.booking, self.platform)
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_platform_param_in_when_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass
        
        def given_data_prepare(self):
            pass

        async def when_opened_page(self):
            self.page = await opened_page(self.booking, self.platform)
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_without_platform_param():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):
        def __init__(self, platform):
            pass

        def given_opened_page(self):
            self.page = await opened_page(self.booking)
    """
    assert_not_error(ScenarioVisitor, code)


def test_scenario_with_platform_param_not_used():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params[allure_labels(AllureID('808960'))](Platforms.DESKTOP)
        @params[allure_labels(AllureID('808961'))](Platforms.MOBILE)
        def __init__(self, platform):
            pass

        async def given_opened_page(self):
            self.page = await opened_page(booking=self.booking)
    """
    assert_error(ScenarioVisitor, code, MissingPlatformArgError)


def test_scenario_with_platform_param_not_used_in_when_step():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params[allure_labels(AllureID('808960'))](Platforms.MOBILE)
        def __init__(self, platform):
            pass

        def when_opened_page(self):
            self.page = await opened_page(booking=self.booking)
    """
    assert_error(ScenarioVisitor, code, MissingPlatformArgError)


def test_scenario_with_platform_param_not_used_and_mocked_context():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass

        async def given_opened_page(self):
            with mocked_page():
                self.page = await opened_page(booking=self.booking)
    """
    assert_error(ScenarioVisitor, code, MissingPlatformArgError)


def test_scenario_with_line_similar_to_opening_context():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass

        async def given_opened_page(self):
            with mocked_page():
                self.page = await opened_page(booking=self.booking, platform=self.platform)
                self.notification_text = await self.page.notification.text.text_content()
    """
    assert_not_error(ScenarioVisitor, code, MissingPlatformArgError)


def test_scenario_with_line_similar_to_opening_context_and_missing_platform():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_steps_checker(PlatformParamsChecker)
    code = """
    class Scenario(vedro.Scenario):

        @params(Platforms.DESKTOP)
        @params(Platforms.MOBILE)
        def __init__(self, platform):
            pass

        async def given_opened_page(self):
            with mocked_page():
                self.page = await opened_page(booking=self.booking)
                self.notification_text = await self.page.notification.text.text_content()
    """
    assert_error(ScenarioVisitor, code, MissingPlatformArgError)