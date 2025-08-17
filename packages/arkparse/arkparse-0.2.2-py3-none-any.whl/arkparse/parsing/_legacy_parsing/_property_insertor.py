from arkparse.parsing._base_value_validator import BaseValueValidator
from typing import List

class PropertyInsertor(BaseValueValidator):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def insert_name(self, name: str, position: int = None):
        if self.save_context is None:
            raise ValueError("Save context is not set")

        if position is not None:
            self.position = position

        name = self.save_context.get_name_id(name)

        if name is None:
            raise ValueError(f"Name {name} not found in save context")
        
        name_bytes = name.to_bytes(4, byteorder="little")
        name_bytes += b'\x00\x00\x00\x00'

        self.insert_bytes(name_bytes, position)

    def insert_string(self, string: str, position: int = None):
        if position is not None:
            self.position = position

        string_bytes = string.encode("utf-8") + b'\x00'
        length = len(string_bytes)
        
        self.insert_uint32(length)
        self.insert_bytes(string_bytes)

    def insert_uint32(self, value: int, position: int = None):
        if position is not None:
            self.position = position
        value_bytes = value.to_bytes(4, byteorder="little")
        self.insert_bytes(value_bytes)
        
    def insert_array(self, array_name: str, property_type: str, item_bytes: List[bytes], position: int = None):
        if self.save_context is None:
            raise ValueError("Save context is not set")
        
        if position is not None:
            self.position = position

        array_length = len(item_bytes) * len(item_bytes[0]) + 4 # 4 bytes for array length

        self.insert_name(array_name)
        self.insert_name("ArrayProperty")
        self.insert_uint32(array_length)
        self.insert_uint32(0)
        self.insert_name(property_type)
        self.insert_bytes(b'\x00')
        self.insert_uint32(len(item_bytes))

        for item in item_bytes:
            self.insert_bytes(item)
        