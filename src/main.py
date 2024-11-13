import datetime as dt
from models import *
from utils.generate_tables import generate_tables
from utils.generate_id import generate_id
import csv

from fastapi import FastAPI

app = FastAPI()

# Define os cabeçalhos para cada tabela
headers = {
    "users": ["id", "name", "year", "cpf", "gender", "phone_number", "address", "email", "password"],
    "messages": ["id", "user_sent_id", "user_received_id", "title", "description", "created_at"],
    "products": ["id", "seller_id", "title", "description", "price", "quantity", "image_url"],
    "favorites": ["id", "user_id", "product_id"],
    "sales": ["id", "seller_id", "buyer_id", "product_id", "date"]
};

# Nomeando diretório de armazenamento dos dados
storage_directory = "data";

# Nomeando caminho para os arquivos CSV
path_directories = {
    "users": f"{storage_directory}/users.csv",
    "messages": f"{storage_directory}/messages.csv",
    "products": f"{storage_directory}/products.csv",
    "favorites": f"{storage_directory}/favorites.csv",
    "sales": f"{storage_directory}/sales.csv"
}

# Inicializando arquivos CSV
generate_tables(storage_directory, headers);

# Rota de teste
@app.get("/")
def read_root():
    return {"message": "Seja bem vindo a Lojita"}

# Rota para criar um novo usuário
@app.post("/users")
async def create_user(user: User):
    try:
        # Escrever os dados no arquivo CSV
        with open(path_directories["users"], mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers["users"]);
            
            # Gerando id aleatório
            user.id = generate_id(16);
            
            # Adicionar a linha com os dados do usuário
            writer.writerow(dict(user));
        # Aqui, `user` é uma instância da classe `User` contendo os dados da requisição
        return {"message": "User created successfully", "data": user};
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/users/{id}")
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

@app.put("/users/{id}")
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
    
@app.delete("/users/{id}")
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
                    
                return {"message": "User deleted successfully"};
            else:
                return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)};
    
@app.post("/messages")
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

@app.get("/messages/{id}")
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
    
@app.put("/messages/{id}")
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
    
@app.delete("/messages/{id}")
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
    
@app.post("/products")
async def create_product(product: Product):
    try:
        seller_exist = False;
        
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == product.seller_id:
                    seller_exist = True;
                    break;
        
        if seller_exist:
            # Escrever os dados no arquivo CSV
            with open(path_directories["products"], mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers["products"]);
                
                # Gerando id aleatório
                product.id = generate_id(16);
                
                # Adicionar a linha com os dados do usuário
                writer.writerow(dict(product));
            # Aqui, `user` é uma instância da classe `User` contendo os dados da requisição
            return {"message": "Product created successfully", "data": product};
        else:
            return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/products/{id}")
async def get_product(id: str):
    try:
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    return {"product": row};
            return {"message": "Product not found"};
    except Exception as e:
        return {"error": str(e)};
    
@app.put("/products/{id}")
async def update_product(id: str, product: Product):
    try:
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            updated = False;
            
            for row in rows:
                if row["id"] == id:
                    row["title"] = product.title;
                    row["description"] = product.description;
                    row["price"] = product.price;
                    row["quantity"] = product.quantity;
                    row["image_url"] = product.image_url;
                    
                    updated = True;
                    break;
            
            if updated:
                with open(path_directories["products"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["products"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "Product updated successfully"};
            else:
                return {"message": "Product not found"};
    except Exception as e:
        return {"error": str(e)};
    
@app.delete("/products/{id}")
async def delete_product(id: str):
    try:
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            deleted = False;
            
            for row in rows:
                if row["id"] == id:
                    rows.remove(row);
                    deleted = True;
                    break;
            
            if deleted:
                with open(path_directories["products"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["products"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "Product deleted successfully"};
            else:
                return {"message": "Product not found"};
    except Exception as e:
        return {"error": str(e)};