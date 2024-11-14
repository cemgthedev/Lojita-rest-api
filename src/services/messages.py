import datetime as dt
from models import Message
from utils.generate_id import generate_id
from services.configs import headers, path_directories
import csv

from fastapi import APIRouter

router = APIRouter()

@router.post("/messages")
async def create_message(message: Message):
    try:
        sent_exist = False;
        receiver_exist = False;
        
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == message.user_sent_id:
                    sent_exist = True;
                if row["id"] == message.user_received_id:
                    receiver_exist = True;
                if sent_exist and receiver_exist:
                    break;
        
        if sent_exist and receiver_exist:
            with open(path_directories["messages"], mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers["messages"]);
                
                # Gerando id aleatório
                message.id = generate_id(16);
                # Adicionando data e hora do envio da mensagem
                message.created_at = dt.datetime.now();
                
                # Adicionar a linha com os dados da requisição
                writer.writerow(dict(message));
                
                return {"message": "Message created successfully", "data": message};
        else:
            return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)}

@router.get("/messages/{id}")
async def get_message(id: str):
    try:
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    return {"message": row};
            return {"message": "Message not found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.put("/messages/{id}")
async def update_message(id: str, message: Message):
    try:
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            updated = False;
            
            for row in rows:
                if row["id"] == id:
                    row["title"] = message.title;
                    row["description"] = message.description;
                    
                    updated = True;
                    break;
            
            if updated:
                with open(path_directories["messages"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["messages"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "Message updated successfully"};
            else:
                return {"message": "Message not found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.delete("/messages/{id}")
async def delete_message(id: str):
    try:
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            deleted = False;
            
            for row in rows:
                if row["id"] == id:
                    rows.remove(row);
                    deleted = True;
                    break;
            
            if deleted:
                with open(path_directories["messages"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["messages"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "Message deleted successfully"};
            else:
                return {"message": "Message not found"};
    except Exception as e:
        return {"error": str(e)};
    
@router.get("/messages")
async def get_messages():
    try:
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            if len(rows) > 0:
                return {"messages": rows};
            else:
                return {"message": "No messages found"};
    except Exception as e:
        return {"error": str(e)}