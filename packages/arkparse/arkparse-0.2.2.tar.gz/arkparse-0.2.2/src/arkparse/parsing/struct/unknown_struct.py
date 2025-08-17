from dataclasses import dataclass

@dataclass
class UnknownStruct:
    struct_type: str
    value: str

    def __init__(self, struct_type: str, value: str):
        self.struct_type = struct_type
        self.value = value
