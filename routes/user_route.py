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
    """Créer un nouvel utilisateur."""
    user.password = pwd_context.hash(user.password)  # Hacher le mot de passe
    result = await user_collection.insert_one(user.model_dump(exclude={"id"}))
    return {"_id": str(result.inserted_id)}

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

@router.get("/users/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Obtenir le profil de l'utilisateur actuel."""
    return {key: current_user[key] for key in current_user if key != "password"}

@router.get("/users", dependencies=[Depends(is_admin)])
async def get_all_users():
    """Obtenir la liste de tous les utilisateurs (admin uniquement)."""
    users = await user_collection.find().to_list(100)
    return decode_users(users)

@router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    """Mettre à jour un utilisateur."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format.",
        )
    await user_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user_update.model_dump(exclude_unset=True)}
    )
    return {"message": "User updated successfully"}
