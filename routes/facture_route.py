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

@facture_router.get("/download/{facture_id}", response_description="Télécharger une facture")
async def download_facture(
    facture_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Télécharger une facture en format PDF.
    
    Args:
        facture_id (str): ID de la facture à télécharger.
        current_user (dict): Utilisateur actuellement authentifié.

    Returns:
        StreamingResponse: Le fichier PDF de la facture.
    """
    if not ObjectId.is_valid(facture_id):
        raise HTTPException(status_code=400, detail="ID de facture invalide.")
    
    facture = await facture_collection.find_one({"_id": ObjectId(facture_id)})
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée.")
    
    is_locataire = str(facture.get("locataire_id")) == str(current_user["id"])
    is_admin_user = "admin" in current_user.get("roles", [])
    if not (is_locataire or is_admin_user):
        raise HTTPException(status_code=403, detail="Accès refusé.")
    
    pdf_stream = generate_facture_pdf(facture)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=facture_{facture_id}.pdf"
        },
    )

@facture_router.get("/all", response_description="Récupérer toutes les factures", response_model=dict)
async def get_all_factures():
    """
    Récupérer toutes les factures disponibles.

    Returns:
        dict: Liste de toutes les factures.
    """
    try:
        cursor = facture_collection.find()
        factures = await cursor.to_list(length=None)

        if not factures:
            return {
                "status": "success",
                "data": []
            }

        factures_list = DecodeFactures(factures)

        return {
            "status": "success",
            "data": factures_list
        }

    except Exception as e:
        print(f"Erreur lors de la récupération des factures : {str(e)}")
        return {
            "status": "error",
            "message": "Une erreur est survenue lors de la récupération des factures."
        }
