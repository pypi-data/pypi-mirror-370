from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from arkparse.parsing.ark_binary_parser import ArkBinaryParser

@dataclass
class ArkIntPoint:
    value1 : int
    value2 : int

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        self.value1 = byte_buffer.read_int()
        self.value2 = byte_buffer.read_int()

    def __str__(self):
        return f"ArkIntPoint: ({self.value1}, {self.value2})"