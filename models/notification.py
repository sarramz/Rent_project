from pydantic import BaseModel, Field
from datetime import datetime

class Notification(BaseModel):
    utilisateur_id: str  # Référence à l'utilisateur destinataire
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
    lue: bool = False  # Statut de lecture (initialement non lue)

class UpdateNotificationModel(BaseModel):
    lue: bool  # Permet seulement de mettre à jour le statut de lecture
