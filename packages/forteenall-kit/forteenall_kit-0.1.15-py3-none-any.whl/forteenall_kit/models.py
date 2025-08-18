from __future__ import annotations
from abc import ABC

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forteenall_kit.invoke import Invoker


class FeatureData(ABC):
    def __init__(
        self,
    ):
        super().__init__()


class FieldBase(ABC):
    def __init__(self, desc: str):
        self.desc = desc


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
