from pydantic import BaseModel, Field
from datetime import datetime

class Reclamation(BaseModel):
    utilisateur_id: str  # Référence à l'utilisateur qui fait la réclamation
    contenu: str
    date: datetime = Field(default_factory=datetime.utcnow)
    statut: str = "En cours"  # Statut par défaut

class UpdateReclamationModel(BaseModel):
    statut: str  # Seulement pour l'administrateur (par exemple : "En cours", "Résolue", etc.)
