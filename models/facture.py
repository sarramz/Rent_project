from pydantic import PositiveFloat, confloat, BaseModel, Field
from typing import Optional
from datetime import datetime

class Facture(BaseModel):
    reservation_id: str
    description: str
    montantHT: PositiveFloat  
    TVA: confloat(ge=0, le=1) = 0.18  
    total: Optional[float] = None
    date_emission: datetime = Field(default_factory=datetime.utcnow)

    def calculer_total(self):
        self.total = self.montantHT + (self.montantHT * self.TVA)


