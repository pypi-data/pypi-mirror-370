




from ._base_value_parser import BaseValueParser

class ByteOperator(BaseValueParser):
    def __init__(self, data: bytes, save_context=None):
        super().__init__(data, save_context)

    def replace_bytes(self, new_bytes: bytes, position: int = None, nr_to_replace: int = None, inc_position: bool = True):
        if position is not None:
            self.position = position
        if nr_to_replace is None:
            nr_to_replace = len(new_bytes)
        self.byte_buffer = self.byte_buffer[:self.position] + new_bytes + self.byte_buffer[self.position + nr_to_replace:]

        if inc_position:
            self.position += + len(new_bytes)

    def insert_bytes(self, new_bytes: bytes, position: int = None, inc_position: bool = True):
        if position is not None:
            self.position = position
        self.byte_buffer = self.byte_buffer[:self.position] + new_bytes + self.byte_buffer[self.position:]

        if inc_position:
            self.position += len(new_bytes)
    
    def snip_bytes(self, length: int):
        self.byte_buffer = self.byte_buffer[:self.position] + self.byte_buffer[self.position + length:]
        