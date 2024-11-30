from datetime import datetime as dt
from models import Sale
from utils.generate_id import generate_id
from services.configs import headers, file_names, path_directories, sales_logger as logger
import csv
import hashlib
import zipfile

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/sales")
async def create_sale(sale: Sale):
    try:
        logger.info(f"Criando uma nova venda...");
        
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
                sale.created_at = dt.now();
                
                # Adicionar a linha com os dados do usuário
                writer.writerow(dict(sale));
                
            logger.info(f"Venda criada com sucesso!");
            return {"message": "Sale created successfully", "data": sale};
        else:
            if not seller_exist:
                logger.warning(f"Vendedora não encontrada");
            if not buyer_exist:
                logger.warning(f"Comprador não encontrado");
            if not product_exist:
                logger.warning(f"Produto não encontrado");
            return {"message": "Seller, buyer or product not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar uma nova venda: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/sales/{id}")
async def get_sale(id: str):
    try:
        logger.info(f"Buscando venda com ID: {id}")
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    logger.info(f"Venda encontrada: {row}")
                    return {"sale": row};
                
            logger.warning(f"Venda com ID {id} não encontrada")
            return {"message": "Sale not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao buscar uma venda: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/sales/{id}")
async def delete_sale(id: str):
    try:
        logger.info(f"Removendo venda com ID: {id}")
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
                
                logger.info(f"Venda removida com sucesso!");
                return {"message": "Sale deleted successfully"};
            else:
                logger.warning(f"Venda com ID {id} não encontrada")
                return {"message": "Sale not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao remover uma venda: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/sales")
async def get_sales(
    seller_id: str = Query(None, description="Id do vendedor"),
    buyer_id: str = Query(None, description="Id do comprador"),
    min_quantity: int = Query(None, description="Quantidade mínima de produtos"),
    max_quantity: int = Query(None, description="Quantidade máxima de produtos"),
    min_datetime: dt = Query(None, description="Data e horário mínimo da compra"),
    max_datetime: dt = Query(None, description="Data e horário máximo da compra")
):
    try:
        logger.info(f"Buscando todas as vendas");
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            filtered_rows = [
                row for row in rows
                if (seller_id is None or seller_id == row["seller_id"]) and
                   (buyer_id is None or buyer_id == row["buyer_id"]) and
                   (min_quantity is None or min_quantity <= int(row["quantity"])) and
                   (max_quantity is None or max_quantity >= int(row["quantity"])) and
                   (min_datetime is None or min_datetime <= dt.fromisoformat(row["created_at"])) and
                   (max_datetime is None or max_datetime >= dt.fromisoformat(row["created_at"]))
            ]
            
            if len(filtered_rows) > 0:
                logger.info(f"Vendas encontradas com sucesso!")
                return {"sales": filtered_rows};
            else:
                logger.warning(f"Nenhuma venda encontrada");
                return {"message": "No sales found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao buscar vendas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/quantity/sales")
async def get_quantity_sales():
    try:
        logger.info(f"Calculando quantidade de vendas...");
        with open(path_directories["sales"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
        
            logger.info(f"Quantidade de vendas encontradas: {len(rows)}");
            return {"quantity": len(rows)};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao calcular quantidade de vendas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/hash256/sales")
async def get_hash256_sales():
    try:
        logger.info(f"Calculando hash256 de vendas...");
        with open(path_directories["sales"], mode="rb") as file:
            hash256 = hashlib.sha256();
            
            # Tamanho de 100kb para calculo do hash
            kbytes = 100 * 1024
            
            # Lendo o arquivo em blocos de 100kb para evitar o uso de muita memória e atualizando cálculo do hash
            for block in iter(lambda: file.read(kbytes), b''):
                hash256.update(block);
            
            logger.info(f"Hash256 de vendas gerado com sucesso! Hash: {hash256.hexdigest()}");
            # Retornando o hash 256 em formato hexadecimal
            return {"hash256": hash256.hexdigest()};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao calcular hash256 de vendas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/backup/sales")
async def get_backup_sales():
    try:
        logger.info(f"Criando backup de vendas...")
        
        # Define o nome do arquivo ZIP e o caminho
        zip_name = file_names["sales"].replace(".csv", ".zip")
        zip_path = path_directories["sales"].replace(".csv", ".zip")
        
        # Cria o arquivo ZIP e adiciona o CSV nele
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(path_directories["sales"], arcname=file_names["sales"])

        logger.info(f"Backup de vendas criado com sucesso!");
        # Retorna o arquivo ZIP para download
        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de vendas não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar backup de vendas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")