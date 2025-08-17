from dataclasses import dataclass
from typing import TYPE_CHECKING
from arkparse.logging import ArkSaveLogger
from .ark_item_net_id import ArkItemNetId

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkServerCustomFolder:
    inventory_comp_type: int = 0
    name: str = ""
    custom_folder_ids: list[ArkItemNetId] = None

    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        self.inventory_comp_type = ark_binary_data.parse_int32_property("InventoryCompType")
        self.name = ark_binary_data.parse_string_property("FolderName")
        self.__read_custom_folder_ids(ark_binary_data)
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkServerCustomFolder: {self.inventory_comp_type}, {self.name}, {len(self.custom_folder_ids)} items")

    def __read_custom_folder_ids(self, ark_binary_data: "ArkBinaryParser"):
        ark_binary_data.validate_name("CustomFolderItemIds")
        ark_binary_data.validate_name("ArrayProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("StructProperty")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("ItemNetID")
        ark_binary_data.validate_uint32(1)
        ark_binary_data.validate_name("/Script/ShooterGame")
        ark_binary_data.validate_uint32(0)
        byte = ark_binary_data.read_byte()  # V14 unknown byte
        pos = ark_binary_data.read_uint32()
        array_length = ark_binary_data.read_uint32()

        self.custom_folder_ids = []
        for _ in range(array_length):
            self.custom_folder_ids.append(ArkItemNetId(ark_binary_data))

    def to_json_obj(self):
        return { "inventory_comp_type": self.inventory_comp_type, "name": self.name, "custom_folder_ids": self.custom_folder_ids }
