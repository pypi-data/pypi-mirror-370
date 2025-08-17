from typing import List
from pathlib import Path
from dataclasses import dataclass
from arkparse.parsing import ArkPropertyContainer
from arkparse.parsing.ark_archive import ArkArchive

@dataclass
class ArkTribe:
    _archive: ArkArchive
    properties: ArkPropertyContainer

    name: str
    owner_id: int
    tribe_id: int
    members: List[str]
    member_ids: List[int]
    tribe_log: List[str]
    log_index: int
    nr_of_dinos: int

    def __init__(self, file: Path, from_store: bool):
        self._archive = ArkArchive(file, from_store)

        self.properties = self._archive.get_object_by_class("/Script/ShooterGame.PrimalTribeData")
        if not self.properties:
            raise ValueError("Failed to find tribe data.")
        
        # Parse 'TribeData'
        tribe_data_prop = self.properties.find_property("TribeData")
        if not tribe_data_prop:
            raise ValueError("Missing 'TribeData' property.")
        if tribe_data_prop.type != "Struct":
            raise ValueError("'TribeData' property is not of type 'Struct'.")
        if not isinstance(tribe_data_prop.value, ArkPropertyContainer):
            raise ValueError("'TribeData' property value is not an ArkPropertyContainer.")

        tribe_data = tribe_data_prop.value

        # Parse 'TribeName' -> name
        name_prop = tribe_data.find_property("TribeName")
        if not name_prop:
            raise ValueError("Missing 'TribeName' property.")
        if name_prop.type != "String":
            raise ValueError("'TribeName' property is not of type 'String'.")
        self.name = name_prop.value

        # Parse 'OwnerPlayerDataId' -> owner_id
        owner_id_prop = tribe_data.find_property("OwnerPlayerDataId")
        if not owner_id_prop:
            raise ValueError("Missing 'OwnerPlayerDataId' property.")
        if owner_id_prop.type not in ["UInt32", "Int"]:
            raise ValueError("'OwnerPlayerDataId' property is not of type 'UInt32' or 'Int'.")
        self.owner_id = owner_id_prop.value

        # Parse 'TribeID' -> tribe_id
        tribe_id_prop = tribe_data.find_property("TribeID")
        if not tribe_id_prop:
            raise ValueError("Missing 'TribeID' property.")
        if tribe_id_prop.type != "Int":
            raise ValueError("'TribeID' property is not of type 'Int'.")
        self.tribe_id = tribe_id_prop.value

        # Parse 'MembersPlayerName' -> members
        members_prop = tribe_data.find_property("MembersPlayerName")
        if members_prop and members_prop.type == "Array":
            self.members = members_prop.value
        else:
            self.members = []

        # Parse 'MembersPlayerDataID' -> member_ids
        member_ids_prop = tribe_data.find_property("MembersPlayerDataID")
        if member_ids_prop and member_ids_prop.type == "Array":
            self.member_ids = member_ids_prop.value
        else:
            self.member_ids = []

        # Parse 'TribeLog' -> tribe_log
        tribe_log_prop = tribe_data.find_property("TribeLog")
        if tribe_log_prop and tribe_log_prop.type == "Array":
            self.tribe_log = tribe_log_prop.value
        else:
            self.tribe_log = []

        # Parse 'LogIndex' -> log_index
        log_index_prop = tribe_data.find_property("LogIndex")
        if not log_index_prop:
            self.log_index = 0
        else:
            if log_index_prop.type != "Int":
                raise ValueError("'LogIndex' property is not of type 'Int'.")
            self.log_index = log_index_prop.value

        # Parse 'NumTribeDinos' -> nr_of_dinos
        nr_of_dinos_prop = tribe_data.find_property("NumTribeDinos")
        if not nr_of_dinos_prop:
            # raise ValueError("Missing 'NumTribeDinos' property.")
            self.nr_of_dinos = 0
        else:
            if nr_of_dinos_prop.type != "Int":
                raise ValueError("'NumTribeDinos' property is not of type 'Int'.")
            self.nr_of_dinos = nr_of_dinos_prop.value

    def __str__(self):
        return f"Tribe: \'{self.name}\' with {len(self.members)} members (id: {self.tribe_id})"

    def to_string_all(self):
        parts = [
            "ArkTribeData:",
            f"  Tribe Name: {self.name}",
            f"  Owner Player Data ID: {self.owner_id}",
            f"  Tribe ID: {self.tribe_id}",
            f"  Members Player Names: {self.members}",
            f"  Members Player Data IDs: {self.member_ids}",
            f"  Tribe Log: {len(self.tribe_log)} entries",
            f"  Log Index: {self.log_index}",
            f"  Number of Tribe Dinos: {self.nr_of_dinos}"
        ]

        return "\n".join(parts)
    
    def print_tribe_log(self):
        print(f"Tribe Log for {self.name}:")
        for entry in self.tribe_log:
            print('    - ' + entry)