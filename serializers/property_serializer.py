def decode_property(property: dict) -> dict:
    """Convertir un document MongoDB en dictionnaire sérialisable."""
    return {
        "_id": str(property.get("_id", "")),
        "titre": property.get("titre", ""),
        "description": property.get("description", ""),
        "adresse": property.get("adresse", ""),
        "ville": property.get("ville", ""),
        "région": property.get("région", ""),
        "prix": property.get("prix", 0.0),
        "superficie": property.get("superficie", 0.0),
        "nbr_chambres": property.get("nbr_chambres", 0),
        "statut": property.get("statut", "disponible"),
        "disponibilite": property.get("disponibilite", True),
        "date_ajout": property.get("date_ajout", "").isoformat() if "date_ajout" in property else None,
        "image": property.get("image", None),
        "proprietaire_id": property.get("proprietaire_id", ""),
    }

def decode_properties(properties: list) -> list:
    """Convertir une liste de documents MongoDB en dictionnaires sérialisables."""
    return [decode_property(property) for property in properties]
