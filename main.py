from fastapi import FastAPI
from routes.property_route import entry_root as property_router
from routes.user_route import user_router
from routes.reservation_route import reservation_router

app = FastAPI()
app.include_router(property_router, prefix="/properties")
app.include_router(user_router, prefix="/users")
app.include_router(reservation_router)

