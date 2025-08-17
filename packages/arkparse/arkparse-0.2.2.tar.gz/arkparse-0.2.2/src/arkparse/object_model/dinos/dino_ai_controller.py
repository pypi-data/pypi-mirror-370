from uuid import UUID

from arkparse.object_model.misc.__parsed_object_base import ParsedObjectBase
from arkparse.saves.asa_save import AsaSave


class DinoAiController(ParsedObjectBase):
    targeting_team: int

    def __init_props__(self):
        super().__init_props__()

        self.targeting_team = self.object.get_property_value("TargetingTeam")
    
    def __init__(self, uuid: UUID = None, save: AsaSave = None):
        super().__init__(uuid, save=save)
