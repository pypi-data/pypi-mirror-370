from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkKeyValuePair:
    key: str
    value: str

    def __init__(self, binary_data: "ArkBinaryParser"):
        binary_data.validate_name("Key")
        binary_data.validate_name("IntProperty")
        binary_data.validate_uint32(0)
        binary_data.validate_uint32(4) #size 
        binary_data.validate_byte(0)
        self.key = binary_data.read_int()

        binary_data.validate_name("Value")
        binary_data.validate_name("IntProperty")
        binary_data.validate_uint32(0)
        binary_data.validate_uint32(4)
        binary_data.validate_byte(0)
        self.value = binary_data.read_int()

