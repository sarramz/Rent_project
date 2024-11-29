from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    PROPRIETAIRE = "proprietaire"
    LOCATAIRE = "locataire"
    VISITEUR = "visiteur"


class UserStatus(int, Enum):
    INACTIVE = 0
    ACTIVE = 1


class User(BaseModel):
    nom: str
    prenom: str
    date_naissance: datetime
    telephone: str
    adresse: str
    email: EmailStr
    username: str
    password: str
    etat: UserStatus = UserStatus.ACTIVE
    image: Optional[str] = None
    role: UserRole = UserRole.VISITEUR


class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    date_naissance: Optional[datetime] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    etat: Optional[UserStatus] = None
    image: Optional[str] = None
    role: Optional[UserRole] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str
