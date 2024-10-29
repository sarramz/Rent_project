from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    nom: str
    prénom: str
    date_de_naissance: datetime
    téléphone: str
    adresse: str
    email: EmailStr
    nom_utilisateur: str
    mot_de_passe: str
    état: int
    image: Optional[str] = None

class UpdateUserModel(BaseModel):
    nom: Optional[str]
    prénom: Optional[str]
    date_de_naissance: Optional[datetime]
    téléphone: Optional[str]
    adresse: Optional[str]
    email: Optional[EmailStr]
    nom_utilisateur: Optional[str]
    mot_de_passe: Optional[str]
    état: Optional[int]
    image: Optional[str] = None
