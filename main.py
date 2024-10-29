from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
import os
from dotenv import load_dotenv
from models import Order
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DETAILS = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@dine-n-shine-cluster.1b1o3.mongodb.net/dine-n-shine?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client["dine-n-shine"]
order_collection = database["orders"]

origins = [
    "http://localhost:5173",
    "https://dine-n-shine.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def order_serializer(order) -> dict:
    return {
        "id": str(order.get("_id")),
        "token": order.get("token"),
        "status": order.get("status"),
        "type": order.get("type"),
        "table": order.get("table"),
        "Amount": order.get("Amount"),
        "Remaining": order.get("Remaining"),
        "items": [
            {
                "name": item.get("name"),
                "quantity": item.get("quantity"),
                "price": item.get("price"),
                "remarks": item.get("remarks"),
            }
            for item in order.get("items", [])
        ],
    }

@app.get("/orders")
async def get_orders():
    orders = await order_collection.find().to_list(100)
    order_list = [order_serializer(order) for order in orders]
    new_orders = [order for order in order_list if order["status"] == "Not Paid"]
    
    return {"orders": order_list, "newOrders": new_orders}

@app.post("/create_order")
async def create_orders(order: Order):
    order_dict = order.dict()
    result = await order_collection.insert_one(order_dict)

    created_order = await order_collection.find_one({"_id": result.inserted_id})
    if created_order:
        return order_serializer(created_order)
    else:
        raise HTTPException(status_code=400, detail="Order creation failed")
    
@app.put("/update_order")
async def update_orders(order: Order, _id: str):
    if not ObjectId.is_valid(_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    updated_order = await order_collection.update_one({"_id": ObjectId(_id)}, {"$set": order.dict(exclude_unset=True)})

    if updated_order.modified_count == 1:
        updated_result = await order_collection.find_one({"_id": ObjectId(_id)})
        return order_serializer(updated_result)
    else:
        raise HTTPException(status_code=404, detail="Order not found or no fields to update")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)