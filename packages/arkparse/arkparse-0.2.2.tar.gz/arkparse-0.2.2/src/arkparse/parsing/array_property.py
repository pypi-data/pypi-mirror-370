from dataclasses import dataclass
from typing import TypeVar

from .ark_property import ArkProperty

T = TypeVar('T')

@dataclass
class ArrayProperty(ArkProperty[T]):
    array_type: str
    array_length: int

    def __init__(self, key: str, type: str, index: int, end_of_struct: int, array_type: str, array_length: int, data: T):
        super().__init__(key, type, data, position=index, unknown_byte=end_of_struct)
        self.array_type = array_type
        self.array_length = array_length
