from models import Product
from utils.generate_id import generate_id
from services.configs import headers, path_directories
import csv

from fastapi import APIRouter

router = APIRouter()

@router.post("/products")
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
            return {"message": "Product created successfully", "data": product};
        else:
            return {"message": "User not found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/products/{id}")
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
    
@router.put("/products/{id}")
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
    
@router.delete("/products/{id}")
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