from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReservationStatus(str, Enum):
    EN_ATTENTE = "En attente"
    CONFIRMÉE = "Confirmée"
    ANNULÉE = "Annulée"

class Reservation(BaseModel):
    date_debut: datetime = Field(..., description="Date de début")
    date_fin: datetime = Field(..., description="Date de fin")
    statut: str = Field(default="En attente", description="Statut de la réservation")
    date_res: datetime = Field(default=None, description="Date de réservation")

class UpdateReservation(BaseModel):
    new_status: Optional[ReservationStatus]
