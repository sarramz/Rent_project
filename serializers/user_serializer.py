def DecodeUser(user) -> dict:
    return {
        "_id": str(user["_id"]),
        "nom": user.get("nom", ""),
        "prénom": user.get("prénom", ""),
        "date_de_naissance": user.get("date_de_naissance", ""),
        "téléphone": user.get("téléphone", ""),
        "adresse": user.get("adresse", ""),
        "email": user.get("email", ""),
        "nom_utilisateur": user.get("nom_utilisateur", ""),
        "mot_de_passe": user.get("mot_de_passe", ""),
        "état": user.get("état", 1),
        "image": user.get("image", None)
    }

def DecodeUsers(users) -> list:
    return [DecodeUser(user) for user in users]
