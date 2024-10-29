from bson import ObjectId

# Un seul document
def DecodeReservation(doc) -> dict:
    return {
        "_id": str(doc["_id"]),
        "idApp": str(doc["idApp"]),
        "idU": str(doc["idU"]),
        "date_debut": doc.get("date_debut"),
        "date_fin": doc.get("date_fin"),
        "statut": doc.get("statut"),
        "date_res": doc.get("date_res"),
    }

# Plusieurs documents
def DecodeReservations(docs) -> list:
    return [DecodeReservation(doc) for doc in docs]
