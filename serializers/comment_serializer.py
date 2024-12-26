def DecodeComment(comment) -> dict:
    return {
        "_id": str(comment["_id"]),
        "utilisateur_id": str(comment.get("utilisateur_id", "")),
        "appartement_id": str(comment.get("appartement_id", "")),
        "contenu": comment.get("contenu", ""),
        "date": comment.get("date", "")
    }

def DecodeComments(comments) -> list:
    return [DecodeComment(comment) for comment in comments]
