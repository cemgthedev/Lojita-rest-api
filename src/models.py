from pydantic import BaseModel
from typing import Optional
from datetime import date
    
# Classe User
class User(BaseModel):
    id: Optional[str] = None
    name: str
    year: Optional[int] = None
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
    created_at: Optional[date] = None
    
class Product(BaseModel):
    id: Optional[str] = None
    seller_id: str
    title: str
    description: str
    price: float
    quantity: int
    image_url: Optional[str] = None