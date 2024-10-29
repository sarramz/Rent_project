from pydantic import BaseModel
from datetime import datetime

class Comment(BaseModel):
    contenu: str
    date: datetime

class UpdateCommentModel(BaseModel):
    contenu: Optional[str]
    date: Optional[datetime]
