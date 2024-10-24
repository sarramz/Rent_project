# Un seul document
def DecodeProperty(doc) -> dict:
    return {
        "_id": str(doc["_id"]),
        "prix": doc.get("prix", 0.0),
        "description": doc.get("description", ""),
        "adresse": doc.get("adresse", ""),
        "ville": doc.get("ville", ""),
        "région": doc.get("région", ""),  # Utilisation de .get pour éviter KeyError
        "nbr_chambres": doc.get("nbr_chambres", 0),
        "statut": doc.get("statut", ""),
        "image": doc.get("image", None)
    }
# Plusieurs documents
def DecodeProperties(docs) -> list:
    return [DecodeProperty(doc) for doc in docs]
