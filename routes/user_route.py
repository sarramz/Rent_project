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
    """Créer un nouvel utilisateur. Le mdp est haché avant d'être enregistré dans la BD"""
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà."
        )
    user.password = pwd_context.hash(user.password) 
    user.role = user.role or "locataire"  # Par défaut, un nouvel utilisateur est un locataire
    result = await user_collection.insert_one(user.model_dump(exclude={"id"}))
    return {"_id": str(result.inserted_id), "message": "Utilisateur enregistré avec succès"}

@router.post("/login")
async def login(user_login: UserLogin):
    """Connexion d'un utilisateur."""
    user = await user_collection.find_one({"email": user_login.email})
    if not user or not pwd_context.verify(user_login.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Obtenir le profil de l'utilisateur actuel."""
    return {key: current_user[key] for key in current_user if key != "password"}

@router.get("/all", dependencies=[Depends(is_admin)])
async def get_all_users():
    """Obtenir la liste de tous les utilisateurs (admin uniquement)."""
    users = await user_collection.find().to_list(100)
    return decode_users(users)

@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    """Obtenir un utilisateur par son ID."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide.",
        )
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé.",
        )
    return decode_user(user)

@router.put("/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    """Mettre à jour un utilisateur."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format d'ID utilisateur invalide.",
        )
    await user_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user_update.model_dump(exclude_unset=True)}
    )
    return {"message": "Utilisateur mis à jour avec succès"}
