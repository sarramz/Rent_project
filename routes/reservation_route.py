from fastapi import APIRouter, HTTPException, Depends
from models.reservation import Reservation, UpdateReservation
from config.config import reservation_collection, property_collection, user_collection
from serializers.reservation_serializer import DecodeReservation
from bson import ObjectId
from auth.auth import get_current_user
from datetime import datetime

reservation_router = APIRouter()

@reservation_router.post("/add", response_model=dict)
async def create_reservation(
    new_reservation: Reservation, current_user: dict = Depends(get_current_user)
):
    """
    Créer une nouvelle réservation.
    Accessible uniquement pour les locataires.
    Vérifie l'existence de la propriété et la disponibilité pour les dates choisies.
    """
    # Vérification du rôle de l'utilisateur
    if current_user.get("role") != "locataire":
        raise HTTPException(
            status_code=403, detail="Seuls les locataires peuvent créer des réservations."
        )

    # Vérification de l'existence de la propriété
    property_exists = await property_collection.find_one({"_id": ObjectId(new_reservation.idApp)})
    if not property_exists:
        raise HTTPException(status_code=404, detail="Propriété introuvable.")

    # Validation des dates
    if new_reservation.date_debut >= new_reservation.date_fin:
        raise HTTPException(
            status_code=400, detail="La date de début doit être antérieure à la date de fin."
        )

    # Vérification de la disponibilité
    overlapping_reservations = await reservation_collection.find_one(
        {
            "idApp": new_reservation.idApp,
            "$or": [
                {"date_debut": {"$lt": new_reservation.date_fin, "$gte": new_reservation.date_debut}},
                {"date_fin": {"$lte": new_reservation.date_fin, "$gt": new_reservation.date_debut}},
            ],
        }
    )
    if overlapping_reservations:
        raise HTTPException(
            status_code=400, detail="La propriété n'est pas disponible pour les dates sélectionnées."
        )

    # Création de la réservation
    reservation_dict = new_reservation.dict()
    reservation_dict["idU"] = str(current_user["_id"])
    result = await reservation_collection.insert_one(reservation_dict)

    new_reservation_data = await reservation_collection.find_one({"_id": result.inserted_id})
    return {"status": "success", "data": DecodeReservation(new_reservation_data)}


@reservation_router.get("/{reservation_id}", response_model=dict)
async def get_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    """
    Récupérer une réservation spécifique.
    Accessible au locataire ou au propriétaire lié à la réservation.
    """
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    # Vérification des permissions
    is_owner = reservation["idU"] == str(current_user["_id"])
    is_property_owner = await property_collection.find_one(
        {"_id": ObjectId(reservation["idApp"]), "proprietaire_id": str(current_user["_id"])}
    )
    if not (is_owner or is_property_owner or current_user.get("role") == "admin"):
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à consulter cette réservation.",
        )

    return {"status": "success", "data": DecodeReservation(reservation)}


@reservation_router.put("/{reservation_id}", response_model=dict)
async def update_reservation(
    reservation_id: str,
    update_data: UpdateReservation,
    current_user: dict = Depends(get_current_user),
):
    """
    Mettre à jour une réservation existante.
    Accessible au locataire ou à l'administrateur.
    """
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    # Vérification des permissions
    if reservation["idU"] != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit à cette réservation.")

    # Mise à jour des champs
    update_fields = update_data.dict(exclude_unset=True)
    await reservation_collection.update_one(
        {"_id": ObjectId(reservation_id)}, {"$set": update_fields}
    )

    updated_reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    return {"status": "success", "data": DecodeReservation(updated_reservation)}


@reservation_router.delete("/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    """
    Supprimer une réservation existante.
    Accessible au locataire ou à l'administrateur.
    """
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    # Vérification des permissions
    if reservation["idU"] != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès interdit à cette réservation.")

    # Suppression
    await reservation_collection.delete_one({"_id": ObjectId(reservation_id)})

    return {"status": "success", "message": "Réservation supprimée avec succès."}
