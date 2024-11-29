def decode_user(user: dict) -> dict:
    """Convertit un document utilisateur MongoDB en dictionnaire serializable"""
    return {
        "id": str(user["_id"]),
        "nom": user.get("nom"),
        "prenom": user.get("prenom"),
        "date_naissance": user.get("date_naissance"),
        "telephone": user.get("telephone"),
        "adresse": user.get("adresse"),
        "email": user.get("email"),
        "username": user.get("username"),
        "etat": user.get("etat"),
        "image": user.get("image"),
        "role": user.get("role"),
    }

def decode_users(users: list) -> list:
    """Convertit une liste de documents utilisateurs MongoDB en liste de dictionnaires serializables"""
    return [decode_user(user) for user in users]
