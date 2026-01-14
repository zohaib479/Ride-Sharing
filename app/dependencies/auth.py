from bson import ObjectId

async def get_current_user():
#(testing ke liye)
    return {
        "_id": ObjectId("6967dac5f8460184f846fa8b"),
        "profession": "doctor",
        "is_verified": True
    }
