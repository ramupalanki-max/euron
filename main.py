from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["euron"]
euron_data = db["euron_coll"]

app = FastAPI()

class eurondata(BaseModel):
    name: str
    phone: str
    city: str
    course: str

class EuronPartialUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    city: str | None = None
    course: str | None = None
    
@app.post("/euron/insert")    
async def euron_data_insert_helper(data:eurondata):
    result  = await euron_data.insert_one(data.dict())
    return str(result.inserted_id)

def euron_helper(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@app.get("/euron/getdata")
async def get_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document))
    return iterms


@app.get("/euron/showdata/{item_id}")
async def show_single_euron_data(item_id: str):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    document = await euron_data.find_one({"_id": obj_id})

    if not document:
        raise HTTPException(status_code=404, detail="Item not found")

    return euron_helper(document)




@app.delete("/euron/delete/{item_id}")
async def delete_euron_data(item_id: str):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = await euron_data.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"status": "success", "message": f"Item {item_id} deleted"}


@app.put("/euron/update/{item_id}")
async def full_update_euron_data(item_id: str, data: eurondata):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = await euron_data.update_one(
        {"_id": obj_id},
        {"$set": data.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"status": "success", "message": "Full update completed"}

# --------------------
# PARTIAL UPDATE API (PATCH)
# --------------------
@app.patch("/euron/update/partial/{item_id}")
async def partial_update_euron_data(item_id: str, data: EuronPartialUpdate):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    update_data = {k: v for k, v in data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    result = await euron_data.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"status": "success", "message": "Partial update completed"}