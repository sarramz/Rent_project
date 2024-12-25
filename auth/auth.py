from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config.config import user_collection
from bson import ObjectId
from serializers.user_serializer import decode_user
from typing import List

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtenir l'utilisateur actuel à partir du token JWT.
    Décode le token, vérifie son authenticité et retourne les informations de l'utilisateur"""
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
         # Log pour déboguer le payload
        #print(f"Payload du token : {payload}")
        
        if not user_id or not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants d'authentification invalides",
            )
            
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur introuvable",
            )
        
        user_decoded = decode_user(user)
        #print(f"Utilisateur décodé : {user_decoded}")  # Log pour vérifier l'utilisateur décodé
        return user_decoded   
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )
    except Exception as e:
        #print(f"Erreur : {e}")  # Log pour afficher l'erreur
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur inattendue lors du traitement du token",
        )
def is_admin(current_user: dict = Depends(get_current_user)):
    """Vérifier si l'utilisateur est administrateur."""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes",
        )
    return True

def is_proprietaire(current_user: dict = Depends(get_current_user)):
    """Vérifier si l'utilisateur a le rôle de propriétaire."""
    if "proprietaire" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé uniquement aux propriétaires",
        )
    return True

def is_locataire(current_user: dict = Depends(get_current_user)):
    """Vérifier si l'utilisateur a le rôle de locataire."""
    if "locataire" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé uniquement aux locataires",
        )
    return current_user
def create_access_token(data: dict):
    """Générer un token JWT pour un accès authentifié.
    Ajoute une date d'expiration au token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_roles(allowed_roles: List[str]):
    """Vérifier si l'utilisateur a un rôle autorisé."""
    def role_verifier(current_user: dict = Depends(get_current_user)):
        if not any(role in current_user.get("roles", []) for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit : rôle insuffisant."
            )
        return current_user
    return role_verifier