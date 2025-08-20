from abc import ABC, abstractmethod
from typing import List

from flake8_plugin_utils import Error

from .scenario_helper import ScenarioHelper


class StepsChecker(ScenarioHelper, ABC):

    @abstractmethod
    def check_steps(self, context, config) -> List[Error]:
        pass
