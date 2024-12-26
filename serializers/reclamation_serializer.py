from bson import ObjectId
from datetime import datetime


def DecodeReclamation(reclamation) -> dict:
    return {
        "_id": str(reclamation["_id"]),
        "utilisateur_id": str(reclamation.get("utilisateur_id", "")),
        "contenu": reclamation.get("contenu", ""),
        "date": reclamation.get("date").isoformat() if isinstance(reclamation.get("date"), datetime) else "",
        "statut": reclamation.get("statut", "En cours"),
    }


def DecodeReclamations(reclamations) -> list:
    return [DecodeReclamation(reclamation) for reclamation in reclamations]
