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
    statut: str  # Statut (ex: "disponible", "réservé")
    disponibilite: bool = True
    date_ajout: datetime = Field(default_factory=datetime.utcnow)
    image: Optional[str] = None
    proprietaire_id: Optional[str] = None# Corrigé pour unifier

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
    disponibilite: Optional[bool]
    image: Optional[str]
