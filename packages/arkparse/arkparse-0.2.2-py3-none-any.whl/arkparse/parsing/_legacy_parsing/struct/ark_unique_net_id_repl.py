from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

@dataclass
class ArkUniqueNetIdRepl:
    unknown: int
    value_type: str
    value: str

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        # print(f"Reading ArkUniqueNetIdRepl at {byte_buffer.get_position()}")
        self.unknown = byte_buffer.read_byte()
        self.value_type = byte_buffer.read_string()
        length = byte_buffer.read_byte()
        self.value = byte_buffer.read_bytes_as_hex(length).replace(' ', '').lower()

    def __str__(self):
        return f"ArkUniqueNetIdRepl: {self.value_type} {self.value}"
    
    def to_json(self):
        return {
            "unknown": self.unknown,
            "value_type": self.value_type,
            "value": self.value
        }
