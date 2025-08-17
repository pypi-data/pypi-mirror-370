from typing import List, Optional
from uuid import UUID

from .ark_property_container import ArkPropertyContainer
from .ark_binary_parser import ArkBinaryParser
from arkparse.parsing.struct.ark_rotator import ArkRotator
from arkparse.parsing.struct.ark_vector import ArkVector
from arkparse.logging import ArkSaveLogger

class ArkObject(ArkPropertyContainer):
    def __init__(
        self,
        uuid: UUID,
        class_name: str,
        item: bool,
        names: List[str],
        from_data_file: bool,
        data_file_index: int,
        properties_offset: int,
        vector: Optional[ArkVector] = None,
        rotator: Optional[ArkRotator] = None
    ):
        super().__init__()
        self.uuid = uuid
        self.class_name = class_name
        self.item = item
        self.names = names
        selffrom_data_file = from_data_file
        self.data_file_index = data_file_index
        self.properties_offset = properties_offset
        self.vector = vector
        self.rotator = rotator

    @classmethod
    def from_reader(cls, reader: ArkBinaryParser) -> "ArkObject":
        uuid = reader.read_uuid()
        class_name = reader.read_string()
        item = reader.read_uint32()
        names = reader.read_strings_array()
        from_data_file = reader.read_uint32()
        data_file_index = reader.read_int()

        vector = None
        rotator = None
        if reader.read_uint32() != 0:
            vector = ArkVector(reader)
            rotator = ArkRotator(reader)
        
        properties_offset = reader.read_int()
        reader.validate_uint32(0)

        ArkSaveLogger.parser_log(f"Read ArkObject: {class_name} with UUID {uuid} at offset {properties_offset}")

        return cls(
            uuid=uuid,
            class_name=class_name,
            item=item,
            names=names,
            from_data_file=from_data_file,
            data_file_index=data_file_index,
            properties_offset=properties_offset,
            vector=vector,
            rotator=rotator
        )
