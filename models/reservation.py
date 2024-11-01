from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from typing import Optional
from pydantic.networks import EmailStr

class Reservation(BaseModel):
    idApp: str  # Référence à Appartement par identifiant
    idU: str  # Référence à Utilisateur par identifiant
    date_debut: datetime
    date_fin: datetime
    statut: str
    date_res: datetime = Field(default_factory=datetime.utcnow)

class UpdateReservationModel(BaseModel):
    idApp: Optional[str]
    idU: Optional[str]
    date_debut: Optional[datetime]
    date_fin: Optional[datetime]
    statut: Optional[str]
    date_res: Optional[datetime]
