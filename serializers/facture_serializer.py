def DecodeFacture(facture) -> dict:
    return {
        "_id": str(facture["_id"]),
        "reservation_id": str(facture["reservation_id"]),
        "locataire_id": str(facture["locataire_id"]),
        "montantHT": facture["montantHT"],
        "TVA": facture["TVA"],
        "total": facture["total"],
        "date_emission": facture["date_emission"],
        "statut": facture["statut"]
    }

def DecodeFactures(factures) -> list:
    return [DecodeFacture(facture) for facture in factures]
