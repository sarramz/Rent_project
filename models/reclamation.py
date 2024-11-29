from pydantic import BaseModel, Field
from datetime import datetime

class Reclamation(BaseModel):
    utilisateur_id: str
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
    statut: str = "En cours"

class UpdateReclamationModel(BaseModel):
    statut: str
