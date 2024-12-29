from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
class Notification(BaseModel):
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
    utilisateur_id: Optional[str] = None

