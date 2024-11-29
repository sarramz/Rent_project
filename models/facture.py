from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Facture(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    reservation_id: str  
    locataire_id: str  
    numero_facture: str  
    montantHT: float  
    TVA: float = 0.18  
    total: Optional[float] = None  
    date_emission: datetime = Field(default_factory=datetime.utcnow)
    statut: str = "En attente"

    def calculer_total(self):
        self.total = self.montantHT + (self.montantHT * self.TVA)

class UpdateFactureModel(BaseModel):
    montantHT: Optional[float]
    TVA: Optional[float]
    total: Optional[float]
