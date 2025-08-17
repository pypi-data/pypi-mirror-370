def is_wild_tamed(dino) -> bool:
    owner_obj = (
        getattr(dino.cryopod.dino, "owner", None).object
        if getattr(dino, "is_cryopodded", False)
        else getattr(dino, "owner", None).object if getattr(dino, "owner", None) else None
    )

    if not owner_obj:
        return True  # No owner, we except its wild tamed

    return owner_obj.get_property_value("DinoAncestors", None) is None