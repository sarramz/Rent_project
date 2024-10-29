from fastapi import FastAPI
from routes.property_route import entry_root as property_router
from routes.user_route import user_router
from routes.reservation_route import reservation_router
from routes.comment_route import comment_router  # Import du routeur pour les commentaires

app = FastAPI()

app.include_router(property_router, prefix="/properties")
app.include_router(user_router, prefix="/users")
app.include_router(reservation_router, prefix="/reservations")  
app.include_router(comment_router, prefix="/comments")  
