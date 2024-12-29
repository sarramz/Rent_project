from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import asyncio


MONGODB_URL = "mongodb+srv://sarra:sarra123@cluster0.19tqig2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGODB_URL)
db = client.rental_platform

user_collection = db.users
property_collection = db.properties
reservation_collection = db.reservations
reclamation_collection = db.reclamations
comment_collection = db.comments
facture_collection = db.factures
notification_collection = db.notifications

async def connect_to_mongo():
    try:
        await client.admin.command('ping')
        print("Connexion à MongoDB réussie!")
    except Exception as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

async def close_mongo_connection():
    try:
        client.close()
        print("Connexion MongoDB fermée")
    except Exception as e:
        print(f"Erreur lors de la fermeture de la connexion MongoDB: {e}")

    try:
        collections = await db.list_collection_names()
        required_collections = ['users', 'properties', 'reservations', 'reclamations', 
                              'comments', 'factures', 'notifications']
        
        for coll in required_collections:
            if coll not in collections:
                print(f"Avertissement : Collection '{coll}' introuvable dans la base de données")
                
    except Exception as e:
        print(f"Erreur lors de la vérification des collections : {e}")
        raise HTTPException(status_code=500, detail="Error verifying database collections")

async def initialize_database():
    await connect_to_mongo()
    await verify_collections()
