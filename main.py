from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List
import os
from dotenv import load_dotenv
from models import Order
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

MONGO_USER = os.getenv("MONGO_USER", "dineAdmin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DETAILS = f"mongodb+srv://dineAdmin:dine-n-shine@dine-n-shine-cluster.1b1o3.mongodb.net/?retryWrites=true&w=majority&appName=dine-n-shine-cluster"

try:
    client = AsyncIOMotorClient(MONGO_DETAILS)
    client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    print("MongoDB connection error:", e)

# client = AsyncIOMotorClient(MONGO_DETAILS)
database = client["dine-n-shine"]
order_collection = database["orders"]
service_collection = database["services"]

origins = [
    "http://localhost:5173",
    "https://dine-n-shine.vercel.app"
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
def service_serializer(service) -> dict:
    return{
        "id":str(service.get("_id")),
        "img":service.get("img"),
        "title":service.get("title"),
        "owner":service.get("owner"),
        "cost":service.get("cost"),
        "date_added":service.get("date_added"),
        "distription":[
            {
                "point":distription.get("point")
            }
            for distription in service.get("distription",[])
        ],
        "menu":{
            "lunch":[
                {
                    "dish": lunch_item.get("dish")
                }
                for lunch_item in service.get("menu",{}).get("lunch",[])
            ],
            "dinner":[
                {
                    "dish": dinner_item.get("dish")
                }
                for dinner_item in service.get("menu",{}).get("dinner",[])
            ]
        }
    }

@app.get("/")
async def home():
    return "welcome to dine-n-shine"

# Service APIs
@app.get("/get_services")
async def get_services():
    services = await service_collection.find().to_list(100)
    service_list = [service_serializer(service) for service in services]
    return {"services":service_list}
    
@app.get("/service_by_id/{_id}")
async def service_by_id(_id: str):
    if not ObjectId.is_valid(_id):
        raise HTTPException(status_code=400, detail="Invalid service ID")
    selected_service = await service_collection.find_one({"_id": _id})
    if selected_service:
        return service_serializer(selected_service)
    else:
        raise HTTPException(status_code=404, detail="Service not found")


# Order APIs
@app.get("/orders")
async def get_orders():
    orders = await order_collection.find().to_list(100)
    order_list = [order_serializer(order) for order in orders]
    new_orders = [order for order in order_list if order["status"] == "Not Paid"]
    
    return {"orders": order_list, "newOrders": new_orders}

@app.get("/order_by_id/{_id}")
async def order_by_id(_id: str):
    if not ObjectId.is_valid(_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    selected_order = await order_collection.find_one({"_id": ObjectId(_id)})
    if selected_order:
        return order_serializer(selected_order)
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.post("/create_order")
async def create_orders(order: Order):
    order_dict = order.dict()
    result = await order_collection.insert_one(order_dict)

    created_order = await order_collection.find_one({"_id": result.inserted_id})
    if created_order:
        return order_serializer(created_order)
    else:
        raise HTTPException(status_code=400, detail="Order creation failed")
    
@app.put("/update_order/{_id}")
async def update_orders(order: Order, _id: str):
    if not ObjectId.is_valid(_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    updated_order = await order_collection.update_one({"_id": ObjectId(_id)}, {"$set": order.dict(exclude_unset=True)})

    if updated_order.modified_count == 1:
        updated_result = await order_collection.find_one({"_id": ObjectId(_id)})
        return order_serializer(updated_result)
    else:
        raise HTTPException(status_code=404, detail="Order not found or no fields to update")
    
@app.delete("/delete_order")
async def delete_order(_id : str):
    if not ObjectId.is_valid(_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    selected_order = await order_collection.find_one({"_id":ObjectId(_id)})
    if selected_order is None:
        raise HTTPException(status_code=404,detail="order not found")
    deleted_order = await order_collection.delete_one({"_id":ObjectId(_id)})

    if deleted_order.deleted_count==1:
        return{"message":"Order deleted successfully"}
    else:
        raise HTTPException(status_code=500,detail="Failed to delete order")
    
@app.get("/search_orders")
async def search_orders(query: str = Query(...)):
    try:
        if ObjectId.is_valid(query):
            matching_orders = await order_collection.find({"_id": ObjectId(query)}).to_list(100)
        else:
            matching_orders = await order_collection.find(
                {"token": {"$regex": f"^{query}", "$options": "i"}}
            ).to_list(10)

        if not matching_orders:
            raise HTTPException(status_code=404, detail="No matching orders found")
        
        return [order_serializer(order) for order in matching_orders]

    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
