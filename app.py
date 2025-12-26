from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel
import os

app = FastAPI(title="MongoDB CRUD API")

client = None
collection = None


# ---------- Pydantic Schema ----------
class Item(BaseModel):
    name: str
    price: int


# ---------- MongoDB Startup ----------
@app.on_event("startup")
def startup_db():
    global client, collection

    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("MONGO_DB")
    COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

    if not MONGO_URI or not DB_NAME or not COLLECTION_NAME:
        raise Exception("MongoDB environment variables are missing")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]


# ---------- Helper ----------
def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "MongoDB CRUD API running"}


# CREATE
@app.post("/items")
def create_item(item: Item):
    result = collection.insert_one(item.dict())
    return {"id": str(result.inserted_id)}


# READ ALL
@app.get("/items")
def get_items():
    return [serialize(item) for item in collection.find()]


# READ ONE
@app.get("/items/{item_id}")
def get_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    item = collection.find_one({"_id": oid})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return serialize(item)


# UPDATE
@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    try:
        oid = ObjectId(item_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = collection.update_one(
        {"_id": oid},
        {"$set": item.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item updated successfully"}


# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    try:
        oid = ObjectId(item_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = collection.delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted successfully"}
