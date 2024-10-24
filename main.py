from fastapi import FastAPI
from routes.property_route import entry_root
app = FastAPI()
app.include_router(entry_root)