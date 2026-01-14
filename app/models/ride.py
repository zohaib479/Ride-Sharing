from datetime import datetime

def create_ride_doc(data, driver):
    return {
        "driver_id": driver["_id"],
        "profession": driver["profession"], 
        "start_location": data.start_location.dict(),
        "end_location": data.end_location.dict(),
        "departure_time": data.departure_time,
        "total_seats": data.total_seats,
        "available_seats": data.total_seats, 
        "total_fare": data.total_fare,
        "status": "scheduled",
        "created_at": datetime.now()
    }
