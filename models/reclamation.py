from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Reclamation(BaseModel):
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)  
    statut: Optional[str] = "En cours"

class UpdateReclamationModel(BaseModel):
    statut: str
