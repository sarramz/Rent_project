
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://sarra:sarra123@cluster0.19tqig2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.rent  

# Collections
property_collection = db["property"]
user_collection = db["users"] 
reservation_collection = db["reservations"]
comment_collection = db["comments"]
notification_collection = db["notifications"]
reclamation_collection = db["reclamations"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)