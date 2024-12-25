from fastapi import APIRouter, HTTPException, Depends, Query
from models.reservation import Reservation, UpdateReservation
from config.config import reservation_collection, property_collection
from serializers.reservation_serializer import DecodeReservation, DecodeReservations
from bson import ObjectId, errors
from auth.auth import get_current_user, is_locataire
from datetime import datetime
import logging

# Initialisation du routeur
reservation_router = APIRouter()

# Activation logs
#logging.basicConfig(level=logging.DEBUG)

@reservation_router.post("/add/{property_id}", response_model=dict)
async def create_reservation(
    new_reservation: Reservation,
    property_id: str,
    current_user: dict = Depends(is_locataire)
):
    try:
        #print(property_id)
        property_id = ObjectId(property_id)
    except errors.InvalidId:
        #logging.error(f"ID de propriété invalide: {property_id}")
        raise HTTPException(status_code=400, detail="ID propriété invalide.")
    
    if new_reservation.date_debut >= new_reservation.date_fin:
        #logging.error(f"Date de début après date de fin: {new_reservation.date_debut} >= {new_reservation.date_fin}")
        raise HTTPException(status_code=400, detail="La date de début doit être avant la date de fin.")
    
    try:
        property_ = await property_collection.find_one({"_id": property_id})
        if not property_:
            #logging.error(f"Propriété non trouvée pour l'ID: {property_id}")
            raise HTTPException(status_code=404, detail="Propriété non trouvée.")
        if property_.get("statut") != "disponible":
            #logging.error(f"Propriété avec ID {property_id} non disponible à la réservation.")
            raise HTTPException(status_code=400, detail="Propriété non disponible à la réservation.")
    except Exception as e:
        #logging.error(f"Erreur lors de la récupération de la propriété: {e}")
        print(e)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")
    
    reservation_data = new_reservation.dict()
    reservation_data.update({
        "idApp": str(property_id),  
        "idU": str(current_user["id"]),
        "statut": "En attente", 
        "date_res": datetime.utcnow(),  
    })
    
    try:
        result = await reservation_collection.insert_one(reservation_data)
        #logging.info(f"Réservation ajoutée avec succès avec l'ID: {result.inserted_id}")
        await property_collection.update_one({"_id": property_id}, {"$set": {"statut": "indisponible"}})
    except Exception as e:
        #logging.error(f"Erreur lors de l'insertion de la réservation: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'insertion de la réservation.")
    
    reservation = await reservation_collection.find_one({"_id": result.inserted_id})
    return {
        "status": "success",
        "data": DecodeReservation(reservation)
    }

@reservation_router.get("/all", response_model=dict)
async def get_all_reservations(current_user: dict = Depends(get_current_user)):
    """
    Récupérer toutes les réservations selon le rôle de l'utilisateur.
    """
    roles = current_user.get("roles", [])
    user_id = str(current_user["id"])  # ID utilisateur (locataire/propriétaire/admin)
    reservations = []

    if "admin" in roles:
        reservations_cursor = reservation_collection.find()
        reservations = await reservations_cursor.to_list(None)

    if "proprietaire" in roles:
        properties = await property_collection.find({"proprietaire_id": user_id}).to_list(None)
        property_ids = [str(p["_id"]) for p in properties]
        owner_reservations_cursor = reservation_collection.find({"idApp": {"$in": property_ids}})
        owner_reservations = await owner_reservations_cursor.to_list(None)
        reservations.extend(owner_reservations)

    if "locataire" in roles:
        renter_reservations_cursor = reservation_collection.find({"idU": user_id})
        renter_reservations = await renter_reservations_cursor.to_list(None)
        reservations.extend(renter_reservations)

    unique_reservations = {str(res["_id"]): res for res in reservations}.values()

    if not unique_reservations:
        return {"status": "success", "message": "Aucune réservation trouvée."}

    return {
        "status": "success",
        "data": DecodeReservations(list(unique_reservations)),
    }



@reservation_router.get("/get/{reservation_id}", response_model=dict)
async def get_reservation(
    reservation_id: str, 
    current_user: dict = Depends(get_current_user)):
    """
    Récupérer une réservation spécifique en fonction des rôles.
    """
    try:
        reservation_id = ObjectId(reservation_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID de réservation invalide.")

    reservation = await reservation_collection.find_one({"_id": reservation_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    user_id = str(current_user["id"])
    roles = current_user.get("roles", [])

    if "admin" in roles:
        pass
    elif "locataire" in roles and reservation["idU"] == user_id:
        pass
    elif "proprietaire" in roles:
        property_ = await property_collection.find_one(
            {"_id": ObjectId(reservation["idApp"]), "proprietaire_id": user_id}
        )
        if not property_:
            raise HTTPException(status_code=403, detail="Accès refusé, propriétaire non autorisé.")
    else:
        raise HTTPException(status_code=403, detail="Accès refusé, rôle non autorisé.")

    return {"status": "success", "data": DecodeReservation(reservation)}



@reservation_router.patch("/{reservation_id}/status", response_model=dict)
async def update_reservation_status(
    reservation_id: str,  
    body: UpdateReservation, 
    current_user: dict = Depends(get_current_user)
):
    """
    Mettre à jour le statut d'une réservation. Seul le propriétaire de l'appartement lié peut le faire.
    """
    try:
        reservation_id = ObjectId(reservation_id)
    except errors.InvalidId:
        raise HTTPException(400, "ID de réservation invalide.")

    reservation = await reservation_collection.find_one({"_id": reservation_id})
    if not reservation:
        raise HTTPException(404, "Réservation introuvable.")

    appartement = await property_collection.find_one({"_id": ObjectId(reservation["idApp"])})

    if not appartement:
        raise HTTPException(404, "Appartement introuvable.")

    if str(appartement["proprietaire_id"]) != str(current_user["id"]):
        raise HTTPException(403, "Seul le propriétaire peut modifier le statut de cette réservation.")

    if not body.new_status:
        raise HTTPException(400, "Le champ 'new_status' est requis.")
    
    await reservation_collection.update_one(
        {"_id": reservation_id},
        {"$set": {"statut": body.new_status.value, "updated_at": datetime.utcnow()}}
    )

    updated_reservation = await reservation_collection.find_one({"_id": reservation_id})

    return {
        "status": "success",
        "message": "Statut de réservation mis à jour.",
        "data": {
            "id": str(updated_reservation["_id"]),
            "idApp": updated_reservation["idApp"],
            "statut": updated_reservation["statut"],
            "updated_at": updated_reservation["updated_at"]
        }
    }

@reservation_router.delete("/{reservation_id}", response_model=dict)
async def delete_reservation(
    reservation_id: str,
    current_user: dict = Depends(get_current_user) 
):
    """
    Supprimer une réservation existante.
    Seuls l'administrateur ou l'utilisateur ayant fait la réservation peuvent la supprimer.
    """
 
    try:
        reservation_id = ObjectId(reservation_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID de réservation invalide.")

  
    reservation = await reservation_collection.find_one({"_id": reservation_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable.")

    if (
        "admin" not in current_user.get("roles", [])  # Si l'utilisateur n'est pas admin
        and str(reservation["idU"]) != str(current_user["id"])  # Et qu'il n'est pas celui qui a fait la réservation
    ):
        raise HTTPException(
            status_code=403, detail="Accès interdit : vous ne pouvez pas supprimer cette réservation."
        )

    # Supprimer la réservation
    await reservation_collection.delete_one({"_id": reservation_id})

    # Mettre à jour l'état de la propriété associée (si applicable)
    if "idApp" in reservation:
        await property_collection.update_one(
            {"_id": ObjectId(reservation["idApp"])},
            {"$set": {"statut": "disponible"}}
        )

    # Retourner une réponse réussie
    return {
        "status": "success",
        "message": "Réservation supprimée avec succès."
    }

