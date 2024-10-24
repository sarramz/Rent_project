from fastapi import APIRouter, HTTPException
from models.property import Property, UpdatePropertyModel
from serializers.property_serializer import DecodeProperties, DecodeProperty
from bson import ObjectId
from config.config import property_collection
entry_root = APIRouter()

# Créer une nouvelle propriété
@entry_root.post("/new/property")
def NewProperty(doc: Property):
    doc = dict(doc)
    res = property_collection.insert_one(doc)

    doc_id = str(res.inserted_id)

    return {
        "status": "ok",
        "message": "Property posted successfully",
        "_id": doc_id
    }

# Obtenir toutes les propriétés
@entry_root.get("/all/properties")
def AllProperties():
    res = property_collection.find()
    decoded_data = DecodeProperties(res)

    return {
        "status": "ok",
        "data": decoded_data
    }

# Obtenir une propriété par ID
@entry_root.get("/property/{_id}")
def GetProperty(_id: str):
    res = property_collection.find_one({"_id": ObjectId(_id)})
    if res:
        decoded_property = DecodeProperty(res)
        return {
            "status": "ok",
            "data": decoded_property
        }
    else:
        raise HTTPException(status_code=404, detail="Property not found")

# Mettre à jour une propriété
@entry_root.patch("/update/{_id}")
def UpdateProperty(_id: str, doc: UpdatePropertyModel):
    req = dict(doc.dict(exclude_unset=True))
    result = property_collection.find_one_and_update(
        {"_id": ObjectId(_id)},
        {"$set": req}
    )
    if result:
        return {
            "status": "ok",
            "message": "Property updated successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Property not found")

# Supprimer une propriété
@entry_root.delete("/delete/{_id}")
def DeleteProperty(_id: str):
    result = property_collection.find_one_and_delete(
        {"_id": ObjectId(_id)}
    )
    if result:
        return {
            "status": "ok",
            "message": "Property deleted successfully"
        }
    else:
        raise HTTPException(status_code=404, detail="Property not found")
