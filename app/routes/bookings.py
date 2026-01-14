from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.db.mongodb import db
from app.dependencies.auth import get_current_user
router = APIRouter(prefix="/bookings", tags=["Bookings"])
@router.post("/{ride_id}/book")
async def book_ride(ride_id: str, user=Depends(get_current_user)):
    if not user["is_verified"]:
        raise HTTPException(403, "User not verified")
    ride = await db.rides.find_one({"_id": ObjectId(ride_id)})
    if not ride:
        raise HTTPException(404, "Ride not found")
    if ride["profession"] != user["profession"]:
        raise HTTPException(403, "Profession mismatch")
    existing = await db.bookings.find_one({
        "ride_id": ObjectId(ride_id),
        "user_id": user["_id"]
    })
    if existing:
        raise HTTPException(400, "Already booked")

    updated_ride = await db.rides.find_one_and_update(
        {"_id": ObjectId(ride_id), "available_seats": {"$gt": 0}},
        {"$inc": {"available_seats": -1}}
    )

    if not updated_ride:
        raise HTTPException(409, "No seats available")
    try:
        await db.bookings.insert_one({
            "ride_id": ObjectId(ride_id),
            "user_id": user["_id"],
            "status": "booked"})
    except:
        await db.rides.update_one(
            {"_id": ObjectId(ride_id)},
            {"$inc": {"available_seats": 1}})
        raise HTTPException(500, "Booking failed")
    return {"message": "Seat booked successfully"}
@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    user=Depends(get_current_user)
):
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(404, "Booking not found")


    if booking["user_id"] != user["_id"]:
        raise HTTPException(403, "Not your booking")
    if booking["status"] != "booked":
        raise HTTPException(400, "Booking already cancelled")
    ride = await db.rides.find_one({"_id": booking["ride_id"]})
    if not ride:
        raise HTTPException(404, "Ride not found")

    if ride["status"] != "scheduled":
        raise HTTPException(400, "Cannot cancel after ride started")
    seat_update = await db.rides.update_one(
        {"_id": ride["_id"]},
        {"$inc": {"available_seats": 1}}
    )
    if seat_update.modified_count == 0:
        raise HTTPException(500, "Seat increment failed")

    await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "cancelled"}}
    )
    return {"message": "Booking cancelled successfully"}

@router.get('/my')
async def show_my_bookings(user=Depends(get_current_user)):
    user_bookings = await db.bookings.find({"user_id": user["_id"]}).to_list(length=None)
    result = []
    for booking in user_bookings:
        ride = await db.rides.find_one({"_id": booking["ride_id"]})
        if not ride:
            continue  

    
        driver = await db.users.find_one({"_id": ride["driver_id"]}, {"name": 1, "profession": 1})
        if not driver:
            driver_info = {}
        else:
            driver_info = {"name": driver["name"], "profession": driver["profession"]}
        ride_info = {
            "from": ride["start_location"],
            "to": ride["end_location"],
            "time": ride["departure_time"],
            "driver": driver_info
        }
        result.append({
            "booking_id": str(booking["_id"]),
            "status": booking["status"],
            "ride": ride_info
        })

    return result
