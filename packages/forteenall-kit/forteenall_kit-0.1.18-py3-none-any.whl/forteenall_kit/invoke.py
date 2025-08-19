from __future__ import annotations
from abc import ABC, abstractmethod
from forteenall_kit.feature import FeatureManager


class Invoker(ABC):
    def __init__(self, name: str, manager: FeatureManager):
        self.name = name
        self.manager = manager

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
