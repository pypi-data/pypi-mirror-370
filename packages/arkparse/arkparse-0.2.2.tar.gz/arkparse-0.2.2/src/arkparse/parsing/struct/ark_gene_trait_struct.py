from dataclasses import dataclass
from typing import TYPE_CHECKING
from arkparse.logging import ArkSaveLogger

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkGeneTraitStruct:
    unique_id: float = 0.0
    class_name: str = ""
    name: str = ""


    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        name = ark_binary_data.peek_name()
        self.unique_id = ark_binary_data.parse_double_property(name)
        name = ark_binary_data.peek_name()
        or_name: str = ark_binary_data.parse_object_reference_property(name).value
        if not or_name.startswith("BlueprintGeneratedClass "):
            ArkSaveLogger.parser_log(f"Unexpected ObjectReference name: {or_name}")
        self.class_name = or_name.replace("BlueprintGeneratedClass ", "")
        name = ark_binary_data.peek_name()
        self.name = ark_binary_data.parse_name_property(name)
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkGeneTraitStruct: {self.unique_id}, {self.class_name}, {self.name}")

    def to_json_obj(self):
        return { "unique_id": self.unique_id, "class_name": self.class_name, "name": self.name }
