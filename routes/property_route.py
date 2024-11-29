from fastapi import APIRouter, HTTPException, Depends
from models.property import Property, UpdatePropertyModel
from serializers.property_serializer import decode_property, decode_properties
from bson import ObjectId
from config.config import property_collection
from auth.auth import is_proprietaire, is_admin, get_current_user

property_router = APIRouter()


@property_router.post("/properties", response_model=dict)
async def create_property(
    property: Property,
    current_user: dict = Depends(is_proprietaire)
):
    property_data = property.dict()
    property_data["proprietaire_id"] = str(current_user["_id"])  # Assign the owner
    result = property_collection.insert_one(property_data)
    return {"status": "ok", "message": "Propriété ajoutée avec succès", "_id": str(result.inserted_id)}


@property_router.get("/properties", response_model=dict)
async def get_all_properties():
    properties = property_collection.find()
    return {"status": "ok", "data": decode_properties(properties)}


@property_router.get("/properties/{property_id}", response_model=dict)
async def get_property(property_id: str):
    property_ = property_collection.find_one({"_id": ObjectId(property_id)})
    if not property_:
        raise HTTPException(status_code=404, detail="Propriété introuvable")
    return {"status": "ok", "data": decode_property(property_)}


@property_router.patch("/properties/{property_id}", response_model=dict)
async def update_property(
    property_id: str,
    property: UpdatePropertyModel,
    current_user: dict = Depends(get_current_user)
):
    existing_property = property_collection.find_one({"_id": ObjectId(property_id)})

    if not existing_property:
        raise HTTPException(status_code=404, detail="Propriété introuvable")

    # Only allow updates by the owner or an admin
    if (
        current_user["role"] != "admin"
        and str(current_user["_id"]) != existing_property["proprietaire_id"]
    ):
        raise HTTPException(
            status_code=403, detail="Accès interdit : Vous n'êtes pas le propriétaire"
        )

    update_data = property.dict(exclude_unset=True)
    property_collection.update_one({"_id": ObjectId(property_id)}, {"$set": update_data})
    return {"status": "ok", "message": "Propriété mise à jour avec succès"}


@property_router.delete("/properties/{property_id}", response_model=dict)
async def delete_property(
    property_id: str,
    current_user: dict = Depends(get_current_user)
):
    property_ = property_collection.find_one({"_id": ObjectId(property_id)})

    if not property_:
        raise HTTPException(status_code=404, detail="Propriété introuvable")

    # Only allow deletion by the owner or an admin
    if (
        current_user["role"] != "admin"
        and str(current_user["_id"]) != property_["proprietaire_id"]
    ):
        raise HTTPException(
            status_code=403, detail="Accès interdit : Vous n'êtes pas le propriétaire"
        )

    property_collection.delete_one({"_id": ObjectId(property_id)})
    return {"status": "ok", "message": "Propriété supprimée avec succès"}

