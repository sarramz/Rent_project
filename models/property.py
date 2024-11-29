from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime  

class Property(BaseModel):
    titre: str
    description: str
    adresse: str
    prix: float
    superficie: float
    type_bien: str  # Type de bien : Appartement, Maison, etc.
    disponibilite: bool = True
    date_ajout: datetime = Field(default_factory=datetime.utcnow)  
    image: Optional[str] = None
    propriétaire_id: str

class UpdatePropertyModel(BaseModel):
    titre: Optional[str]
    description: Optional[str]
    adresse: Optional[str]
    prix: Optional[float]
    superficie: Optional[float]
    type_bien: Optional[str]
    disponibilite: Optional[bool]
    image: Optional[str]
