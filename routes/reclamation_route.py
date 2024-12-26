from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId, errors
from datetime import datetime
from models.reclamation import Reclamation, UpdateReclamationModel
from serializers.reclamation_serializer import DecodeReclamation, DecodeReclamations
from config.config import reclamation_collection, user_collection
from auth.auth import get_current_user, is_admin

reclamation_router = APIRouter()

@reclamation_router.post("/add", response_model=dict)
async def create_reclamation(
    reclamation: Reclamation,
    current_user: dict = Depends(get_current_user),
):
    """
    Créer une réclamation. Accessible uniquement aux locataires et propriétaires.
    """
    user_roles = current_user.get("roles", [])
    if "locataire" not in user_roles and "proprietaire" not in user_roles:
        raise HTTPException(
            status_code=403,
            detail="Seuls les locataires ou propriétaires peuvent créer une réclamation."
        )

    # Préparation des données de la réclamation
    reclamation_data = {
        "utilisateur_id": str(current_user["id"]),  # ID de l'utilisateur connecté
        "contenu": reclamation.contenu,
        "date": datetime.utcnow(),  # Date automatique
        "statut": "En cours",       # Statut par défaut
    }

    # Insertion dans la base de données
    result = await reclamation_collection.insert_one(reclamation_data)

    return {
        "status": "ok",
        "message": "Réclamation créée avec succès",
        "_id": str(result.inserted_id),
    }


@reclamation_router.get("/myreclamations", response_model=dict)
async def get_my_reclamations(current_user: dict = Depends(get_current_user)):
    """
    Récupérer toutes les réclamations de l'utilisateur connecté.

    Args:
        current_user (dict): Informations sur l'utilisateur connecté.

    Returns:
        dict: Liste des réclamations de l'utilisateur.
    """
    user_reclamations = await reclamation_collection.find({"utilisateur_id": str(current_user["id"])}).to_list(length=None)

    if not user_reclamations:
        return {"status": "ok", "message": "Aucune réclamation trouvée pour cet utilisateur.", "data": []}

    return {"status": "ok", "data": DecodeReclamations(user_reclamations)}


@reclamation_router.get("/all", response_model=dict)
async def get_all_reclamations(current_user: dict = Depends(is_admin)):
    """
    Récupérer toutes les réclamations. Accessible uniquement à l'administrateur.
    """
    all_reclamations = await reclamation_collection.find().to_list(length=None)
    return {"status": "ok", "data": DecodeReclamations(all_reclamations)}



@reclamation_router.patch("/update/{reclamation_id}", response_model=dict)
async def update_reclamation(
    reclamation_id: str,
    update_data: UpdateReclamationModel,
    current_user: dict = Depends(is_admin),
):
    """
    Modifier le statut d'une réclamation. Accessible uniquement à l'administrateur.
    """
    try:
        reclamation_id = ObjectId(reclamation_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID de réclamation invalide.")

    updated_reclamation = await reclamation_collection.find_one_and_update(
        {"_id": reclamation_id},
        {"$set": update_data.dict(exclude_unset=True)},
        return_document=True,
    )

    if not updated_reclamation:
        raise HTTPException(status_code=404, detail="Réclamation introuvable.")

    return {
        "status": "ok",
        "message": "Statut de la réclamation mis à jour.",
        "data": DecodeReclamation(updated_reclamation),
    }


@reclamation_router.delete("/delete/{reclamation_id}", response_model=dict)
async def delete_reclamation(
    reclamation_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Supprimer une réclamation. 
    Accessible uniquement à l'administrateur ou au propriétaire de la réclamation.
    """
    try:
        reclamation_id = ObjectId(reclamation_id)
    except errors.InvalidId:
        raise HTTPException(
            status_code=400, 
            detail="ID de réclamation invalide."
        )

    reclamation = await reclamation_collection.find_one({"_id": reclamation_id})
    if not reclamation:
        raise HTTPException(
            status_code=404, 
            detail="Réclamation introuvable."
        )

    if (
        "admin" not in current_user.get("roles", []) and
        str(reclamation["utilisateur_id"]) != str(current_user["id"])
    ):
        raise HTTPException(
            status_code=403,
            detail="Accès refusé. Seul l'administrateur ou le propriétaire peut supprimer cette réclamation."
        )

    result = await reclamation_collection.delete_one({"_id": reclamation_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la suppression de la réclamation."
        )

    return {
        "status": "ok",
        "message": "Réclamation supprimée avec succès."
    }


