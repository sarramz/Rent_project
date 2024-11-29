from fastapi import APIRouter, HTTPException
from models.comment import Comment, UpdateCommentModel
from serializers.comment_serializer import DecodeComment, DecodeComments
from bson import ObjectId

from config.config import comment_collection, property_collection, user_collection


comment_router = APIRouter()

# Créer un nouveau commentaire
@comment_router.post("/new/comment")
def create_comment(comment: Comment):
    # Vérifier si l'utilisateur existe
    if not user_collection.find_one({"_id": ObjectId(comment.utilisateur_id)}):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Vérifier l'existence de l'appartement, si spécifié
    if comment.appartement_id and not property_collection.find_one({"_id": ObjectId(comment.appartement_id)}):
        raise HTTPException(status_code=404, detail="Appartement non trouvé")

    # Insérer le commentaire
    comment_data = comment.dict()
    result = comment_collection.insert_one(comment_data)
    comment_id = str(result.inserted_id)

    return {"status": "ok", "message": "Commentaire créé avec succès", "_id": comment_id}

# Obtenir tous les commentaires
@comment_router.get("/all/comments")
def get_all_comments():
    comments = comment_collection.find()
    return {"status": "ok", "data": DecodeComments(comments)}

# Obtenir un commentaire par ID
@comment_router.get("/comment/{comment_id}")
def get_comment(comment_id: str):
    # Vérifier la validité de l'ObjectId
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de comment invalide")

    comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
    if comment:
        return {"status": "ok", "data": DecodeComment(comment)}
    raise HTTPException(status_code=404, detail="Commentaire non trouvé")

# Mettre à jour un commentaire
@comment_router.patch("/update/comment/{comment_id}")
def update_comment(comment_id: str, comment: UpdateCommentModel):
    # Vérifier la validité de l'ObjectId
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de comment invalide")

    update_data = comment.dict(exclude_unset=True)
    updated_comment = comment_collection.find_one_and_update(
        {"_id": ObjectId(comment_id)},
        {"$set": update_data},
        return_document=True
    )
    if updated_comment:
        return {"status": "ok", "message": "Commentaire mis à jour avec succès"}
    raise HTTPException(status_code=404, detail="Commentaire non trouvé")

# Supprimer un commentaire
@comment_router.delete("/delete/comment/{comment_id}")
def delete_comment(comment_id: str):
    # Vérifier la validité de l'ObjectId
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de comment invalide")

    deleted_comment = comment_collection.find_one_and_delete({"_id": ObjectId(comment_id)})
    if deleted_comment:
        return {"status": "ok", "message": "Commentaire supprimé avec succès"}
    raise HTTPException(status_code=404, detail="Commentaire non trouvé")
