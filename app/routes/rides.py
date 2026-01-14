from fastapi import APIRouter, Depends, HTTPException
from app.db.mongodb import db
from app.schemas.ride import RideCreate
from app.models.ride import create_ride_doc
from app.dependencies.auth import get_current_user
from datetime import datetime
from fastapi import Query
router = APIRouter(prefix="/rides", tags=["Rides"])

@router.post("/create")
async def create_ride(
    ride: RideCreate,
    user=Depends(get_current_user)
):
    if not user["is_verified"]:
        raise HTTPException(403, "User not verified")

    if ride.total_seats < 2:
        raise HTTPException(400, "At least 2 seats required")

    ride_doc = create_ride_doc(ride, user)
    await db.rides.insert_one(ride_doc)

    return {"message": "Ride created successfully"}


@router.get('/search')
async def search_rides(
    start_time:datetime =Query(...),
    end_time:datetime =Query(...),
    user=Depends(get_current_user)
):
    rides=await db.rides.find({
        "profession":user["profession"],
        "departure_time":{
            "$gte":start_time,
            "$lte":end_time
        },
        "available_seats":{"$gte":0},
        "status":"scheduled"
    }).to_list(20)

    return rides

from bson import ObjectId

@router.post("/{ride_id}/complete")
async def complete_ride(
    ride_id: str,
    user=Depends(get_current_user)
):
    ride = await db.rides.find_one({"_id": ObjectId(ride_id)})
    if not ride:
        raise HTTPException(404, "Ride not found")

#sirf driverrr kar paai completeee
    if ride["driver_id"] != user["_id"]:
        raise HTTPException(403, "Only driver can complete this ride")

    if ride["status"] == "completed":
        raise HTTPException(400, "Ride already completed")

    if datetime.now() < ride["departure_time"]:
        raise HTTPException(400, "Ride cannot be completed before start time")
 
    await db.rides.update_one(
        {"_id": ObjectId(ride_id)},
        {"$set": {"status": "completed"}}
    )
    await db.bookings.update_many(
        {
            "ride_id": ObjectId(ride_id),
            "status": "booked"
        },
        {"$set": {"status": "completed"}}
    )
    return {"message": "Ride completed successfully"}
