from __future__ import annotations
from abc import ABC

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forteenall_kit.invoke import Invoker


class FieldBase(ABC):
    def __init__(self, desc: str):
        self.desc = desc
        self.value = None

    def __str__(self):
        return f"<{super().__str__()}: {str(self.value)}>"

    def setValue(self, value):
        self.value = value


class CharField(FieldBase): ...


class BoolField(FieldBase): ...


class TextField(FieldBase): ...


class IntegerField(FieldBase): ...


class ChoiceField(FieldBase):
    def __init__(self, desc, choices: list[str]):
        super().__init__(desc)
        self.choices = choices


class FeatureM2OField(FieldBase):
    def __init__(self, desc, to: Invoker):
        super().__init__(desc)
        self.feature = to


class FeatureM2MField(FieldBase):
    def __init__(self, desc, to: Invoker):
        super().__init__(desc)
        self.feature = to


class FeatureValueRelationField(FieldBase):
    def __init__(self, desc, to: Invoker, feature_field_name: str):
        super().__init__(desc)
        self.feature = to
        self.feature_field_name = feature_field_name


class FeatureData(ABC):
    def __init__(self, options):
        super().__init__()

        # this options set from JSON
        self.options = options

    def _addField(self, name: str, field: FieldBase):
        self.__setattr__(name, field)
