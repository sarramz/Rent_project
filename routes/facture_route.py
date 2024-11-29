from fastapi import APIRouter, HTTPException
from models.facture import Facture, UpdateFactureModel
from serializers.facture_serializer import DecodeFacture, DecodeFactures
from config.config import facture_collection, reservation_collection, user_collection
from bson import ObjectId
from utils.pdf_generator import generate_facture_pdf
from fastapi.responses import StreamingResponse

facture_router = APIRouter()

@facture_router.post("/new/facture")
def create_facture(facture: Facture):
    # Vérification des entités liées
    if not reservation_collection.find_one({"_id": ObjectId(facture.reservation_id)}):
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    if not user_collection.find_one({"_id": ObjectId(facture.locataire_id)}):
        raise HTTPException(status_code=404, detail="Locataire non trouvé")

    facture.calculer_total()
    result = facture_collection.insert_one(facture.dict())
    return {"status": "ok", "message": "Facture créée", "_id": str(result.inserted_id)}

@facture_router.get("/locataire/factures/{locataire_id}")
def get_locataire_factures(locataire_id: str):
    if not ObjectId.is_valid(locataire_id):
        raise HTTPException(status_code=400, detail="ID locataire invalide")

    factures = facture_collection.find({"locataire_id": locataire_id})
    return {"status": "ok", "data": DecodeFactures(factures)}

@facture_router.get("/facture/{facture_id}/download", response_class=StreamingResponse)
def download_facture(facture_id: str):
    facture = facture_collection.find_one({"_id": ObjectId(facture_id)})
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    pdf = generate_facture_pdf(facture)
    return StreamingResponse(pdf, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=facture_{facture_id}.pdf"
    })
