from fastapi import APIRouter, HTTPException, Depends, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional
from models.property import Property, UpdatePropertyModel
from serializers.property_serializer import decode_property, decode_properties
from config.config import property_collection, user_collection
from auth.auth import is_admin, get_current_user,is_proprietaire

property_router = APIRouter()

# Créer une propriété
@property_router.post("/add", response_model=dict)
async def create_property(
    property: Property,
    current_user: dict = Depends(get_current_user),
):
    """Permet aux propriétaires et administrateurs d'ajouter une propriété."""
    # Vérification des permissions
    if current_user["role"] not in ["admin", "proprietaire"]:
        raise HTTPException(
            status_code=403,
            detail="Seuls les administrateurs et les propriétaires peuvent créer une propriété.",
        )

    proprietaire_id = current_user.get("_id") or current_user.get("id")
    if not proprietaire_id:
        raise HTTPException(
            status_code=500,
            detail="Erreur interne : identifiant utilisateur introuvable.",
        )

    # Vérifier si le propriétaire existe dans la base de données
    user_in_db = await user_collection.find_one({"_id": ObjectId(proprietaire_id)})
    if not user_in_db:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur non trouvé dans la base de données.",
        )

    property_data = property.dict()
    property_data["proprietaire_id"] = str(proprietaire_id)
   
    result = await property_collection.insert_one(property_data)
    return {
        "status": "ok",
        "message": "Propriété ajoutée avec succès",
        "_id": str(result.inserted_id),
    }

# Récupérer toutes les propriétés
@property_router.get("/all", response_model=dict)
async def get_all_properties(current_user: dict = Depends(get_current_user)):
    """Récupérer toutes les propriétés, accessible à tous les utilisateurs."""
    properties_cursor = property_collection.find()
    properties = await properties_cursor.to_list(length=None)
    serialized_properties = decode_properties(properties)
    return {"status": "ok", "data": serialized_properties}

# Récupérer une propriété par ID
@property_router.get("/get/{property_id}", response_model=dict)
async def get_property(property_id: str, current_user: dict = Depends(get_current_user)):
    """Récupérer les détails d'une propriété par son ID."""
    try:
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Format de l'ID invalide")

    property_ = await property_collection.find_one({"_id": object_id})
    if not property_:
        raise HTTPException(status_code=404, detail="Propriété introuvable")

    # Vérifier si l'utilisateur a le droit d'accès
    if (
        current_user["role"] not in ["admin", "proprietaire", "locataire"]
        and str(current_user["_id"]) != property_["proprietaire_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Accès interdit : vous n'avez pas les droits pour consulter cette propriété.",
        )

    return {"status": "ok", "data": decode_property(property_)}

# Mettre à jour une propriété
@property_router.patch("/update/{property_id}", response_model=dict)
async def update_property(
    property_id: str,
    property: UpdatePropertyModel,
    current_user: dict = Depends(get_current_user),
):
    """Permet aux propriétaires et administrateurs de mettre à jour une propriété."""
    try:
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Format de l'ID invalide")

    existing_property = await property_collection.find_one({"_id": object_id})
    if not existing_property:
        raise HTTPException(status_code=404, detail="Propriété introuvable")

    # Vérification des permissions
    if (
        current_user["role"] != "admin"
        and str(current_user["_id"]) != existing_property["proprietaire_id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Accès interdit : seuls les propriétaires ou administrateurs peuvent modifier cette propriété.",
        )

    update_data = property.dict(exclude_unset=True)
    await property_collection.update_one({"_id": object_id}, {"$set": update_data})
    return {"status": "ok", "message": "Propriété mise à jour avec succès"}

# Supprimer une propriété
@property_router.delete("/delete/{property_id}", response_model=dict)
async def delete_property(
    property_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Supprimer une propriété.
    Les administrateurs peuvent supprimer n'importe quelle propriété.
    Les propriétaires ne peuvent supprimer que leurs propres propriétés.
    """
    try:
        # Conversion de l'ID en ObjectId
        object_id = ObjectId(property_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format de l'ID invalide. Veuillez fournir un ID MongoDB valide.",
        )

    # Recherche de la propriété
    property_ = await property_collection.find_one({"_id": object_id})
    if not property_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La propriété spécifiée est introuvable. Assurez-vous que l'ID est correct.",
        )
    print(f"Utilisateur actuel dans la suppression : {current_user}")
    # Récupération des informations nécessaires
    proprietaire_id = property_.get("proprietaire_id")
    current_user_id = str(current_user.get("id"))
    is_admin = current_user.get("role") == "admin"
    is_proprietaire = current_user_id == proprietaire_id

     # Logs pour le débogage
    print(f"Utilisateur actuel dans la suppression : {current_user}")
    print(f"Propriétaire ID (propriété) : {proprietaire_id}")
    print(f"Utilisateur actuel ID : {current_user_id}")
    print(f"Rôle utilisateur : {current_user.get('role')}")
    print(f"Est administrateur ? {is_admin}")
    print(f"Est propriétaire de la propriété ? {is_proprietaire}")
    
 # Vérification des permissions
    if not is_admin and not is_proprietaire:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Vous n'êtes pas autorisé à supprimer cette propriété. "
                "Seuls les administrateurs et les propriétaires de la propriété peuvent effectuer cette action."
            ),
        )
        
    # Suppression de la propriété
    result = await property_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur inattendue s'est produite lors de la suppression de la propriété.",
        )

    return {"status": "ok", "message": "Propriété supprimée avec succès"}
# Recherche des propriétés
@property_router.get("/search", response_model=dict)
async def search_properties(
    ville: Optional[str] = None,
    prix_min: Optional[float] = None,
    prix_max: Optional[float] = None,
):
    """Rechercher des propriétés selon des critères (ville, prix)"""
    query = {}
    if ville:
        query["ville"] = ville
    if prix_min is not None:
        query["prix"] = {"$gte": prix_min}
    if prix_max is not None:
        query["prix"] = query.get("prix", {})
        query["prix"]["$lte"] = prix_max

    properties_cursor = property_collection.find(query)
    properties = await properties_cursor.to_list(length=None)
    serialized_properties = decode_properties(properties)
    return {"status": "ok", "data": serialized_properties}
