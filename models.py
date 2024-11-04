from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class OrderItem(BaseModel):
    name: str
    quantity: int
    price: int
    remarks: Optional[str] = None


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token: str
    status: str
    type: str
    table: Optional[str] = None
    Amount: str
    Remaining: str
    items: List[OrderItem]
class OrdersResponse(BaseModel):
    orders: List[Order]
    newOrders: List[Order]

class DiscriptionPoint(BaseModel):
    point:str
class MenuItem(BaseModel):
    dish: str

class Menu(BaseModel):
    lunch: list[MenuItem]
    dinner: list[MenuItem]

class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    img:str
    title:str
    owner:str
    cost:str
    distription:Optional[List[dict]]
    date_added:datetime=Field(default_factory=datetime.utcnow)
    menu:Menu

    
