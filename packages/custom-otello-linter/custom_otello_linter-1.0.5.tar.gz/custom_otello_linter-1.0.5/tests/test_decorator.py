from flake8_plugin_utils import assert_error, assert_not_error

from custom_otello_linter.errors import DecoratorVedroParams
from custom_otello_linter.visitors import ScenarioVisitor
from custom_otello_linter.visitors.scenario_checkers import VedroParamsChecker


def test_vedro_decorator_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(VedroParamsChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @vedro.params(1)
        @vedro.params(2)
        def __init__(foo): pass
    """
    assert_error(ScenarioVisitor, code, DecoratorVedroParams)


def test_decorator_params():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(VedroParamsChecker)
    code = """
    class Scenario:
        subject = 'any subject'
        @params(1)
        @params(2)
        def __init__(foo): pass
    """
    assert_not_error(ScenarioVisitor, code)


def test_decorator_params_imported_from_vedro():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(VedroParamsChecker)
    code = """
    from vedro import params
    class Scenario:
        subject = 'any subject'
        @params(1)
        @params(2)
        def __init__(foo): pass
    """
    assert_error(ScenarioVisitor, code, DecoratorVedroParams)


def test_vedro_decorator_skip():
    ScenarioVisitor.deregister_all()
    ScenarioVisitor.register_scenario_checker(VedroParamsChecker)
    code = """
    @vedro.skip
    class Scenario: pass
    """
    assert_not_error(ScenarioVisitor, code)
