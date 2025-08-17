from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ark_binary_parser import ArkBinaryParser

from arkparse.logging import ArkSaveLogger
from .ark_vector import ArkVector


@dataclass
class ArkVectorBoolPair:
    vector: ArkVector
    bool_: bool

    def __init__(self, byte_buffer: "ArkBinaryParser"):

        byte_buffer.validate_string("VectorVal")
        byte_buffer.validate_string("StructProperty")
        byte_buffer.validate_uint64(24)
        byte_buffer.validate_string("Vector")

        byte_buffer.skip_bytes(17)

        self.vector = ArkVector(byte_buffer)

        byte_buffer.validate_string("BoolVal")
        byte_buffer.validate_string("BoolProperty")
        byte_buffer.validate_uint64(0)

        self.bool_ = byte_buffer.read_uint16() != 0

        byte_buffer.validate_string("None")

        ArkSaveLogger.parser_log(
            f"Read vector bool pair {self.vector} {self.vector}")

    def __str__(self):
        return f"ArkVectorBoolPair: {self.vector} {self.bool_}"
