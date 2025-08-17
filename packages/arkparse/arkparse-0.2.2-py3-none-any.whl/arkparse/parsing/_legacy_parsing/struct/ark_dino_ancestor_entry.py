from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arkparse.parsing import ArkBinaryParser

class ArkDinoAncestor:
    name: str
    id1: int
    id2: int

    def __init__(self, name: str, id1: int, id2: int):
        self.name = name
        self.id1 = id1
        self.id2 = id2

    def __str__(self):
        return f"Ancestor:(name={self.name}, id=({self.id1}, {self.id2}))"

@dataclass
class ArkDinoAncestorEntry:
    male: ArkDinoAncestor
    female: ArkDinoAncestor

    def __init__(self, byte_buffer: "ArkBinaryParser"):
        male_name = byte_buffer.parse_string_property("MaleName")
        id1 = byte_buffer.parse_uint32_property("MaleDinoID1")
        id2 = byte_buffer.parse_uint32_property("MaleDinoID2")
        self.male = ArkDinoAncestor(male_name, id1, id2)

        female_name = byte_buffer.parse_string_property("FemaleName")
        id1 = byte_buffer.parse_uint32_property("FemaleDinoID1")
        id2 = byte_buffer.parse_uint32_property("FemaleDinoID2")
        self.female = ArkDinoAncestor(female_name, id1, id2)
        byte_buffer.validate_name("None")

    def __str__(self):
        return f"AncestorEntry:[M:{self.male}, F:{self.female}]"
