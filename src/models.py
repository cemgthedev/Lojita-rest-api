from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt
    
# Classe User
class User(BaseModel):
    id: Optional[str] = None
    name: str
    age: Optional[int] = None
    cpf: str
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    address: str
    email: str
    password: str

class Message(BaseModel):
    id: Optional[str] = None
    user_sent_id: str
    user_received_id: str
    title: str
    description: str
    created_at: Optional[dt] = None
    
class Product(BaseModel):
    id: Optional[str] = None
    seller_id: str
    title: str
    description: str
    category: str
    price: float
    quantity: int
    image_url: Optional[str] = None
    
class Favorite(BaseModel):
    id: Optional[str] = None
    user_id: str
    product_id: str
    
class Sale(BaseModel):
    id: Optional[str] = None
    seller_id: str
    buyer_id: str
    product_id: str
    quantity: int
    created_at: Optional[dt] = None