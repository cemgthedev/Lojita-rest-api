import datetime as dt
from models import Sale
from utils.generate_id import generate_id
from services.configs import headers, path_directories
import csv

from fastapi import APIRouter

router = APIRouter()

@router.post("/sales")
async def create_sale(sale: Sale):
    try:
        seller_exist = False;
        
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == sale.seller_id:
                    seller_exist = True;
                    break;
                
        buyer_exist = False;
        
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == sale.buyer_id:
                    buyer_exist = True;
                    break;
                
        product_exist = False;
        
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == sale.product_id:
                    product_exist = True;
                    break;
        
        if seller_exist and buyer_exist and product_exist:
            # Escrever os dados no arquivo CSV
            with open(path_directories["sales"], mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers["sales"]);
                
                # Gerando id aleatório
                sale.id = generate_id(16);
                
                # Adicionando data e hora da compra
                sale.created_at = dt.datetime.now();
                
                # Adicionar a linha com os dados do usuário
                writer.writerow(dict(sale));
            return {"message": "Sale created successfully", "data": sale};
        else:
            print(seller_exist, buyer_exist, product_exist)
            return {"message": "Seller, buyer or product not found"};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/sales/{id}")
async def get_sale(id: str):
    try:
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    return {"sale": row};
            return {"message": "Sale not found"};
    except Exception as e:
        return {"error": str(e)};
    
@router.delete("/sales/{id}")
async def delete_sale(id: str):
    try:
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            deleted = False;
            
            for row in rows:
                if row["id"] == id:
                    rows.remove(row);
                    deleted = True;
                    break;
            
            if deleted:
                with open(path_directories["sales"], mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=headers["sales"]);
                    writer.writeheader();
                    writer.writerows(rows);
                    
                return {"message": "Sale deleted successfully"};
            else:
                return {"message": "Sale not found"};
    except Exception as e:
        return {"error": str(e)};
    
@router.get("/sales")
async def get_sales():
    try:
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            if len(rows) > 0:
                return {"sales": rows};
            else:
                return {"message": "No sales found"};
    except Exception as e:
        return {"error": str(e)}