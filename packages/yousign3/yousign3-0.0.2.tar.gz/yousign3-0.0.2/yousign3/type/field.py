from typing import Self, Optional
from yousign3.constants import Field as ConstField
from yousign3.datasets import FieldData


class Field:
    type: ConstField.Type
    x: int
    y: int
    page: int
    document_id: Optional[str]
    signer_id: Optional[str]

    def __init__(self, _type: ConstField.Type):
        self.type = _type
        self.x = 0
        self.y = 0
        self.page = 1
        self.document_id = None
        self.signer_id = None

    def set_document_id(self, document_id: str) -> Self:
        self.document_id = document_id
        return self

    def set_signer_id(self, signer_id: str) -> Self:
        self.signer_id = signer_id
        return self

    def set_x(self, x: int) -> Self:
        self.x = x
        return self

    def set_y(self, y: int) -> Self:
        self.y = y
        return self

    def set_page(self, page: int) -> Self:
        self.page = page
        return self

    def conclude(self) -> FieldData:
        return FieldData(**self.__dict__)


class NameField(Field):
    name: str

    def __init__(self, _type: ConstField.Type):
        super().__init__(_type)
        self.name = ''

    def set_name(self, name: str) -> Self:
        self.name = name
        return self


class WidthField(Field):
    width: int
    height: int

    def __init__(self, _type: ConstField.Type):
        super().__init__(_type)
        self.width = 24
        self.height = 1

    def set_width(self, width: int) -> Self:
        if self.width < 24:
            return self
        self.width = width
        return self

    def set_height(self, height: int) -> Self:
        if self.width < 1:
            return self
        self.height = height
        return self
