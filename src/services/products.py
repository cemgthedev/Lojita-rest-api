from models import Product
from utils.generate_id import generate_id
from services.configs import headers, file_names, path_directories, products_logger as logger
import csv
import hashlib
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/products")
async def create_product(product: Product):
    try:
        logger.info(f"Criando um novo produto...");
        
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
                
            logger.info(f"Produto criado com sucesso!");
            return {"message": "Product created successfully", "data": product};
        else:
            logger.warning(f"Usuário do produto não encontrado!");
            return {"message": "User not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/products/{id}")
async def get_product(id: str):
    try:
        logger.info(f"Buscando produto com ID: {id}")
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    logger.info(f"Produto encontrado: {row}")
                    return {"product": row};
            
            logger.warning(f"Produto com ID: {id} não encontrado");
            return {"message": "Product not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao buscar um produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/products/{id}")
async def update_product(id: str, product: Product):
    try:
        logger.info(f"Atualizando produto com ID: {id}")
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            updated = False;
            
            for row in rows:
                if row["id"] == id:
                    row["title"] = product.title;
                    row["description"] = product.description;
                    row["category"] = product.category;
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
                
                logger.info(f"Produto atualizado com sucesso!");
                return {"message": "Product updated successfully"};
            else:
                logger.warning(f"Produto com ID: {id} não encontrado");
                return {"message": "Product not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao atualizar um produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/products/{id}")
async def delete_product(id: str):
    try:
        logger.info(f"Deletando produto com ID: {id}")
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
                
                logger.info(f"Produto deletado com sucesso!");
                return {"message": "Product deleted successfully"};
            else:
                logger.warning(f"Produto com ID: {id} não encontrado");
                return {"message": "Product not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao remover um produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/products")
async def get_products():
    try:
        logger.info(f"Buscando produtos...")
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            if len(rows) > 0:
                logger.info(f"Produtos encontrados com sucesso!")
                return {"products": rows};
            else:
                logger.warning(f"Nenhum produto encontrado!")
                return {"message": "No products found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/quantity/products")
async def get_quantity_products():
    try:
        logger.info(f"Calculando quantidade de produtos...");
        with open(path_directories["products"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            logger.info(f"Quantidade de produtos encontrados: {len(rows)}")
            return {"quantity": len(rows)};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao calcular quantidade de produtos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/hash256/products")
async def get_hash256_products():
    try:
        logger.info(f"Calculando hash256 de produtos...");
        with open(path_directories["products"], mode="rb") as file:
            hash256 = hashlib.sha256();
            
            # Tamanho de 100kb para calculo do hash
            kbytes = 100 * 1024
            
            # Lendo o arquivo em blocos de 100kb para evitar o uso de muita memória e atualizando cálculo do hash
            for block in iter(lambda: file.read(kbytes), b''):
                hash256.update(block);
            
            logger.info(f"Hash256 de produtos gerado com sucesso! Hash: {hash256.hexdigest()}");
            # Retornando o hash 256 em formato hexadecimal
            return {"hash256": hash256.hexdigest()};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao calcular hash256 de produtos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/backup/products")
async def get_backup_products():
    try:
        logger.info(f"Criando backup de produtos...")
        
        # Define o nome do arquivo ZIP e o caminho
        zip_name = file_names["products"].replace(".csv", ".zip")
        zip_path = path_directories["products"].replace(".csv", ".zip")
        
        # Cria o arquivo ZIP e adiciona o CSV nele
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(path_directories["products"], arcname=file_names["products"])

        logger.info(f"Backup de produtos criado com sucesso!")
        # Retorna o arquivo ZIP para download
        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de produtos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar backup de produtos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")