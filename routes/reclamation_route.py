from fastapi import APIRouter, HTTPException, Depends
from models.reclamation import Reclamation, UpdateReclamationModel
from serializers.reclamation_serializer import DecodeReclamation, DecodeReclamations
from bson import ObjectId
from config.config import reclamation_collection,user_collection


reclamation_router = APIRouter()

# Créer une réclamation (Utilisateur)
@reclamation_router.post("/new/reclamation")
def create_reclamation(reclamation: Reclamation):
    # Vérifie que l'utilisateur existe
    if not user_collection.find_one({"_id": ObjectId(reclamation.utilisateur_id)}):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Insère la réclamation
    reclamation_data = reclamation.dict()
    result = reclamation_collection.insert_one(reclamation_data)
    reclamation_id = str(result.inserted_id)
    return {"status": "ok", "message": "Réclamation créée", "_id": reclamation_id}

# Consulter les réclamations d'un utilisateur
@reclamation_router.get("/user/reclamations/{utilisateur_id}")
def get_user_reclamations(utilisateur_id: str):
    # Vérifie si l'utilisateur existe
    if not ObjectId.is_valid(utilisateur_id) or not user_collection.find_one({"_id": ObjectId(utilisateur_id)}):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Récupère les réclamations de l'utilisateur
    user_reclamations = reclamation_collection.find({"utilisateur_id": utilisateur_id})
    return {"status": "ok", "data": DecodeReclamations(user_reclamations)}

# Consulter toutes les réclamations (Administrateur)
@reclamation_router.get("/admin/reclamations")
def get_all_reclamations():
    reclamations = reclamation_collection.find()
    return {"status": "ok", "data": DecodeReclamations(reclamations)}

# Mettre à jour le statut d'une réclamation (Administrateur)
@reclamation_router.patch("/admin/update/reclamation/{reclamation_id}")
def update_reclamation_status(reclamation_id: str, update: UpdateReclamationModel):
    if not ObjectId.is_valid(reclamation_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de réclamation invalide")

    # Mise à jour du statut de la réclamation
    update_data = update.dict(exclude_unset=True)
    updated_reclamation = reclamation_collection.find_one_and_update(
        {"_id": ObjectId(reclamation_id)},
        {"$set": update_data},
        return_document=True
    )
    if updated_reclamation:
        return {"status": "ok", "message": "Statut de la réclamation mis à jour"}
    raise HTTPException(status_code=404, detail="Réclamation non trouvée")
