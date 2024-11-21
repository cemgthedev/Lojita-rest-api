from models import Favorite
from utils.generate_id import generate_id
from services.configs import headers, file_names, path_directories, favorites_logger as logger
import csv
import hashlib
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/favorites")
async def create_favorite(favorite: Favorite):
    try:
        logger.info(f"Criando um novo favorito");
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
                
            logger.info(f"Favorito criado com sucesso!");
            return {"message": "Favorite created successfully", "data": favorite};
        else:
            logger.info(f"Usuário ou produto do favorito não encontrado!");
            return {"message": "User or product not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/favorites/{id}")
async def get_favorite(id: str):
    try:
        logger.info(f"Buscando favorito com ID: {id}");
        with open(path_directories["favorites"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    logger.info(f"Favorito encontrado: {row}");
                    return {"favorite": row};
            
            logger.info(f"Favorito com ID {id} não encontrado");
            return {"message": "Favorite not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/favorites/{id}")
async def delete_favorite(id: str):
    try:
        logger.info(f"Removendo favorito com ID: {id}");
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
                
                logger.info(f"Favorito removido com sucesso!");
                return {"message": "Favorite deleted successfully"};
            else:
                logger.info(f"Favorito com ID {id} não encontrado");
                return {"message": "Favorite not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/favorites")
async def get_favorites():
    try:
        logger.info(f"Buscando todos os favoritos");
        with open(path_directories["favorites"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            if len(rows) > 0:
                logger.info(f"Quantidade de favoritos encontrados: {len(rows)}")
                return {"favorites": rows};
            else:
                logger.info(f"Nenhum favorito encontrado");
                return {"message": "No favorites found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/quantity/favorites")
async def get_quantity_favorites():
    logger.info(f"Buscando quantidade de favoritos");
    try:
        with open(path_directories["favorites"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
        
            logger.info(f"Quantidade de favoritos encontradas: {len(rows)}")
            return {"quantity": len(rows)};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/hash256/favorites")
async def get_hash256_favorites():
    try:
        logger.info(f"Buscando hash256 de favoritos");
        with open(path_directories["favorites"], mode="rb") as file:
            hash256 = hashlib.sha256();
            
            # Tamanho de 100kb para calculo do hash
            kbytes = 100 * 1024
            
            # Lendo o arquivo em blocos de 100kb para evitar o uso de muita memória e atualizando cálculo do hash
            for block in iter(lambda: file.read(kbytes), b''):
                hash256.update(block);
            
            logger.info(f"Hash256 de favoritos gerado com sucesso!");
            # Retornando o hash 256 em formato hexadecimal
            return {"hash256": hash256.hexdigest()};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/backup/favorites")
async def get_backup_favorites():
    try:
        logger.info(f"Criando backup de favoritos...")
        
        # Define o nome do arquivo ZIP e o caminho
        zip_name = file_names["favorites"].replace(".csv", ".zip")
        zip_path = path_directories["favorites"].replace(".csv", ".zip")
        
        # Cria o arquivo ZIP e adiciona o CSV nele
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(path_directories["favorites"], arcname=file_names["favorites"])

        logger.info(f"Backup de favoritos criado com sucesso!")
        # Retorna o arquivo ZIP para download
        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de favoritos não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo favorito: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")