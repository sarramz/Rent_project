from fastapi import APIRouter, HTTPException
from models.reservation import Reservation, UpdateReservationModel
from serializers.reservation_serializer import DecodeReservations, DecodeReservation
from config.config import reservation_collection, property_collection, user_collection
from bson import ObjectId

reservation_router = APIRouter()

# Créer une nouvelle réservation
@reservation_router.post("/new/reservation")
def NewReservation(doc: Reservation):
    # Vérifier que l'appartement et l'utilisateur existent
    if not property_collection.find_one({"_id": ObjectId(doc.idApp)}):
        raise HTTPException(status_code=404, detail="Appartement not found")
    if not user_collection.find_one({"_id": ObjectId(doc.idU)}):
        raise HTTPException(status_code=404, detail="Utilisateur not found")

    # Insérer la réservation
    res = reservation_collection.insert_one(doc.dict())
    doc_id = str(res.inserted_id)

    return {
        "status": "ok",
        "message": "Reservation posted successfully",
        "_id": doc_id
    }

# Obtenir toutes les réservations
@reservation_router.get("/all/reservations")
def AllReservations():
    res = reservation_collection.find()
    decoded_data = DecodeReservations(res)
    return {
        "status": "ok",
        "data": decoded_data
    }

# Obtenir une réservation par ID
@reservation_router.get("/reservation/{_id}")
def GetReservation(_id: str):
    res = reservation_collection.find_one({"_id": ObjectId(_id)})
    if res:
        decoded_reservation = DecodeReservation(res)
        return {
            "status": "ok",
            "data": decoded_reservation
        }
    else:
        raise HTTPException(status_code=404, detail="Reservation not found")

# Mettre à jour une réservation
@reservation_router.patch("/update/{_id}")
def UpdateReservation(_id: str, doc: UpdateReservationModel):
    req = dict(doc.dict(exclude_unset=True))
    result = reservation_collection.find_one_and_update(
        {"_id": ObjectId(_id)},
        {"$set": req}
    )
    if result:
        return {
            "status": "ok",
            "message": "Reservation updated successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Reservation not found")

# Supprimer une réservation
@reservation_router.delete("/delete/{_id}")
def DeleteReservation(_id: str):
    result = reservation_collection.find_one_and_delete(
        {"_id": ObjectId(_id)}
    )
    if result:
        return {
            "status": "ok",
            "message": "Reservation deleted successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Reservation not found")
