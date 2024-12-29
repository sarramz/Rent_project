from bson import ObjectId
from datetime import datetime

def DecodeFacture(facture) -> dict:
    """Convertit un document MongoDB en dictionnaire."""
    try:
        decoded_facture = {
            "_id": str(facture.get("_id", "")),
            "reservation_id": str(facture.get("reservation_id", "")),
            "locataire_id": str(facture.get("locataire_id", "")),
            "description": str(facture.get("description", "")),
            "montantHT": float(facture.get("montantHT", 0)),
            "TVA": float(facture.get("TVA", 0)),
            "date_emission": facture.get("date_emission", datetime.utcnow())
        }
        
        total = facture.get("total")
        decoded_facture["total"] = float(total) if total is not None else None
        
        return decoded_facture
        
    except Exception as e:
        print(f"Erreur lors du décodage de la facture: {str(e)}")
        return None

def DecodeFactures(factures) -> list:
    """Convertit une liste de documents MongoDB en liste de dictionnaires."""
    decoded_factures = []
    
    for facture in factures:
        decoded_facture = DecodeFacture(facture)
        if decoded_facture:
            decoded_factures.append(decoded_facture)
            
    return decoded_factures