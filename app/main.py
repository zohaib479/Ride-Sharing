from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from dotenv import load_dotenv
from app.db.mongodb import db

app=FastAPI()

@app.get('/test-db')
async def test_db():
    collections=await db.list_collection_names()
    return {"collections":collections}
@app.on_event("startup")
async def startup_db():
    print("MongoDB Connected")

@app.on_event("shutdown")
async def shutdown_db():
    print('MongoDB Disconnected')
@app.post("/insert-test")
async def insert_test():
    await db.test.insert_one({"hello": "world"})
    return {"status": "inserted"}

@app.get('/')
def basic():
    return {"message":"hello"}
