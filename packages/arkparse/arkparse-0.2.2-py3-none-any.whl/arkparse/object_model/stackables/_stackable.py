
from uuid import UUID
import os

from arkparse import AsaSave
from arkparse.object_model.misc.inventory_item import InventoryItem
from arkparse.parsing import ArkBinaryParser
from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase

class Stackable(InventoryItem):
    def __init__(self, uuid: UUID, binary: ArkBinaryParser):
        super().__init__(uuid, binary)

    @staticmethod
    def _generate(save: AsaSave):
        return ParsedObjectBase._generate(save, os.path.join("templates", "stackable", "stackable"))     

    def __str__(self):
        raise NotImplementedError("This method must be implemented by the subclass")

    
