from dataclasses import dataclass
from typing import TYPE_CHECKING
from arkparse.logging import ArkSaveLogger

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkGachaResourceStruct:
    class_name: str = ""
    base_quantity: float = 0.0

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        name = ark_binary_data.peek_name()
        or_name: str = ark_binary_data.parse_object_reference_property(name).value
        if not or_name.startswith("BlueprintGeneratedClass "):
            ArkSaveLogger.parser_log(f"Unexpected ObjectReference name: {or_name}")
        self.class_name = or_name.replace("BlueprintGeneratedClass ", "")
        name = ark_binary_data.peek_name()
        self.base_quantity = ark_binary_data.parse_float_property(name)
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkGachaResourceStruct: {self.class_name}, {self.base_quantity}")