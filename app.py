from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import math

app = FastAPI(
    title="TAXIUMS4 – Taxi API",
    description="Backend voor TAXIUMS4 rit-berekening en chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # voor demo simpel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    from_lat: float
    from_lng: float
    to_lat: float
    to_lng: float
    price_per_km: float = 1.5

class TripResponse(BaseModel):
    distance_km: float
    duration_minutes: float
    price: float

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

def haversine(lat1, lon1, lat2, lon2):
    """Afstand in km tussen 2 coördinaten."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

@app.get("/")
def serve_index():
    # index.html moet in dezelfde map staan
    return FileResponse("index.html")

@app.post("/calculate-trip", response_model=TripResponse)
def calculate_trip(req: TripRequest):
    distance = haversine(req.from_lat, req.from_lng, req.to_lat, req.to_lng)
    duration_hours = distance / 45 if distance > 0 else 0  # schatting 45 km/u stadsritten
    duration_minutes = duration_hours * 60
    price = distance * req.price_per_km

    return TripResponse(
        distance_km=round(distance, 2),
        duration_minutes=round(duration_minutes, 1),
        price=round(price, 2),
    )

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.lower()

    if "hallo" in text or "hey" in text or "hoi" in text:
        reply = "Welkom bij TAXIUMS4! 🚕 Waar kan ik je mee helpen?"
    elif "rit" in text or "prijs" in text or "kilometer" in text:
        reply = (
            "Ik kan je helpen de ritprijs te berekenen. "
            "Klik twee punten op de kaart of vul de coördinaten in bij 'Rit berekenen'."
        )
    elif "telefoon" in text or "nummer" in text or "bellen" in text:
        reply = "Je kunt TAXIUMS4 direct bellen op 06 4001 4198 📞"
    elif "whatsapp" in text:
        reply = "Stuur ons gerust een WhatsApp op 06 4001 4198 📲"
    else:
        reply = (
            f"Je zei: '{req.message}'. Ik ben de slimme TAXIUMS4-assistent. "
            "Vraag me gerust iets over ritten, prijzen of hoe je ons kunt bereiken!"
        )

    return ChatResponse(reply=reply)
