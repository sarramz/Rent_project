from fastapi import APIRouter, HTTPException, Depends, status
from auth.auth import create_access_token, get_current_user, is_admin
from config.config import user_collection
from models.user import User, UserUpdate, UserLogin
from bson import ObjectId
from passlib.context import CryptContext
from serializers.user_serializer import decode_user, decode_users

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", status_code=201)
async def register_user(user: User):
    """Créer un nouvel utilisateur. Le mot de passe est haché avant d'être enregistré dans la BD."""
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà."
        )
    user.password = pwd_context.hash(user.password)
    if "locataire" not in user.roles:
        user.roles.append("locataire")
    result = await user_collection.insert_one(user.dict(exclude={"id"}))
    return {"_id": str(result.inserted_id), "message": "Utilisateur enregistré avec succès"}

@router.post("/login")
async def login(user_login: UserLogin):
    """Connexion d'un utilisateur."""
    user = await user_collection.find_one({"email": user_login.email})
    if not user or not pwd_context.verify(user_login.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
        )
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Obtenir le profil de l'utilisateur actuel."""
    return {key: current_user[key] for key in current_user if key != "password"}

@router.get("/all", dependencies=[Depends(is_admin)])
async def get_all_users(skip: int = 0, limit: int = 100):
    """
    Obtenir la liste de tous les utilisateurs (accessible uniquement aux administrateurs).
    - `skip`: Nombre d'utilisateurs à ignorer (pagination).
    - `limit`: Limite du nombre d'utilisateurs à récupérer.
    """
    if limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le paramètre 'limit' ne peut pas dépasser 100."
            )
    users_cursor = user_collection.find().skip(skip).limit(limit)
    users = await users_cursor.to_list(length=limit)
    return decode_users(users)

@router.get("/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    """Obtenir un utilisateur par son ID."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide."
        )
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé."
        )
    if "admin" not in current_user.get("roles", []) and str(current_user["id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas les permissions pour accéder à cet utilisateur."
        )
    return decode_user(user)
@router.put("/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Mettre à jour les informations d'un utilisateur."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide."
        )
    if str(current_user["id"]) != user_id and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas l'autorisation de modifier cet utilisateur."
        )
    user_in_db = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé."
        )
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = pwd_context.hash(update_data["password"])
    await user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return {"message": "Utilisateur mis à jour avec succès"}

@router.delete("/{user_id}", dependencies=[Depends(is_admin)])
async def delete_user(user_id: str):
    """Permet à un administrateur de supprimer un utilisateur."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide."
        )
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé."
        )
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la suppression de l'utilisateur."
        )
    return {"message": "Utilisateur supprimé avec succès"}

# @router.delete("/{user_id}", dependencies=[Depends(is_admin)], response_model=dict)
# async def delete_user(user_id: str):
    """
    Permet à un administrateur de supprimer un utilisateur.
    """
    # Vérifie si l'ID est valide
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide.",
        )

    # Recherche l'utilisateur dans la base de données
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )

    # Supprime l'utilisateur
    result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de la suppression de l'utilisateur.",
        )

    return {"message": "Utilisateur supprimé avec succès"}