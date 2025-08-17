from typing import List, Dict
from arkparse.parsing.struct import ArkLinearColor
from arkparse.parsing import ArkPropertyContainer
from dataclasses import dataclass

@dataclass
class ArkCharacterConfig:
    is_female: bool
    body_colors: List[ArkLinearColor]
    head_hair_index: int
    eyebrow_index: int
    hair_growth: float
    facial_hair_growth: float
    bone_modifiers: List[float]  # TODO - find out which slider is what
    dyn_material_values: List[int] # TODO - find out what these are
    voice: int
    spawn_region: int

    def __init__(self, properties: ArkPropertyContainer):

        facial_growth = properties.find_property("PercentageOfFacialHairGrowth")
        if not facial_growth:
            self.facial_hair_growth = 0.0
        else:
            # raise ValueError("Missing 'PercentageOfFacialHairGrowth' property.")
            self.facial_hair_growth = (
                facial_growth.value
                if facial_growth.type == "Float"
                else 0.0
            )
        
        properties = properties.get_property_value("MyPlayerCharacterConfig")
        # Parse is_female
        is_female_prop = properties.find_property("bIsFemale")
        if not is_female_prop:
            self.is_female = False
            # raise ValueError("Missing 'bIsFemale' property.")
        else:
            self.is_female = (
                is_female_prop.value
                if is_female_prop.type == "Boolean"
                else False
            )

        # Parse BodyColors
        body_colors_props = properties.find_all_properties_of_name("BodyColors")
        # Sort by position to maintain order
        body_colors_props_sorted = sorted(body_colors_props, key=lambda p: p.position)
        self.body_colors = []
        for prop in body_colors_props_sorted:
            if prop.type != "Struct" or not isinstance(prop.value, ArkLinearColor):
                continue
            self.body_colors.append(prop.value)

        # Parse head_hair_index
        head_hair_props = properties.find_property("HeadHairIndex")
        self.head_hair_index = 0
        if head_hair_props:
            self.head_hair_index = (
                head_hair_props.value
                if head_hair_props.type in ["Byte", "Int"]
                else 0
            )

        # Parse eyebrow_index
        eyebrow_props = properties.find_property("EyebrowIndex")
        if not eyebrow_props:
            self.eyebrow_index = 0
            # raise ValueError("Missing 'eyebrow_index' property.")
        else:
            self.eyebrow_index = (
                eyebrow_props.value
                if eyebrow_props.type in ["Byte", "Int"]
                else 0
            )

        # Parse hair_growth
        self.hair_growth = properties.get_property_value("PercentOfFullHeadHairGrowth", 0.0)

        # Parse bone_modifiers
        bone_modifiers_props = properties.find_all_properties_of_name("RawBoneModifiers")
        # Sort by position to maintain order
        bone_modifiers_props_sorted = sorted(bone_modifiers_props, key=lambda p: p.position)
        self.bone_modifiers = [
            prop.value for prop in bone_modifiers_props_sorted if prop.type == "Float"
        ]

        # Parse dyn_material_values
        dynamic_material_props = properties.find_all_properties_of_name("DynamicMaterialBytes")
        # Sort by position to maintain order
        dynamic_material_props_sorted = sorted(dynamic_material_props, key=lambda p: p.position)
        self.dyn_material_values = [
            prop.value for prop in dynamic_material_props_sorted if prop.type == "Byte"
        ]

        # Parse voice
        voice_id_props = properties.find_property("PlayerVoiceCollectionIndex")
        if not voice_id_props:
            raise ValueError("Missing 'PlayerVoiceCollectionIndex' property.")
        self.voice = (
            voice_id_props.value
            if voice_id_props.type == "Int"
            else 0
        )

        # Parse spawn_region
        spawn_region_props = properties.find_property("PlayerSpawnRegionIndex")
        if not spawn_region_props:
            self.spawn_region = 0
        else:
            # raise ValueError("Missing 'Playerspawn_regionIndex' property.")
            self.spawn_region = (
                spawn_region_props.value
                if spawn_region_props.type == "Int"
                else 0
            )

    def __str__(self):
        # Build a comprehensive, compact string representation
        parts = [
            "ArkCharacterConfig:",
            f"  Is Female: {self.is_female}",
            f"  Head Hair Index: {self.head_hair_index}",
            f"  Eyebrow Index: {self.eyebrow_index}",
            f"  Hair Growth Percent: {(self.hair_growth * 100):.2f}%",
            f"  Facial Hair Growth Percent: {(self.facial_hair_growth * 100):.2f}%",
            f"  Voice ID: {self.voice}",
            f"  Spawn Region: {self.spawn_region}",
            f"  Body Colors: [{', '.join(str(color) for color in self.body_colors)}]",
            f"  Bone Modifiers: [{', '.join(f'{modifier:.2f}' for modifier in self.bone_modifiers)}]",
            f"  Dynamic Material Values: [{', '.join(str(value) for value in self.dyn_material_values)}]"
        ]
        return "\n".join(parts)

