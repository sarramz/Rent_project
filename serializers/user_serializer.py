from bson import ObjectId

def decode_user(user: dict) -> dict:
    """Convertit un document utilisateur MongoDB en dictionnaire sérialisable."""
    print(f"Utilisateur décodé : {user}")
    return {
        "id": str(user["_id"]) if isinstance(user["_id"], ObjectId) else user["_id"],
        "nom": user.get("nom"),
        "prenom": user.get("prenom"),
        "date_naissance": user.get("date_naissance"),
        "telephone": user.get("telephone"),
        "adresse": user.get("adresse"),
        "email": user.get("email"),
        "username": user.get("username"),
        "etat": user.get("etat"),
        "image": user.get("image"),
        "roles": user.get("roles", []),
    }

def decode_users(users: list) -> list:
    """Convertit une liste de documents utilisateurs MongoDB en liste de dictionnaires sérialisables."""
    return [decode_user(user) for user in users]
