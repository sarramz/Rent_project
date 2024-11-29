from fastapi import APIRouter, HTTPException, Depends
from models.notification import Notification, UpdateNotificationModel
from serializers.notification_serializer import DecodeNotification, DecodeNotifications
from bson import ObjectId
from config.config import notification_collection, user_collection

notification_router = APIRouter()

# Créer une nouvelle notification
@notification_router.post("/new/notification")
def create_notification(notification: Notification):
    utilisateur = user_collection.find_one({"_id": ObjectId(notification.utilisateur_id)})
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    result = notification_collection.insert_one(notification.dict())
    return {
        "status": "ok",
        "message": "Notification créée",
        "_id": str(result.inserted_id)
    }

# Obtenir toutes les notifications
@notification_router.get("/all/notifications")
def get_all_notifications():
    notifications = notification_collection.find()
    return {
        "status": "ok",
        "data": DecodeNotifications(notifications)
    }

# Mettre à jour une notification
@notification_router.patch("/update/notification/{notification_id}")
def update_notification(notification_id: str, update: UpdateNotificationModel):
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=400, detail="ID de notification invalide")

    updated_notification = notification_collection.find_one_and_update(
        {"_id": ObjectId(notification_id)},
        {"$set": update.dict(exclude_unset=True)},
        return_document=True
    )
    if not updated_notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")

    return {"status": "ok", "message": "Notification mise à jour avec succès"}

# Supprimer une notification
@notification_router.delete("/delete/notification/{notification_id}")
def delete_notification(notification_id: str):
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=400, detail="ID de notification invalide")

    deleted_notification = notification_collection.find_one_and_delete({"_id": ObjectId(notification_id)})
    if not deleted_notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")

    return {"status": "ok", "message": "Notification supprimée avec succès"}
