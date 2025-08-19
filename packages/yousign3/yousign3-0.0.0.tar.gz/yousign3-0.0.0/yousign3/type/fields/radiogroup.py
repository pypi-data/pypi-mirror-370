from typing import Self, List
from yousign.datasets import RadioData
from yousign.constants import Field
from yousign.type.field import WidthField, NameField


class RadioGroup(WidthField, NameField):
    read_only: bool
    radios: List[RadioData]

    def __init__(self):
        super().__init__(Field.Type.SIGNATURE)
        self.read_only = False

    def set_radios(self, radios: List[RadioData] = []) -> Self:
        self.radios = radios
        return self
