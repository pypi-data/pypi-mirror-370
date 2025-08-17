from arkparse.parsing import ArkPropertyContainer

class PersistentBuffData:
    class_: str
    name: str

    def __init__(self, properties: ArkPropertyContainer):
        self.class_ = properties.find_property("ForPrimalBuffClass").value.value
        self.name = properties.find_property("ForPrimalBuffClassString").value

    def __str__(self):
        return f"class={self.class_}, name={self.name}"