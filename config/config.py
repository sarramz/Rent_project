from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import asyncio

# MongoDB Connection URL
MONGODB_URL = "mongodb+srv://sarra:sarra123@cluster0.19tqig2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create async MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client.rental_platform

# Collections
user_collection = db.users
property_collection = db.properties
reservation_collection = db.reservations
reclamation_collection = db.reclamations
comment_collection = db.comments
facture_collection = db.factures
notification_collection = db.notifications

async def connect_to_mongo():
    try:
        # Verify connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

async def close_mongo_connection():
    try:
        client.close()
        print("MongoDB connection closed")
    except Exception as e:
        print(f"Error closing MongoDB connection: {e}")

# Verify collections
async def verify_collections():
    try:
        collections = await db.list_collection_names()
        required_collections = ['users', 'properties', 'reservations', 'reclamations', 
                              'comments', 'factures', 'notifications']
        
        for coll in required_collections:
            if coll not in collections:
                print(f"Warning: Collection '{coll}' not found in database")
                
    except Exception as e:
        print(f"Error verifying collections: {e}")
        raise HTTPException(status_code=500, detail="Error verifying database collections")

# Initialize connection and verify collections on startup
async def initialize_database():
    await connect_to_mongo()
    await verify_collections()
