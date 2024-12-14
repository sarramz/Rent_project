from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReservationStatus(str, Enum):
    EN_ATTENTE = "En attente"
    CONFIRMÉE = "Confirmée"
    ANNULÉE = "Annulée"

class Reservation(BaseModel):
    idApp: str  
    idU: str  
    date_debut: datetime 
    date_fin: datetime  
    statut: ReservationStatus = ReservationStatus.EN_ATTENTE  
    date_res: datetime = Field(default_factory=datetime.utcnow) 

class UpdateReservation(BaseModel):
    idApp: Optional[str]
    idU: Optional[str]  
    date_debut: Optional[datetime]
    date_fin: Optional[datetime]
    statut: Optional[ReservationStatus]
    date_res: Optional[datetime]
