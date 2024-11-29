def decode_property(property: dict) -> dict:
    """Convert a MongoDB property document into a serializable dictionary."""
    return {
        "_id": str(property["_id"]),
        "titre": property.get("titre", ""),
        "description": property.get("description", ""),
        "adresse": property.get("adresse", ""),
        "prix": property.get("prix", 0.0),
        "superficie": property.get("superficie", 0.0),
        "type_bien": property.get("type_bien", ""),
        "disponibilite": property.get("disponibilite", True),
        "date_ajout": property.get("date_ajout", ""),
        "image": property.get("image", None),
        "proprietaire_id": property.get("proprietaire_id", "")
    }


def decode_properties(properties) -> list:
    """Convert a list of MongoDB property documents into a list of serializable dictionaries."""
    return [decode_property(property) for property in properties]
