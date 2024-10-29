from pydantic import BaseModel
from datetime import datetime

class Notification(BaseModel):
    contenu: str
    date: datetime

class UpdateNotificationModel(BaseModel):
    contenu: Optional[str]
    date: Optional[datetime]
