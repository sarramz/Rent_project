# serializers/comment_serializer.py

def DecodeComment(comment) -> dict:
    return {
        "_id": str(comment["_id"]),
        "utilisateur_id": str(comment["utilisateur_id"]),
        "appartement_id": str(comment["appartement_id"]) if comment.get("appartement_id") else None,
        "contenu": comment.get("contenu"),
        "date": comment.get("date")
    }

def DecodeComments(comments) -> list:
    return [DecodeComment(comment) for comment in comments]
