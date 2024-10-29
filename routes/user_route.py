from fastapi import APIRouter, HTTPException
from models.user import User, UpdateUserModel
from serializers.user_serializer import DecodeUser, DecodeUsers
from bson import ObjectId
from config.config import user_collection

user_router = APIRouter()
@user_router.post("/new/user")
def create_user(user: User):
    user_data = dict(user)
    result = user_collection.insert_one(user_data)
    user_id = str(result.inserted_id)
    return {"status": "ok", "message": "User created successfully", "_id": user_id}

@user_router.get("/all/users")
def get_all_users():
    users = user_collection.find()
    return {"status": "ok", "data": DecodeUsers(users)}

@user_router.get("/user/{user_id}")
def get_user(user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return {"status": "ok", "data": DecodeUser(user)}
    raise HTTPException(status_code=404, detail="User not found")

@user_router.patch("/update/user/{user_id}")
def update_user(user_id: str, user: UpdateUserModel):
    update_data = user.dict(exclude_unset=True)
    updated_user = user_collection.find_one_and_update(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )
    if updated_user:
        return {"status": "ok", "message": "User updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@user_router.delete("/delete/user/{user_id}")
def delete_user(user_id: str):
    deleted_user = user_collection.find_one_and_delete({"_id": ObjectId(user_id)})
    if deleted_user:
        return {"status": "ok", "message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
