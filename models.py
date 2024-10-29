from pydantic import BaseModel, Field
from typing import List, Optional
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
