import re

class HeaderLocation:
    def __init__(self, loc_str: str):
        # Regex to match the pattern in the Part strings
        pattern = r"^(?P<map>\w+)_(?P<grid>\w+)_L(?P<l>-?\d+)_X(?P<x>-?\d+)_Y(?P<y>-?\d+)(?:_DL(?P<dl>[A-Fa-f0-9]+))?$"
        match = re.match(pattern, loc_str)
        
        if match:
            self.map = match.group("map")
            self.grid = match.group("grid")
            self.l = int(match.group("l"))
            self.x = int(match.group("x"))
            self.y = int(match.group("y"))
            self.dl = int(match.group("dl"), 16) if match.group("dl") else None
        elif loc_str == "BunkerSPZV":
            self.map = "BunkerSPZV"
            self.grid = "BunkerSPZV"
            self.l = 0
            self.x = 0
            self.y = 0
            self.dl = None
        else:
            raise ValueError("String format does not match expected pattern: " + loc_str)
        
    def __str__(self):
        return f"{self.map}_{self.grid}_L{self.l}_X{self.x}_Y{self.y}" + (f"_DL{self.dl:08X}" if self.dl is not None else "")