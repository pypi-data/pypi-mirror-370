from __future__ import annotations
from abc import ABC, abstractmethod
from forteenall_kit.feature import FeatureManager


class Invoker(ABC):
    @abstractmethod
    def __init__(self, name):
        self.name = name
        self.manager: FeatureManager = FeatureManager()

    @property
    def spaces(self):
        return self.manager.spaces

    def init(self):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def log(self, message):
        print(f"[{self.name}] {message}")

    def _generate(self):
        """
        this function generate YAML standard
        this yaml use in forteenall kit
        for another packages
        """
