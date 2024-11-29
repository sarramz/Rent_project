from pydantic import BaseModel, Field
from datetime import datetime

class Notification(BaseModel):
    utilisateur_id: str
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
    lue: bool = False

class UpdateNotificationModel(BaseModel):
    lue: bool
