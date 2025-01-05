from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional
from models.property import Property, UpdatePropertyModel
from serializers.property_serializer import decode_property, decode_properties
from config.config import property_collection, user_collection
from auth.auth import is_admin, get_current_user,is_proprietaire
property_router = APIRouter()

@property_router.post("/add", response_model=dict)
async def create_property(
    property: Property,
    current_user: dict = Depends(get_current_user),
):
    """
    Permet aux propriétaires et administrateurs d'ajouter une propriété.
    """
    allowed_roles = ["proprietaire", "admin"]

    if not any(role in current_user.get("roles", []) for role in allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les propriétaires peuvent ajouter une propriété.",
        )

    proprietaire_id = current_user.get("id") or current_user.get("_id")
    if not proprietaire_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne : identifiant utilisateur introuvable.",
        )

    user_in_db = await user_collection.find_one({"_id": ObjectId(proprietaire_id)})
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé dans la base de données.",
        )

    property_data = property.dict()
    property_data["proprietaire_id"] = str(proprietaire_id)

  
    result = await property_collection.insert_one(property_data)

    return {
        "status": "ok",
        "message": "Propriété ajoutée avec succès.",
        "_id": str(result.inserted_id),
    }




@property_router.get("/all", response_model=dict)
async def get_all_properties(
    current_user: dict = Depends(get_current_user),
    show_all: Optional[bool] = False,  # Les administrateurs/propriétaires peuvent forcer l'affichage de toutes les propriétés
):
    """
    Récupérer toutes les propriétés :
    - Les visiteurs ne voient que les propriétés "disponibles".
    - Les administrateurs et propriétaires peuvent voir toutes les propriétés.
    """
    query = {}
    current_user_roles = current_user.get("roles", [])

    if "admin" not in current_user_roles and "proprietaire" not in current_user_roles:
        query["statut"] = "disponible"


    properties_cursor = property_collection.find(query)
    properties = await properties_cursor.to_list(length=None)
    serialized_properties = decode_properties(properties)

    return {"status": "ok", "data": serialized_properties}



@property_router.get("/get/{property_id}", response_model=dict)
async def get_property(
    property_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Récupérer une propriété par son ID :
    - Les administrateurs peuvent accéder à toutes les propriétés.
    - Les propriétaires peuvent accéder à leurs propres propriétés.
    - Les locataires et visiteurs peuvent voir uniquement les propriétés "disponibles".
    """
    try:
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Format de l'ID invalide.")

    property_ = await property_collection.find_one({"_id": object_id})
    if not property_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriété introuvable.",
        )

    current_user_roles = current_user.get("roles", [])
    current_user_id = str(current_user.get("id") or current_user.get("_id"))
    proprietaire_id = property_.get("proprietaire_id")
    statut = property_.get("statut", "indisponible")

    if (
        "admin" not in current_user_roles
        and current_user_id != proprietaire_id
        and statut != "disponible"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit : vous ne pouvez pas consulter cette propriété.",
        )

    return {"status": "ok", "data": decode_property(property_)}



@property_router.patch("/update/{property_id}", response_model=dict)
async def update_property(
    property_id: str,
    property: UpdatePropertyModel,
    current_user: dict = Depends(get_current_user),
):
    """
    Permet aux propriétaires (de la propriété) et administrateurs de mettre à jour une propriété.
    """
    try:
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Format de l'ID invalide.")

    existing_property = await property_collection.find_one({"_id": object_id})
    if not existing_property:
        raise HTTPException(status_code=404, detail="Propriété introuvable.")

    current_user_roles = current_user.get("roles", [])
    current_user_id = str(current_user.get("id") or current_user.get("_id"))
    proprietaire_id = existing_property.get("proprietaire_id")

    if (
        "admin" not in current_user_roles
        and current_user_id != proprietaire_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs et les propriétaires de la propriété peuvent modifier cette propriété.",
        )

    update_data = property.dict(exclude_unset=True)
    await property_collection.update_one({"_id": object_id}, {"$set": update_data})
    return {"status": "ok", "message": "Propriété mise à jour avec succès."} 
    
    
@property_router.delete("/delete/{property_id}", response_model=dict)
async def delete_property(
    property_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Supprimer une propriété :
    - Administrateurs : peuvent supprimer n'importe quelle propriété.
    - Propriétaires : peuvent supprimer leurs propres propriétés.
    """
    try:
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID invalide. Fournissez un identifiant MongoDB valide.",
        )

    property_ = await property_collection.find_one({"_id": object_id})
    if not property_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriété introuvable.",
        )
        
    proprietaire_id = property_.get("proprietaire_id")
    current_user_id = str(current_user.get("id") or current_user.get("_id"))
    current_user_roles = current_user.get("roles", [])

    if "admin" not in current_user_roles and current_user_id != proprietaire_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit : seuls les administrateurs ou les propriétaires de la propriété peuvent la supprimer.",
        )

    result = await property_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur inattendue lors de la suppression de la propriété.",
        )

    return {"status": "ok", "message": "Propriété supprimée avec succès."}

@property_router.get("/search", response_model=dict)
async def search_properties(
    ville: Optional[str] = None,
    prix_min: Optional[float] = None,
    prix_max: Optional[float] = None,
    nbr_chambres: Optional[int] = None,
    statut: Optional[str] = None, 
):
    """
    Rechercher des propriétés en fonction de critères :
    - Ville
    - Plage de prix
    - Nombre de chambres
    - Statut
    """
    query = {}

    if ville:
        query["ville"] = {"$regex": ville, "$options": "i"} 
    if prix_min is not None:
        query["prix"] = {"$gte": prix_min}
    if prix_max is not None:
        query["prix"] = query.get("prix", {})
        query["prix"]["$lte"] = prix_max
    if nbr_chambres is not None:
        query["nbr_chambres"] = nbr_chambres
    if statut:
        query["statut"] = statut

    properties_cursor = property_collection.find(query)
    properties = await properties_cursor.to_list(length=None)

    return {"status": "ok", "data": decode_properties(properties)}
@property_router.get("/my-properties", response_model=dict)
async def get_user_properties(
    current_user: dict = Depends(get_current_user),
):
    """
    Récupérer les propriétés d'un utilisateur connecté :
    - Administrateurs : voient toutes les propriétés.
    - Propriétaires : voient uniquement leurs propres propriétés.
    """
    query = {}
    current_user_roles = current_user.get("roles", [])
    current_user_id = str(current_user.get("id") or current_user.get("_id"))

    if "admin" in current_user_roles:
        properties_cursor = property_collection.find(query)
    else:
        query["proprietaire_id"] = current_user_id
        properties_cursor = property_collection.find(query)

    properties = await properties_cursor.to_list(length=None)
    serialized_properties = decode_properties(properties)

    return {"status": "ok", "data": serialized_properties}
@property_router.get("/owner/{property_id}", response_model=dict)
async def get_property_owner(
    property_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Récupérer l'identifiant du propriétaire d'une propriété.
    - Administrateurs : peuvent accéder à l'information pour n'importe quelle propriété.
    """
    try:
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de l'ID de la propriété invalide.",
        )

    # Récupérer la propriété depuis la base de données
    property_ = await property_collection.find_one({"_id": object_id})
    if not property_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriété introuvable.",
        )

    # Vérifier les permissions
    current_user_roles = current_user.get("roles", [])
    if "admin" not in current_user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit : seuls les administrateurs peuvent accéder à cette information.",
        )

    proprietaire_id = property_.get("proprietaire_id")
    if not proprietaire_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne : l'identifiant du propriétaire est manquant.",
        )

    # Récupérer les détails du propriétaire
    owner = await user_collection.find_one({"_id": ObjectId(proprietaire_id)})
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propriétaire introuvable.",
        )

    return {
        "status": "ok",
        "property_id": property_id,
        "owner": {
            "id": str(owner["_id"]),
            "nom": owner.get("nom"),
            "prenom": owner.get("prenom"),
            "email": owner.get("email"),
        },
    }



# @property_router.get("/property-with-comments/{property_id}", response_model=dict)
# async def get_property_with_comments(
#     property_id: str,
#     current_user: dict = Depends(get_current_user),
# ):
#     """
#     Récupérer une propriété avec tous ses commentaires associés.

#     Args:
#         property_id (str): ID de la propriété.

#     Returns:
#         dict: Détails de la propriété et liste des commentaires associés.
#     """
#     try:
#         object_id = ObjectId(property_id)
#     except Exception:
#         raise HTTPException(status_code=400, detail="ID de propriété invalide.")

#     property_ = await property_collection.find_one({"_id": object_id})
#     if not property_:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Propriété introuvable.",
#         )

#     current_user_roles = current_user.get("roles", [])
#     current_user_id = str(current_user.get("id") or current_user.get("_id"))
#     proprietaire_id = property_.get("proprietaire_id")
#     statut = property_.get("statut", "indisponible")

#     if (
#         "admin" not in current_user_roles
#         and current_user_id != proprietaire_id
#         and statut != "disponible"
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Accès interdit : vous ne pouvez pas consulter cette propriété.",
#         )

#     comments_cursor = comment_collection.find({"appartement_id": property_id})
#     comments = await comments_cursor.to_list(length=None)

#     return {
#         "status": "ok",
#         "property": decode_property(property_),
#         "comments": DecodeComments(comments),
#     }
