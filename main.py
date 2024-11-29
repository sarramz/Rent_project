from fastapi import FastAPI

from config.config import db
from routes.user_route import router as user_route
from routes.comment_route import comment_router
from routes.facture_route import facture_router
from routes.notification_route import notification_router
from routes.reservation_route import reservation_router
from routes.property_route import property_router
from routes.reclamation_route import reclamation_router

app = FastAPI(title="Rental Platform API")

# Inclure les routes
app.include_router(user_route, prefix="/users", tags=["Users"])
app.include_router(property_router, prefix="/properties", tags=["Properties"])
app.include_router(reservation_router, prefix="/reservations", tags=["Reservations"])
app.include_router(reclamation_router, prefix="/reclamations", tags=["Reclamations"])
app.include_router(comment_router, prefix="/comments", tags=["Comments"])
app.include_router(facture_router, prefix="/factures", tags=["Factures"])
app.include_router(notification_router, prefix="/notifications", tags=["Notifications"])

