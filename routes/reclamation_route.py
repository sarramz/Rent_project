from fastapi import APIRouter, HTTPException, Depends
from models.reclamation import Reclamation, UpdateReclamationModel
from serializers.reclamation_serializer import DecodeReclamation, DecodeReclamations
from bson import ObjectId
from config.config import reclamation_collection, user_collection
from auth.auth import is_admin, get_current_user

reclamation_router = APIRouter()

@reclamation_router.post("/new/reclamation")
def create_reclamation(reclamation: Reclamation, current_user=Depends(get_current_user)):
    if not user_collection.find_one({"_id": ObjectId(reclamation.utilisateur_id)}):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    reclamation_data = reclamation.dict()
    result = reclamation_collection.insert_one(reclamation_data)
    return {"status": "ok", "message": "Réclamation créée", "_id": str(result.inserted_id)}

@reclamation_router.get("/user/reclamations/{utilisateur_id}")
def get_user_reclamations(utilisateur_id: str, current_user=Depends(get_current_user)):
    if not ObjectId.is_valid(utilisateur_id) or not user_collection.find_one({"_id": ObjectId(utilisateur_id)}):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user_reclamations = reclamation_collection.find({"utilisateur_id": utilisateur_id})
    return {"status": "ok", "data": DecodeReclamations(user_reclamations)}


@reclamation_router.get("/admin/reclamations", dependencies=[Depends(is_admin)])
def get_all_reclamations():
    reclamations = reclamation_collection.find()
    return {"status": "ok", "data": DecodeReclamations(reclamations)}

@reclamation_router.patch("/admin/update/reclamation/{reclamation_id}", dependencies=[Depends(is_admin)])
def update_reclamation_status(reclamation_id: str, update: UpdateReclamationModel):
    if not ObjectId.is_valid(reclamation_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de réclamation invalide")
    updated_reclamation = reclamation_collection.find_one_and_update(
        {"_id": ObjectId(reclamation_id)},
        {"$set": update.dict(exclude_unset=True)},
        return_document=True
    )
    if updated_reclamation:
        return {"status": "ok", "message": "Statut de la réclamation mis à jour"}
    raise HTTPException(status_code=404, detail="Réclamation non trouvée")
