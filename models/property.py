from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Property(BaseModel):
    titre: str
    description: str
    adresse: str
    ville: str
    région: str
    prix: float
    superficie: float
    nbr_chambres: int
    statut: str  # Exp: "disponible", "réservé", "loué", "indisponible"
    date_ajout: datetime = Field(default_factory=datetime.utcnow)
    image: Optional[str] = None
    proprietaire_id: Optional[str] = None

class UpdatePropertyModel(BaseModel):
    titre: Optional[str]
    description: Optional[str]
    adresse: Optional[str]
    ville: Optional[str]
    région: Optional[str]
    prix: Optional[float]
    superficie: Optional[float]
    nbr_chambres: Optional[int]
    statut: Optional[str]
    image: Optional[str]
