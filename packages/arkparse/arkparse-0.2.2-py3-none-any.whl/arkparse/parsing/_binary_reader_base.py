from ..saves.save_context import SaveContext

class BinaryReaderBase:
    LENGTH_OF_NAME = 8
    LENGTH_OF_BOOLEAN_PROPERTY = 26

    def __init__(self, data: bytes, save_context=None):
        self.byte_buffer = data
        self.position = 0
        self.save_context = save_context if save_context else SaveContext()
        self.in_cryopod = False

    def get_position(self) -> int:
        return self.position

    def set_position(self, i: int):
        self.position = i

    def has_more(self) -> bool:
        return self.position < len(self.byte_buffer)

    def size(self) -> int:
        return len(self.byte_buffer)
    