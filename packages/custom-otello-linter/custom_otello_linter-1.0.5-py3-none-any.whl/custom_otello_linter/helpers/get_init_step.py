import ast

from custom_otello_linter.visitors import Context


def get_init_step(context: Context) -> ast.FunctionDef | None:
    """
    Ищет метод __init__ в сценарии
    """
    for step in context.steps:
        if isinstance(step, ast.FunctionDef) and step.name == '__init__':
            return step


def is_platform_param_present(init_step: ast.FunctionDef) -> bool:
    """
    Проходит по списку декораторов и ищет в них вызовы params с атрибутом Platforms
    """
    for decorator in init_step.decorator_list:
        if isinstance(decorator, ast.Call):
            # Для декораторов вида "@params[allure_labels(AllureID('808960'))](Platforms.MOBILE)"
            # и "@params(Platforms.MOBILE)"
            if (decorator is ast.Call(func=ast.Subscript(value=ast.Name(id='params')))
                    or ast.Call(func=ast.Name(id='params'))):
                # Ищем Platforms в аргументах декоратора params
                for arg in decorator.args:
                    if (
                            isinstance(arg, ast.Attribute)
                            and isinstance(arg.value, ast.Name)
                            and arg.value.id == 'Platforms'
                    ):
                        return True
                return False
    return False
