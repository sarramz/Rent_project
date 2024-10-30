from pydantic import BaseModel, Field
from datetime import datetime

class Reclamation(BaseModel):
    utilisateur_id: str  # Référence à l'utilisateur émetteur
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
    statut: str = "En cours"  # Statut de traitement

class UpdateReclamationModel(BaseModel):
    contenu: Optional[str]
    statut: Optional[str]
    date: Optional[datetime]
