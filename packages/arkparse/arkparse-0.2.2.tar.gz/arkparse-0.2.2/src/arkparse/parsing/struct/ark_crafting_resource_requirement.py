from dataclasses import dataclass
from typing import TYPE_CHECKING
from arkparse.logging import ArkSaveLogger

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkCraftingResourceRequirement:
    base_requirement: float = 0
    resource_type: str = ""
    require_exact_type: bool = False

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        self.base_requirement = ark_binary_data.parse_float_property("BaseResourceRequirement")
        self.__read_type(ark_binary_data)
        self.require_exact_type = ark_binary_data.parse_boolean_property("bCraftingRequireExactResourceType")
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkCraftingResourceRequirement: {self.base_requirement}, {self.resource_type}, {self.require_exact_type}")

    def __read_type(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("ResourceItemType")
        ark_binary_data.validate_name("ObjectProperty")
        ark_binary_data.validate_uint32(0)
        ark_binary_data.read_byte()
        ark_binary_data.validate_uint32(0)
        ark_binary_data.validate_uint16(1)
        full_name = ark_binary_data.read_name()
        if not full_name.startswith("BlueprintGeneratedClass "):
            ArkSaveLogger.open_hex_view()
            raise Exception(f"Expected ResourceItemType to start with 'BlueprintGeneratedClass ', got {full_name}")
        self.resource_type = full_name.replace("BlueprintGeneratedClass ", "")

