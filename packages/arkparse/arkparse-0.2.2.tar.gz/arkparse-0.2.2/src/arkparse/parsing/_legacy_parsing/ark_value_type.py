from enum import Enum
from typing import Type, Optional, Any
from decimal import Decimal
from arkparse.enums.ark_enum import ArkEnumValue

#non-legacy imports
from arkparse.parsing.ark_set import ArkSet

class ArkValueType(Enum):
    Boolean = ("BoolProperty", bool)
    Byte = ("ByteProperty", int)
    Float = ("FloatProperty", float)
    Int = ("IntProperty", int)
    Enum = ("EnumProperty", ArkEnumValue)
    Name = ("NameProperty", str)
    Object = ("ObjectProperty", str)
    String = ("StrProperty", str)
    Struct = ("StructProperty", object)  # Placeholder for custom struct
    Array = ("ArrayProperty", list)
    Double = ("DoubleProperty", float)
    Int16 = ("Int16Property", int)  # Python's int serves for both Int16 and regular integers
    Int64 = ("Int64Property", int)
    Int8 = ("Int8Property", int)
    UInt16 = ("UInt16Property", int)
    UInt32 = ("UInt32Property", int)
    UInt64 = ("UInt64Property", Decimal)  # Use Decimal for very large unsigned integers
    SoftObject = ("SoftObjectProperty", str)
    Set = ("SetProperty", ArkSet)
    Map = ("MapProperty", "ArkProperty")  # Use a string annotation for ArkProperty to prevent circular imports

    def __init__(self, type_name: str, clazz: Type[Any]):
        self._type_name = type_name
        self._clazz = clazz

    @property
    def type_name(self) -> str:
        return self._type_name

    @classmethod
    def from_name(cls, name: str) -> Optional["ArkValueType"]:
        for item in cls:
            if item._type_name == name:
                return item
        return None

    def get_property_type(self) -> Type[Any]:
        return self._clazz
