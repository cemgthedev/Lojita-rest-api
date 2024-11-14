from models import Favorite
from utils.generate_id import generate_id
from services.configs import headers, path_directories
import csv

from fastapi import APIRouter

router = APIRouter()

@router.post("/favorites")
async def create_favorite(favorite: Favorite):
    try:
        user_exist = False;
        
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == favorite.user_id:
                    user_exist = True;
                    break;
                
        product_exist = False;
        
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == favorite.product_id:
                    product_exist = True;
                    break;
        
        if user_exist and product_exist:
            # Escrever os dados no arquivo CSV
            with open(path_directories["favorites"], mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers["favorites"]);
                
                # Gerando id aleatório
                favorite.id = generate_id(16);
                
                # Adicionar a linha com os dados do usuário
                writer.writerow(dict(favorite));
            return {"message": "Favorite created successfully", "data": favorite};
        else:
            return {"message": "User or product not found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/favorites/{id}")
async def get_favorite(id: str):
    try:
        with open(path_directories["favorites"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    return {"favorite": row};
            return {"message": "Favorite not found"};
    except Exception as e:
        return {"error": str(e)};
    
@router.delete("/favorites/{id}")
async def delete_favorite(id: str):
    try:
        with open(path_directories["favorites"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            deleted = False;
            
            for row in rows:
                if row["id"] == id:
                    rows.remove(row);
                    deleted = True;
                    break;
            
            if deleted:
                with open(path_directories["favorites"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["favorites"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "Favorite deleted successfully"};
            else:
                return {"message": "Favorite not found"};
    except Exception as e:
        return {"error": str(e)};