from typing import Set, Any
from dataclasses import dataclass

@dataclass
class ArkSet:
    value_type: Any
    values: Set[Any]