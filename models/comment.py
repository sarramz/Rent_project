from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Comment(BaseModel):
    utilisateur_id: str
    appartement_id: Optional[str] = None
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)

class UpdateCommentModel(BaseModel):
    contenu: Optional[str]
    date: Optional[datetime]
