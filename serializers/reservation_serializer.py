from datetime import datetime
from bson import ObjectId

def DecodeReservation(reservation: dict) -> dict:
    return {
        "id": str(reservation["_id"]) if isinstance(reservation["_id"], ObjectId) else reservation["_id"],
        "idApp": reservation.get("idApp"),  # ID de la propriété
        "idU": reservation.get("idU"),  # ID de l'utilisateur
        "date_debut": reservation.get("date_debut").isoformat() if isinstance(reservation.get("date_debut"), datetime) else reservation.get("date_debut"),
        "date_fin": reservation.get("date_fin").isoformat() if isinstance(reservation.get("date_fin"), datetime) else reservation.get("date_fin"),
        "statut": reservation.get("statut", "En attente"),  # Valeur par défaut
        "date_res": reservation.get("date_res").isoformat() if isinstance(reservation.get("date_res"), datetime) else reservation.get("date_res", datetime.utcnow().isoformat()),
    }

def DecodeReservations(reservations: list) -> list:
    return [DecodeReservation(reservation) for reservation in reservations]
