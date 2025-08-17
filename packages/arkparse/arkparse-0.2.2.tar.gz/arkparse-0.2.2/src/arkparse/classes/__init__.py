from .consumables import Consumables
from .placed_structures import PlacedStructures
from .dinos import Dinos
from .resources import Resources
from .player import Player
from .equipment import Equipment

class Structures:
    placed : PlacedStructures = PlacedStructures()

    all_bps = placed.all_bps

class Classes:
    consumables: Consumables = Consumables()
    structures: Structures = Structures()
    dinos: Dinos = Dinos()
    resources: Resources = Resources()
    player: Player = Player()
    equipment: Equipment = Equipment()

    all_bps = consumables.all_bps + structures.all_bps + dinos.all_bps + resources.all_bps + player.all_bps + equipment.all_bps