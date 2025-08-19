from typing import Any, Generic, TypeVar

from dooit.api import DooitModel
from ._input import Input

ModelType = TypeVar("ModelType", bound=DooitModel)
ModelValue = TypeVar("ModelValue", bound=Any)


class SimpleInput(Input, Generic[ModelType, ModelValue]):
    """
    A simple single line Text Input widget
    """

    _cursor_pos: int = 0
    _cursor: str = "|"

    def __init__(self, model: ModelType) -> None:
        self.model = model

        default_value = self._get_default_value()
        super().__init__(value=default_value)

        self.reset()

    def _get_default_value(self) -> str:
        return str(self.model_value)

    @property
    def _property(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def model_value(self) -> ModelValue:
        return getattr(self.model, self._property)

    @model_value.setter
    def model_value(self, value: str) -> None:
        return setattr(self.model, self._property, value)

    def _typecast_value(self, value: str) -> Any:
        return value

    def reset(self) -> str:
        self._cursor_pos = len(self.value)
        return self.value

    def stop_edit(self) -> None:
        self._value = self.value.strip()
        try:
            self.model_value = self._typecast_value(self.value)
            self.model.save()
        finally:
            self._value = self._get_default_value()
            super().stop_edit()
            self.move_cursor_to_end()

    def keypress(self, key: str) -> None:
        super().keypress(key)
