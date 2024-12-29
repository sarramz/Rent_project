from fastapi import APIRouter, HTTPException, Depends
from models.facture import Facture
from serializers.facture_serializer import DecodeFacture, DecodeFactures
from config.config import facture_collection, reservation_collection
from bson import ObjectId
from fastapi.responses import StreamingResponse
from utils.pdf_generator import generate_facture_pdf
from auth.auth import get_current_user

facture_router = APIRouter()

@facture_router.post("/add", response_model=dict)
async def create_facture(facture_data: Facture,current_user: dict = Depends(get_current_user)):
    """
    Créer une nouvelle facture pour une réservation existante
    Cette tâche est strictement réservée au locataire pour éviter toute incohérence
    """
    if not ObjectId.is_valid(facture_data.reservation_id):
        raise HTTPException(status_code=400, detail="ID de réservation invalide")

    reservation = await reservation_collection.find_one({"_id": ObjectId(facture_data.reservation_id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")

    locataire_id = current_user["id"]
    if reservation.get("idU") != str(locataire_id):
        raise HTTPException(
            status_code=403, 
            detail="Vous n'êtes pas autorisé à générer une facture pour cette réservation."
        )

    facture = Facture(
        description=facture_data.description,
        reservation_id=facture_data.reservation_id,
        montantHT=facture_data.montantHT,
        TVA=facture_data.TVA
    )
    facture.calculer_total()

    facture_dict = facture.dict()
    facture_dict["locataire_id"] = str(locataire_id)
    result = await facture_collection.insert_one(facture_dict)

    pdf = generate_facture_pdf(facture_dict)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=facture_{result.inserted_id}.pdf"
        },
    )


@facture_router.get("/all/{locataire_id}",response_description="Liste des factures du locataire")
async def get_locataire_factures(locataire_id: str):
    """
    Récupère toutes les factures pour un locataire donné 
    """
    try:
        if not ObjectId.is_valid(locataire_id):
            return {
                "status": "error",
                "message": "ID locataire invalide"
            }
        
        cursor = facture_collection.find({"locataire_id": locataire_id})
        factures = await cursor.to_list(length=None)
        
        if not factures:
            return {
                "status": "success",
                "data": []
            }
        
        factures_list = DecodeFactures(factures)
        
        if not factures_list:
            return {
                "status": "error",
                "message": "Erreur lors du décodage des factures"
            }
        
        return {
            "status": "success",
            "data": factures_list
        }

    except Exception as e:
        print(f"Erreur inattendue: {str(e)}") 
        return {
            "status": "error",
            "message": "Une erreur est survenue lors de la récupération des factures"
        }
