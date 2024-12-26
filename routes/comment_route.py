from fastapi import APIRouter, HTTPException,Depends ,status 
from models.comment import Comment, UpdateCommentModel
from serializers.comment_serializer import DecodeComment, DecodeComments
from bson import ObjectId
from datetime import datetime
from config.config import comment_collection, property_collection, user_collection
from auth.auth import get_current_user


comment_router = APIRouter()

@comment_router.post("/add/{appartement_id}")
async def create_comment(
    appartement_id: str, 
    comment: Comment, 
    current_user: dict = Depends(get_current_user),
):
    """
    Créer un nouveau commentaire pour un appartement.

    Args:
        appartement_id (str): L'ID de l'appartement (transmis dans l'URL).
        comment (Comment): Les données du commentaire (contenu uniquement).
        current_user (dict): L'utilisateur connecté (injecté via Depends).

    Returns:
        dict: Statut et message de succès avec l'ID du commentaire créé.
    """
    appartement = await property_collection.find_one({"_id": ObjectId(appartement_id)})
    if not appartement:
        raise HTTPException(status_code=404, detail="Appartement non trouvé")

    comment_data = {
        "utilisateur_id": str(current_user["id"]),  # Récupéré automatiquement via le token
        "appartement_id": appartement_id,           # Récupéré depuis l'URL
        "contenu": comment.contenu,
        "date": comment.date
    }

    result = await comment_collection.insert_one(comment_data)
    comment_id = str(result.inserted_id)

    return {"status": "ok", "message": "Commentaire créé avec succès", "_id": comment_id}


@comment_router.get("/all/{appartement_id}", response_model=dict)
async def get_all_comments_for_appartement(
    appartement_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Récupérer tous les commentaires d'un appartement.

    Args:
        appartement_id (str): ID de l'appartement.
        current_user (dict): Utilisateur connecté (via le token).

    Returns:
        dict: Liste des commentaires de l'appartement.
    """
    try:
        appartement_id = ObjectId(appartement_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de l'appartement invalide.")

    appartement = await property_collection.find_one({"_id": appartement_id})
    if not appartement:
        raise HTTPException(status_code=404, detail="Appartement non trouvé.")

    comments_cursor = comment_collection.find({"appartement_id": str(appartement_id)})
    comments = await comments_cursor.to_list(length=None)

    return {"status": "ok", "data": DecodeComments(comments)}

@comment_router.patch("/update/{comment_id}", response_model=dict)
async def update_comment(
    comment_id: str,
    comment: UpdateCommentModel,
    current_user: dict = Depends(get_current_user)
):
    """
    Mettre à jour un commentaire existant uniquement si l'utilisateur est le créateur.
    """
    try:
        comment_id = ObjectId(comment_id)
    except Exception:
        raise HTTPException(
            status_code=400, 
            detail="Format d'identifiant de commentaire invalide"
        )

    # Rechercher le commentaire existant
    existing_comment = await comment_collection.find_one({"_id": comment_id})
    if not existing_comment:
        raise HTTPException(
            status_code=404, 
            detail="Commentaire non trouvé"
        )

    # Vérifier que l'utilisateur connecté est le créateur du commentaire
    if str(existing_comment["utilisateur_id"]) != str(current_user["id"]):
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé : vous ne pouvez modifier que vos propres commentaires"
        )

    # Construire les données pour la mise à jour
    update_data = comment.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400, 
            detail="Aucune donnée valide pour la mise à jour"
        )

    # Mettre à jour le champ "date" si nécessaire
    if "date" not in update_data:
        update_data["date"] = datetime.utcnow()

    # Effectuer la mise à jour
    updated_comment = await comment_collection.find_one_and_update(
        {"_id": comment_id},
        {"$set": update_data},
        return_document=True
    )

    if updated_comment:
        return {
            "status": "ok",
            "message": "Commentaire mis à jour avec succès",
            "data": DecodeComment(updated_comment)
        }

    raise HTTPException(
        status_code=500, 
        detail="Erreur lors de la mise à jour du commentaire"
    )


@comment_router.delete("/delete/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Supprimer un commentaire.
    Seul l'utilisateur qui a créé le commentaire ou un administrateur peut le supprimer.

    Args:
        comment_id (str): L'ID du commentaire.
        current_user (dict): Les informations de l'utilisateur connecté.

    Returns:
        dict: Statut de suppression et message de confirmation.
    """
    try:
        comment_id = ObjectId(comment_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Format d'identifiant de commentaire invalide.")

    comment = await comment_collection.find_one({"_id": comment_id})
    if not comment:
        raise HTTPException(status_code=404, detail="Commentaire non trouvé.")

    is_author = str(comment["utilisateur_id"]) == str(current_user["id"])
    is_admin_user = "admin" in current_user.get("roles", [])
    if not (is_author or is_admin_user):
        raise HTTPException(status_code=403, detail="Vous n'avez pas la permission de supprimer ce commentaire.")

    deleted_comment = await comment_collection.delete_one({"_id": comment_id})
    if deleted_comment.deleted_count == 1:
        return {"status": "success", "message": "Commentaire supprimé avec succès."}

    raise HTTPException(status_code=500, detail="Erreur lors de la suppression du commentaire.")