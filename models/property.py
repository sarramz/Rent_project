from pydantic import BaseModel
from typing import Optional, List

class Property(BaseModel):
    prix: float
    description: str
    adresse: str
    ville: str
    région: str
    nbr_chambres: int
    statut: str
    image: Optional[str] = None

class UpdatePropertyModel(BaseModel):
    prix: Optional[float]
    description: Optional[str]
    adresse: Optional[str]
    ville: Optional[str]
    région: Optional[str]
    nbr_chambres: Optional[int]
    statut: Optional[str]
    image: Optional[str] = None
