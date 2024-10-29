from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Reservation(BaseModel):
    date_début: datetime
    date_fin: datetime
    statut: str
    date_res: datetime

class UpdateReservationModel(BaseModel):
    date_début: Optional[datetime]
    date_fin: Optional[datetime]
    statut: Optional[str]
    date_res: Optional[datetime]
