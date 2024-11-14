from models import User
from utils.generate_id import generate_id
from services.configs import headers, path_directories
import csv
import hashlib

from fastapi import APIRouter

router = APIRouter()

# Rota para criar um novo usuário
@router.post("/users")
async def create_user(user: User):
    try:
        # Escrever os dados no arquivo CSV
        with open(path_directories["users"], mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers["users"]);
            
            # Gerando id aleatório
            user.id = generate_id(16);
            
            # Adicionar a linha com os dados do usuário
            writer.writerow(dict(user));
        return {"message": "User created successfully", "data": user};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/users/{id}")
async def get_user(id: str):
    try:
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    return {"user": row};
            return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)}

@router.put("/users/{id}")
async def update_user(id: str, user: User):
    try:
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            updated = False;
            
            for row in rows:
                if row["id"] == id:
                    row["name"] = user.name;
                    row["year"] = user.year;
                    row["cpf"] = user.cpf;
                    row["gender"] = user.gender;
                    row["phone_number"] = user.phone_number;
                    row["address"] = user.address;
                    row["email"] = user.email;
                    row["password"] = user.password;
                    
                    updated = True;
                    break;
            
            if updated:
                with open(path_directories["users"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["users"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "User updated successfully"};
            else:
                return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.delete("/users/{id}")
async def delete_user(id: str):
    try:
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            deleted = False;
            
            for row in rows:
                if row["id"] == id:
                    rows.remove(row);
                    deleted = True;
                    break;
            
            if deleted:
                with open(path_directories["users"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["users"]);
                    writer.writeheader();
                    writer.writerows(rows);
                
                # Removendo os dados relacionados ao usuário
                with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file);
                    rows = list(reader);
                    
                    for row in rows:
                        if row["user_sent_id"] == id or row["user_received_id"] == id:
                            rows.remove(row);
                    
                    with open(path_directories["messages"], mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.DictWriter(file, fieldnames=headers["messages"]);
                        writer.writeheader();
                        writer.writerows(rows);
                
                with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file);
                    rows = list(reader);
                    
                    for row in rows:
                        if row["seller_id"] == id:
                            rows.remove(row);
                    
                    with open(path_directories["products"], mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.DictWriter(file, fieldnames=headers["products"]);
                        writer.writeheader();
                        writer.writerows(rows);
                        
                with open(path_directories["favorites"], mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file);
                    rows = list(reader);
                    
                    for row in rows:
                        if row["user_id"] == id:
                            rows.remove(row);
                    
                    with open(path_directories["favorites"], mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.DictWriter(file, fieldnames=headers["favorites"]);
                        writer.writeheader();
                        writer.writerows(rows);
                    
                with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file);
                    rows = list(reader);
                    
                    for row in rows:
                        if row["seller_id"] == id or row["buyer_id"] == id:
                            rows.remove(row);
                    
                    with open(path_directories["sales"], mode="w", newline="", encoding="utf-8") as file:
                        writer = csv.DictWriter(file, fieldnames=headers["sales"]);
                        writer.writeheader();
                        writer.writerows(rows);
                    
                return {"message": "User deleted successfully"};
            else:
                return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)};
    
@router.get("/users")
async def get_users():
    try:
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            if len(rows) > 0:
                return {"users": rows};
            else:
                return {"message": "No users found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/quantity/users")
async def get_quantity_users():
    try:
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
        
            return {"quantity": len(rows)};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/hash256/users")
async def get_hash256_users():
    try:
        with open(path_directories["users"], mode="rb") as file:
            hash256 = hashlib.sha256();
            
            # Tamanho de 100kb para calculo do hash
            kbytes = 100 * 1024
            
            # Lendo o arquivo em blocos de 100kb para evitar o uso de muita memória e atualizando cálculo do hash
            for block in iter(lambda: file.read(kbytes), b''):
                hash256.update(block);
            
            # Retornando o hash 256 em formato hexadecimal
            return {"hash256": hash256.hexdigest()};
    except Exception as e:
        return {"error": str(e)}