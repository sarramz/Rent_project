from fastapi import APIRouter, HTTPException, Depends
from models.reservation import Reservation, UpdateReservation
from config.config import reservation_collection, user_collection, property_collection
from serializers.reservation_serializer import DecodeReservation, DecodeReservations
from bson import ObjectId
from auth.auth import get_current_user

reservation_router = APIRouter()


@reservation_router.post("/reservations")
async def create_reservation(new_reservation: Reservation, current_user: dict = Depends(get_current_user)):
    property_exists = await property_collection.find_one({"_id": ObjectId(new_reservation.idApp)})
    if not property_exists:
        raise HTTPException(status_code=404, detail="Property not found")

    # Validation: Vérification de la disponibilité de la propriété
    overlapping_reservations = await reservation_collection.find_one({
        "idApp": new_reservation.idApp,
        "$or": [
            {"date_debut": {"$lt": new_reservation.date_fin, "$gte": new_reservation.date_debut}},
            {"date_fin": {"$lte": new_reservation.date_fin, "$gt": new_reservation.date_debut}}
        ]
    })
    if overlapping_reservations:
        raise HTTPException(status_code=400, detail="Property is not available for the selected dates")

    reservation_dict = new_reservation.dict()
    reservation_dict["idU"] = str(current_user["_id"])
    result = await reservation_collection.insert_one(reservation_dict)
    new_reservation_data = await reservation_collection.find_one({"_id": result.inserted_id})
    return {"status": "success", "data": DecodeReservation(new_reservation_data)}


@reservation_router.get("/reservations")
async def get_all_reservations():
    reservations = DecodeReservations(await reservation_collection.find().to_list(length=100))
    return {"status": "success", "data": reservations}


@reservation_router.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation["idU"] != str(current_user["_id"]) and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this reservation")
    return {"status": "success", "data": DecodeReservation(reservation)}


@reservation_router.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: str, update_data: UpdateReservation, current_user: dict = Depends(get_current_user)):
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation["idU"] != str(current_user["_id"]) and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this reservation")
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items()}
    result = await reservation_collection.update_one({"_id": ObjectId(reservation_id)}, {"$set": update_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reservation not updated")
    updated_reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    return {"status": "success", "data": DecodeReservation(updated_reservation)}


@reservation_router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    reservation = await reservation_collection.find_one({"_id": ObjectId(reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation["idU"] != str(current_user["_id"]) and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this reservation")
    result = await reservation_collection.delete_one({"_id": ObjectId(reservation_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Failed to delete reservation")
    return {"status": "success", "message": "Reservation deleted successfully"}
