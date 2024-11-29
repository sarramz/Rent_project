from fastapi import APIRouter, HTTPException, Depends, status
from auth.auth import create_access_token, get_current_user, is_admin
from config.config import user_collection
from models.user import User, UserUpdate, UserLogin
from bson import ObjectId
from passlib.context import CryptContext

router = APIRouter()  # L'objet APIRouter est nommé "router"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# replacer dict() par model_dump() a cause de pydantic v2
@router.post("/register", status_code=201)
async def register_user(user: User):
    user.password = pwd_context.hash(user.password)
    result = await user_collection.insert_one(user.model_dump(exclude={"id"}))  # Utilisation de model_dump()
    return {"_id": str(result.inserted_id)}  # Retourner l'ID avec le bon champ "_id"

@router.post("/login")
async def login(user_login: UserLogin):
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
    return current_user

@router.get("/users", dependencies=[Depends(is_admin)])
async def get_all_users():
    users = await user_collection.find().to_list(100)
    return users

@router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    await user_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user_update.model_dump(exclude_unset=True)}  # Utilisation de model_dump()
    )
    return {"message": "User updated successfully"}
