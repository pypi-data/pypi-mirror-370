from dataclasses import dataclass
from typing import TYPE_CHECKING
from arkparse.logging import ArkSaveLogger
from .ark_vector import ArkVector

if TYPE_CHECKING:   
    from arkparse.parsing import ArkBinaryParser

@dataclass
class ArkPlayerDeathReason:
    player_id: int = 0
    reason: str = ""
    time: float = 0.0
    location: ArkVector = None


    def __init__(self, ark_binary_data: "ArkBinaryParser"):
        self.player_id = ark_binary_data.parse_int32_property("PlayerID")
        self.reason = ark_binary_data.parse_string_property("DeathReason")
        self.time = ark_binary_data.parse_double_property("DiedAtTime")
        ark_binary_data.validate_name("DeathLocation")
        self.location = ArkVector(ark_binary_data, from_struct=True)
        ark_binary_data.validate_name("None")

        ArkSaveLogger.parser_log(f"ArkPlayerDeathReason: {self.player_id}, {self.reason}, {self.time}, {self.location}")