from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkColor:
    r: int
    g: int
    b: int
    a: int

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        self.r = ark_binary_data.read_byte()
        self.g = ark_binary_data.read_byte()
        self.b = ark_binary_data.read_byte()
        self.a = ark_binary_data.read_byte()
