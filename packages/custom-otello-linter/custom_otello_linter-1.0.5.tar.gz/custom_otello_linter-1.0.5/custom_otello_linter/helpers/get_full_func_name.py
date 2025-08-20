import ast


def get_full_func_name(func_node) -> str:
    """
    Извлекает полное имя функции из узла ast.Call.func.
    Для прямых вызовов (make_screenshot_for_comparison) возвращает 'make_screenshot_for_comparison'.
    Для вызовов через атрибуты (self.page.make_screenshot_for_comparison)
    возвращает 'self.page.make_screenshot_for_comparison'.
    """
    if isinstance(func_node, ast.Name):
        return func_node.id
    elif isinstance(func_node, ast.Attribute):
        return get_full_func_name(func_node.value) + '.' + func_node.attr
    return ""
