from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from bson import ObjectId
from typing import List, Dict
from models.notification import Notification
from serializers.notification_serializer import DecodeNotification, DecodeNotifications
from config.config import notification_collection
from auth.auth import (
    get_current_user,
    get_current_user_from_ws,
    is_admin,
    is_proprietaire,
    is_locataire,
)

notification_router = APIRouter()

class ConnectionManager:
    """Gestionnaire de connexions WebSocket pour les notifications."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@notification_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Gérer les connexions WebSocket."""
    try:
        current_user = await get_current_user_from_ws(websocket)
        user_id = str(current_user["id"])
        await manager.connect(user_id, websocket)
        print(f"Connexion établie pour l'utilisateur {user_id}")

        while True:
            await websocket.receive_text()  # Maintenir la connexion active

    except WebSocketDisconnect:
        print(f"Déconnexion pour l'utilisateur {user_id}")
        await manager.disconnect(user_id, websocket)
    except Exception as e:
        print(f"Erreur WebSocket : {e}")
        await websocket.close(code=1011)


@notification_router.post("/add", response_model=dict)
async def create_notification(
    notification: Notification,
    current_user: dict = Depends(get_current_user),
):
    """
    Créer une notification pour l'utilisateur connecté ou un utilisateur cible.
    """
    try:
        role = current_user.get("roles", [])
        user_id = current_user.get("id")
        target_user = None 

        if "admin" in role:
            target_user = notification.utilisateur_id
            if not target_user or not ObjectId.is_valid(target_user):
                raise HTTPException(
                    status_code=400, detail="ID utilisateur cible invalide ou manquant."
                )
        elif "proprietaire" in role or "locataire" in role:
            target_user = notification.utilisateur_id or user_id  # Auto-ciblage pour propriétaires ou locataires
        else:
            raise HTTPException(
                status_code=403, detail="Rôle utilisateur non autorisé à créer une notification."
            )

        notification_data = notification.dict()
        notification_data["utilisateur_emetteur"] = user_id
        notification_data["utilisateur_id"] = target_user

        result = await notification_collection.insert_one(notification_data)
        notification_data["_id"] = str(result.inserted_id)

        await manager.send_personal_message(
            DecodeNotification(notification_data), str(target_user)
        )

        return {
            "status": "ok",
            "message": "Notification créée avec succès.",
            "_id": str(result.inserted_id),
        }

    except Exception as e:
        print(f"Erreur lors de la création de la notification : {e}")
        raise HTTPException(
            status_code=500, detail="Erreur interne lors de la création de la notification."
        )
        
@notification_router.get("/all", response_model=dict)
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """
    Récupérer les notifications pour l'utilisateur actuel.
    """
    try:
        utilisateur_id = current_user["id"]
        query = {"utilisateur_id": utilisateur_id}

        notifications = await notification_collection.find(query).limit(limit).to_list(length=limit)

        if not notifications:
            return {"status": "ok", "message": "Aucune notification trouvée.", "data": []}

        return {"status": "ok", "data": DecodeNotifications(notifications)}

    except Exception as e:
        print(f"Erreur lors de la récupération des notifications : {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération des notifications.",
        )