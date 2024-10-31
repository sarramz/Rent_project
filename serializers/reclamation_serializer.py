def DecodeReclamation(reclamation) -> dict:
    return {
        "_id": str(reclamation["_id"]),
        "utilisateur_id": str(reclamation["utilisateur_id"]),
        "contenu": reclamation.get("contenu"),
        "date": reclamation.get("date"),
        "statut": reclamation.get("statut", "En cours")
    }

def DecodeReclamations(reclamations) -> list:
    return [DecodeReclamation(reclamation) for reclamation in reclamations]
