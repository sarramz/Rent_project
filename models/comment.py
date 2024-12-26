from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Comment(BaseModel):
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
class UpdateCommentModel(BaseModel):
    contenu: Optional[str] = Field(None, title="Contenu du commentaire")
    date: Optional[datetime] = Field(None, title="Date de modification")