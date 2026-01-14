from pydantic import BaseModel
from datetime import datetime

class Location(BaseModel):
    lat: float
    lng: float
    address: str

class RideCreate(BaseModel):
    start_location: Location
    end_location: Location
    departure_time: datetime
    total_seats: int
    total_fare: float
