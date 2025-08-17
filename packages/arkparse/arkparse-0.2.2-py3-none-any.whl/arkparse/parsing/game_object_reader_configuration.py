from dataclasses import dataclass
from typing import Optional, Callable
from uuid import UUID


@dataclass
class GameObjectReaderConfiguration:
    uuid_filter: Optional[Callable[[UUID], bool]] = None
    blueprint_name_filter: Optional[Callable[[Optional[str]], bool]] = None
