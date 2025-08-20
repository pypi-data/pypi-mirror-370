from typing import Self
from yousign3.constants import Field
from yousign3.type.field import WidthField
from typing import Optional


class SignatureField(WidthField):
    reason: Optional[str]

    def __init__(self):
        super().__init__(Field.Type.SIGNATURE)
        self.set_width(85)
        self.set_height(37)

    def set_reason(self, reason: Optional[str] = None) -> Self:
        self.reason = reason
        return self
