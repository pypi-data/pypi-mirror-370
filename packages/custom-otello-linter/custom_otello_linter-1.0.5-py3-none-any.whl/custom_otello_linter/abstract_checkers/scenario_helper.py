import ast
from typing import List, Union

SCENARIOS_FOLDER = 'scenarios'


class ScenarioHelper:

    def get_all_steps(self, class_node: ast.ClassDef) -> List:
        return [
            element for element in class_node.body if (
                isinstance(element, ast.FunctionDef)
                or isinstance(element, ast.AsyncFunctionDef)
            )
        ]

    def get_allure_labels_decorator(self, scenario_node: ast.ClassDef) -> Union[ast.Call, None]:
        """
        Метод находит узел с декоратором allure_labels и списком лейблов.
        Лейблы, указанные в параметризации, не попадут в выборку
        """

        for decorator in scenario_node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == 'allure_labels':
                    return decorator

    def get_allure_labels_names(self, allure_decorator: ast.Call) -> List[str]:
        """
        Метод получает список лейблов из переданного декоратора @allure_labels
        """

        def get_label_first_name(arg: ast.Attribute) -> str:
            if isinstance(arg.value, ast.Attribute):
                return get_label_first_name(arg.value)
            if isinstance(arg.value, ast.Name):
                return arg.value.id

        labels_names = []
        for arg in allure_decorator.args:
            if isinstance(arg, ast.Attribute):
                labels_names.append(get_label_first_name(arg))
            elif isinstance(arg, ast.Name):
                labels_names.append(arg.id)
        return labels_names
