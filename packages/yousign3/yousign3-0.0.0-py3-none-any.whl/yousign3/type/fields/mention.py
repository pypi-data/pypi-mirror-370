from typing import Self
from yousign.constants import Field
from yousign.type.field import WidthField, NameField


class MentionField(WidthField, NameField):
    mention: str

    def __init__(self):
        super().__init__(Field.Type.SIGNATURE)
        self.mention = ''

    def set_mention(self, mention: str) -> Self:
        if len(mention) <= 255:
            self.reason = mention
        return self

    def set_readonly(self, readonly: bool = False) -> Self:
        self.read_only = readonly
        return self
