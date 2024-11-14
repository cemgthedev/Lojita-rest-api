import datetime as dt
from models import Sale
from utils.generate_id import generate_id
from services.configs import headers, file_names, path_directories
import csv
import hashlib
import zipfile

from fastapi import APIRouter
from fastapi.responses import FileResponse

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
    
@router.get("/quantity/sales")
async def get_quantity_sales():
    try:
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
        
            return {"quantity": len(rows)};
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/hash256/sales")
async def get_hash256_sales():
    try:
        with open(path_directories["sales"], mode="rb") as file:
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
    
@router.get("/backup/sales")
async def get_backup_sales():
    try:
        # Define o nome do arquivo ZIP e o caminho
        
        zip_name = file_names["sales"].replace(".csv", ".zip")
        zip_path = path_directories["sales"].replace(".csv", ".zip")
        
        # Cria o arquivo ZIP e adiciona o CSV nele
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(path_directories["sales"], arcname=file_names["sales"])

        # Retorna o arquivo ZIP para download
        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )
    except Exception as e:
        return {"error": str(e)}