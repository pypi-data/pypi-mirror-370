from typing import Self
from yousign3.constants import Field
from yousign3.type.field import NameField


class CheckboxField(NameField):
    size: int
    optional: bool
    checked: bool
    read_only: bool

    def __init__(self):
        super().__init__(Field.Type.SIGNATURE)
        self.mention = ''
        self.size = 24

    def set_size(self, size: int = 24) -> Self:
        if size >= 8 and size <= 240:
            self.size = size
        return self

    def set_checked(self, readonly: bool = False) -> Self:
        self.read_only = readonly
        return self

    def set_optional(self, optional: bool = False) -> Self:
        self.read_only = optional
        return self

    def set_readonly(self, readonly: bool = False) -> Self:
        self.read_only = readonly
        return self
