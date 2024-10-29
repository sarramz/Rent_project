# models/comment.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Comment(BaseModel):
    utilisateur_id: str  # Référence à l'utilisateur
    appartement_id: Optional[str] = None  # Référence à l'appartement (si applicable)
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)

class UpdateCommentModel(BaseModel):
    contenu: Optional[str]
    date: Optional[datetime]
