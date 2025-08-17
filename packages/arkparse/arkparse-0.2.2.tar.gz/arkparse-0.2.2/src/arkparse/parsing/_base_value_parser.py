import struct
from typing import List
from uuid import UUID

from ._binary_reader_base import BinaryReaderBase
from arkparse.logging import ArkSaveLogger

class BaseValueParser(BinaryReaderBase):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def read_int(self) -> int:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an int.")
        result = struct.unpack_from('<i', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_uint32(self) -> int:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned int.")
        result = struct.unpack_from('<I', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_uint16(self) -> int:
        if self.position + 2 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned short.")
        result = struct.unpack_from('<H', self.byte_buffer, self.position)[0]
        self.position += 2
        return result

    def read_uint64(self) -> int:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read an unsigned long.")
        result = struct.unpack_from('<Q', self.byte_buffer, self.position)[0]
        self.position += 8
        return result
    
    def read_int64(self) -> int:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a long.")
        result = struct.unpack_from('<q', self.byte_buffer, self.position)[0]
        self.position += 8
        return result

    def read_bytes(self, count: int) -> bytes:
        if count > len(self.byte_buffer) - self.position:
            ArkSaveLogger.open_hex_view()
            raise ValueError("Attempting to read more bytes than available in the buffer: " + str(count) + " " + str(len(self.byte_buffer) - self.position))
        result = self.byte_buffer[self.position:self.position + count]
        self.position += count
        return result

    def skip_bytes(self, count: int):
        self.position += count

    def read_string(self) -> str:
       
        length = self.read_int()
        if length == 0:
            return None
        
        is_multi_byte = length < 0
        abs_length = abs(length)

        result = ""
        if is_multi_byte:
            ArkSaveLogger.parser_log(f"Reading multi-byte string of length {abs_length}")
            # ArkSaveLogger.open_hex_view(True)
            for _ in range(abs_length - 1):
                result += self.read_bytes(1).decode('utf-8', errors='ignore')
                self.skip_bytes(1)  # Skip the null
            terminator = self.read_uint16()  # Read the null terminator
        else:
            pre_read_pos = self.position
            result = self.read_bytes(abs_length - 1).decode('utf-8', errors='ignore')
            terminator = self.read_byte()

        if terminator != 0:
            ArkSaveLogger.warning_log(f"Terminator is not zero: {terminator}")
            self.position = pre_read_pos
            # ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
                

        return result

    def read_chars(self, size: int) -> str:
        result = struct.unpack_from(f'<{size}s', self.byte_buffer, self.position)[0].decode('utf-16')
        self.position += size * 2
        return result

    def read_boolean(self) -> bool:
        return self.read_byte() != 0

    def read_float(self) -> float:
        if self.position + 4 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a float.")
        result = struct.unpack_from('<f', self.byte_buffer, self.position)[0]
        self.position += 4
        return result

    def read_double(self) -> float:
        if self.position + 8 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a double.")
        result = struct.unpack_from('<d', self.byte_buffer, self.position)[0]
        self.position += 8
        return result

    def read_short(self) -> int:
        if self.position + 2 > len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a short.")
        result = struct.unpack_from('<h', self.byte_buffer, self.position)[0]
        self.position += 2
        return result

    def read_unsigned_byte(self) -> int:
        # ArkSaveLogger.enable_debug = True
        # ArkSaveLogger.set_file(self, "read_unsigned_byte")
        # ArkSaveLogger.open_hex_view(True)
        return self.read_byte() & 0xFF

    def read_byte(self) -> int:
        if self.position >= len(self.byte_buffer):
            raise IndexError("Buffer underflow: not enough bytes to read a byte.")
        result = self.byte_buffer[self.position]
        self.position += 1
        return result

    def read_uuid(self) -> UUID:
        return UUID(bytes=self.read_bytes(16))
    
    def read_uuid_as_string(self) -> str:
        return str(self.read_uuid())

    def peek_int(self) -> int:
        current_position = self.position
        value = self.read_int()
        self.position = current_position
        return value
    
    def read_name(self, default=None, is_peek=False) -> str:
        if not self.save_context.has_name_table():
            return self.read_string()

        pos = self.position    
        name_id = self.read_uint32()
        name = self.save_context.get_name(name_id)
        # print(f"Reading name with id {name_id} at position {self.position}, name: {name}")

        if is_peek:
            return name if name is not None else default

        if name is None and default is not None:
            name = default
            # print(f"Name with id {name_id} not found, using default: {name}")
            ArkSaveLogger.parser_log(f"Name with id {name_id} not found, using default: {name}")

        if name is None and self.save_context.generate_unknown:
            name = f"UnknownName_{name_id:08X}"
            ArkSaveLogger.warning_log(f"Name with id {name_id} not found, generating unknown name: {name}")
        
        if name is None:
            # ArkSaveLogger.enable_debug = True
            ArkSaveLogger.open_hex_view()
            raise ValueError(f"Name is None, for name index {hex(name_id)} at position {pos}")

        if name == "NPCZoneVolume" or "NPCZoneVolume_" in name or "_NPCZoneVolume" in name or "NPCCountVolume" in name:
            return name + "_" + hex(self.read_int())

        always_zero = self.read_int()

        no_prints = ["DontDoMaterialSpawning", "CorruptSpawnInValue", "LadderSocket"]
        if always_zero != 0 and name not in no_prints:
            ArkSaveLogger.warning_log(f"Always zero is not zero: {always_zero}, for name {name} at position {pos}")
        
        return name
    
    def peek_name(self, ahead: int = 0) -> str:
        pos = self.position
        self.position += ahead
        name = self.read_name(default="", is_peek=True)
        self.position = pos
        return name
    
    def read_strings_array(self) -> List[str]:
        count = self.read_uint32()
        return [self.read_string() for _ in range(count)]

    def read_names(self, name_count: int) -> List[str]:
        names = []
        offsets = []

        for _ in range(name_count):
            if self.save_context.is_read_names_as_strings():
                offsets.append(self.position + 4)
                names.append(self.read_string())
            else:
                names.append(self.read_name())
        return names, offsets
    
    def read_bytes_as_hex(self, data_size: int) -> str:
        # Reads `data_size` bytes from the current position and returns them as a hexadecimal string
        bytes_data = self.read_bytes(data_size)
        return ' '.join(f"{byte:02X}" for byte in bytes_data)
    