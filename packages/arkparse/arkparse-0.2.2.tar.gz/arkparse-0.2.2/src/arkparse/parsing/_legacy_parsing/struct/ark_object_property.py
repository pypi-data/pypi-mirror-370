from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

@dataclass
class ArkObjectProperty:
    name : str
    value : int

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        self.name = byte_buffer.read_string()
        self.value = byte_buffer.read_uint32()

    def __str__(self) -> str:
        return f"OP[name:{self.name} value:{self.value}]"