from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from forteenall_kit.feature import FeatureManager
from forteenall_kit.models import FeatureData, FieldBase


class Invoker(ABC):
    model: FeatureData = None

    def __init__(
        self,
        name: str,
        manager: FeatureManager,
        options: dict[str, Any],
        invokerType: str,
    ):
        # set main data from manager
        self.name = name
        self.manager = manager
        self.options = options
        self.feature_type = invokerType

        if self.model is None:
            raise SyntaxError(f"model `{self.feature_type}:{self.name}` is None")

        self.objects: FeatureData = self.model(options)

        # set field and another data
        for option, value in self.options.items():
            feature_model_field_instance: FieldBase = self.model.__dict__[option]
            feature_model_field_instance.setValue(value)
            self.objects._addField(option, feature_model_field_instance)

            self.__setattr__(option, value)

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
