from fastapi import APIRouter, HTTPException, Depends
from models.reservation import Reservation, UpdateReservation
from config.config import reservation_collection, user_collection, property_collection
from serializers.reservation_serializer import DecodeReservation, DecodeReservations
from bson import ObjectId
from auth.auth import get_current_user
from datetime import datetime

# Création d'un routeur pour gérer les routes liées aux réservations
reservation_router = APIRouter()


@reservation_router.post("/reservations", response_model=dict)
async def create_reservation(new_reservation: Reservation, current_user: dict = Depends(get_current_user)):
    """
    Créer une nouvelle réservation.
    - Accessible uniquement aux locataires.
    - Vérifie l'existence de la propriété.
    - Valide la disponibilité de la propriété pour les dates sélectionnées.
    """

    # Vérification des droits : uniquement pour les locataires
    if current_user.get("role") != "locataire":
        raise HTTPException(status_code=403, detail="Accès réservé aux locataires uniquement")

    # Validation de l'existence de la propriété
    property_exists = await property_collection.find_one({"_id": ObjectId(new_reservation.idApp)})
    if not property_exists:
        raise HTTPException(status_code=404, detail="Propriété introuvable")

    # Validation des dates : La date de début doit précéder la date de fin
    if new_reservation.date_debut >= new_reservation.date_fin:
        raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")

    # Validation de la disponibilité de la propriété
    overlapping_reservations = await reservation_collection.find_one({
        "idApp": new_reservation.idApp,
        "$or": [
            {"date_debut": {"$lt": new_reservation.date_fin, "$gte": new_reservation.date_debut}},
            {"date_fin": {"$lte": new_reservation.date_fin, "$gt": new_reservation.date_debut}}
        ]
    })
    if overlapping_reservations:
        raise HTTPException(status_code=400, detail="La propriété n'est pas disponible pour les dates sélectionnées")

    # Création de la réservation
    reservation_dict = new_reservation.dict()
    reservation_dict["idU"] = str(current_user["_id"])
    result = await reservation_collection.insert_one(reservation_dict)

    # Retourne les détails de la réservation créée
    new_reservation_data = await reservation_collection.find_one({"_id": result.inserted_id})
    return {"status": "success", "data": DecodeReservation(new_reservation_data)}


@reservation_router.get("/reservations", response_model=dict)
async def get_all_reservations(current_user: dict = Depends(get_current_user)):
    """
    Récupérer toutes les réservations.
    - Les locataires ne peuvent voir que leurs propres réservations.
    - Les administrateurs peuvent voir toutes les réservations.
    """
    query = {}
    if current_user.get("role") == "locataire":
        query["idU"] = str(current_user["_id"])  # Filtre par utilisateur pour les locataires

    reservations = DecodeReservations(await reservation_collection.find(query).to_list(length=100))
    return {"status": "success", "data": reservations}


@reservation_router.get("/reservations/{reservation_id}", response_model=dict)
async def get_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    """
    Récupérer une réservation spécifique par ID.
    - Accessible uniquement au locataire qui a fait la réservation ou à un administrateur.
    """
    # Vérification de l'existence de la réservation
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    # Vérification des droits d'accès
    if reservation["idU"] != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à accéder à cette réservation")

    return {"status": "success", "data": DecodeReservation(reservation)}


@reservation_router.put("/reservations/{reservation_id}", response_model=dict)
async def update_reservation(reservation_id: str, update_data: UpdateReservation, current_user: dict = Depends(get_current_user)):
    """
    Mettre à jour une réservation existante.
    - Accessible uniquement au locataire ayant fait la réservation ou à un administrateur.
    - Valide les dates si elles sont modifiées.
    """
    # Validation de l'existence de la réservation
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    # Vérification des droits d'accès
    if reservation["idU"] != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à modifier cette réservation")

    # Validation des dates si elles sont modifiées
    if update_data.date_debut and update_data.date_fin:
        if update_data.date_debut >= update_data.date_fin:
            raise HTTPException(status_code=400, detail="La date de début doit être antérieure à la date de fin")

    # Mise à jour de la réservation
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items()}
    result = await reservation_collection.update_one({"_id": ObjectId(reservation_id)}, {"$set": update_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Aucune modification effectuée sur la réservation")

    updated_reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    return {"status": "success", "data": DecodeReservation(updated_reservation)}


@reservation_router.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    """
    Supprimer une réservation existante.
    - Accessible uniquement au locataire ayant fait la réservation ou à un administrateur.
    """
    # Vérification de l'existence de la réservation
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")

    # Vérification des droits d'accès
    if reservation["idU"] != str(current_user["_id"]) and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à supprimer cette réservation")

    # Suppression de la réservation
    result = await reservation_collection.delete_one({"_id": ObjectId(reservation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=400, detail="Échec de la suppression de la réservation")

    return {"status": "success", "message": "Réservation supprimée avec succès"}
