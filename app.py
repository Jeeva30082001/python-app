from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
import os

app = FastAPI()

# Environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Convert ObjectId to string
def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@app.get("/")
def root():
    return {"message": "MongoDB CRUD API running"}


# CREATE
@app.post("/items")
def create_item(item: dict):
    result = collection.insert_one(item)
    return {"id": str(result.inserted_id)}


# READ ALL
@app.get("/items")
def get_items():
    items = collection.find()
    return [serialize(item) for item in items]


# READ ONE
@app.get("/items/{item_id}")
def get_item(item_id: str):
    item = collection.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize(item)


# UPDATE
@app.put("/items/{item_id}")
def update_item(item_id: str, data: dict):
    result = collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item updated"}


# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    result = collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}
