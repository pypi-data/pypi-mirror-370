from typing import Optional, Self
from yousign3.type.field import WidthField, NameField
from yousign3.constants import Field as ConstField
from yousign3.datasets import FontData


class ReadOnlyTextField(WidthField):
    text: str
    font: Optional[FontData]

    def __init__(self):
        super().__init__(ConstField.Type.READ_ONLY)
        self.font = None
        self.text = ''

    def set_text(self, text: str) -> Self:
        if len(text) <= 5000:
            self.text = text
        return self

    def set_font(self, font: Optional[FontData] = None) -> Self:
        self.font = font
        return self


class TextField(WidthField, NameField):
    max_length: int
    question: str
    instruction: Optional[str]
    optional: bool
    font: Optional[FontData]
    default_value: str
    read_only: bool

    def __init__(self):
        super().__init__(ConstField.Type.TEXT)
        self.read_only = False
        self.default_value = None
        self.optional = False
        self.instruction = None
        self.question = ''
        self.max_length = 1

    def set_maxlength(self, max_length: int) -> Self:
        if max_length >= 1 and max_length <= 32767:
            self.max_length = max_length
        return self

    def set_question(self, question: str) -> Self:
        if len(question) < 255:
            self.question = question
        return self

    def set_instruction(self, instruction: Optional[str] = None) -> Self:
        self.instruction = instruction
        return self

    def set_optional(self, optional: bool = False) -> Self:
        self.optional = optional
        return self

    def set_font(self, font: Optional[FontData] = None) -> Self:
        self.font = font
        return self

    def set_default(self, default: Optional[str] = None) -> Self:
        self.default_value = default
        return self

    def set_readonly(self, readonly: bool = False) -> Self:
        self.read_only = readonly
        return self
