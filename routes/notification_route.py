from fastapi import APIRouter, HTTPException
from models.notification import Notification, UpdateNotificationModel
from serializers.notification_serializer import DecodeNotification, DecodeNotifications
from bson import ObjectId
from config.config import notification_collection,user_collection

notification_router = APIRouter()

# Créer une nouvelle notification
@notification_router.post("/new/notification")
def create_notification(notification: Notification):
    if not user_collection.find_one({"_id": ObjectId(notification.utilisateur_id)}):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    notification_data = notification.dict()
    result = notification_collection.insert_one(notification_data)
    notification_id = str(result.inserted_id)
    return {"status": "ok", "message": "Notification créée", "_id": notification_id}

# Obtenir toutes les notifications
@notification_router.get("/all/notifications")
def get_all_notifications():
    notifications = notification_collection.find()
    return {"status": "ok", "data": DecodeNotifications(notifications)}

# Mettre à jour le statut de lecture d'une notification
@notification_router.patch("/update/notification/{notification_id}")
def mark_notification_as_read(notification_id: str, update: UpdateNotificationModel):
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de notification invalide")

    update_data = update.dict(exclude_unset=True)
    updated_notification = notification_collection.find_one_and_update(
        {"_id": ObjectId(notification_id)},
        {"$set": update_data},
        return_document=True
    )
    if updated_notification:
        return {"status": "ok", "message": "Statut de lecture de la notification mis à jour"}
    raise HTTPException(status_code=404, detail="Notification non trouvée")

# Supprimer une notification
@notification_router.delete("/delete/notification/{notification_id}")
def delete_notification(notification_id: str):
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=400, detail="Format d'identifiant de notification invalide")

    deleted_notification = notification_collection.find_one_and_delete({"_id": ObjectId(notification_id)})
    if deleted_notification:
        return {"status": "ok", "message": "Notification supprimée avec succès"}
    raise HTTPException(status_code=404, detail="Notification non trouvée")
