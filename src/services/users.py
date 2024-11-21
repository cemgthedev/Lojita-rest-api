from models import User
from utils.generate_id import generate_id
from services.configs import headers, file_names, path_directories, users_logger as logger
import csv
import hashlib
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


# Criar roteador
router = APIRouter()

# Rota para criar um novo usuário
@router.post("/users")
async def create_user(user: User):
    try:
        logger.info(f"Criando um novo usuário...")
        # Escrever os dados no arquivo CSV
        with open(path_directories["users"], mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers["users"]);
            
            # Gerando id aleatório
            user.id = generate_id(16);
            
            # Adicionar a linha com os dados do usuário
            writer.writerow(dict(user));
            
        logger.info(f"Usuário criado com sucesso!")
        return {"message": "User created successfully", "data": user};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/users/{id}")
async def get_user(id: str):
    try:
        logger.info(f"Buscando usuário com ID: {id}")
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    logger.info(f"Usuário encontrado: {row}")
                    return {"user": row};
            logger.info(f"Usuário com ID {id} não encontrado")
            return {"message": "User not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/users/{id}")
async def update_user(id: str, user: User):
    try:
        logger.info(f"Atualizando usuário com ID: {id}")
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
                
                logger.info(f"Usuário atualizado com sucesso!")
                return {"message": "User updated successfully"};
            else:
                logger.info(f"Usuário com ID {id} não encontrado")
                return {"message": "User not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/users/{id}")
async def delete_user(id: str):
    try:
        logger.info(f"Removendo usuário com ID: {id}")
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
                
                logger.info(f"Usuário removido com sucesso!")
                logger.info(f"Dados relacionados ao usuário removidos com sucesso!")
                return {"message": "User deleted successfully"};
            else:
                return {"message": "User not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/users")
async def get_users():
    try:
        logger.info(f"Buscando usuários...")
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            if len(rows) > 0:
                logger.info(f"Usuários encontrados com sucesso!")
                return {"users": rows};
            else:
                logger.info(f"Nenhum usuário encontrado!")
                return {"message": "No users found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/quantity/users")
async def get_quantity_users():
    try:
        logger.info(f"Buscando quantidade de usuários...")
        with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            logger.info(f"Quantidade de usuários encontrados: {len(rows)}");
            return {"quantity": len(rows)};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}");
        raise HTTPException(status_code=500, detail="XML file not found");
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}");
        raise HTTPException(status_code=500, detail="Internal server error");
    
@router.get("/hash256/users")
async def get_hash256_users():
    try:
        logger.info(f"Buscando hash256 de usuários...")
        with open(path_directories["users"], mode="rb") as file:
            hash256 = hashlib.sha256();
            
            # Tamanho de 100kb para calculo do hash
            kbytes = 100 * 1024
            
            # Lendo o arquivo em blocos de 100kb para evitar o uso de muita memória e atualizando cálculo do hash
            for block in iter(lambda: file.read(kbytes), b''):
                hash256.update(block);
            
            logger.info(f"Hash256 de usuários gerado com sucesso!");
            # Retornando o hash 256 em formato hexadecimal
            return {"hash256": hash256.hexdigest()};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/backup/users")
async def get_backup_users():
    try:
        logger.info(f"Criando backup de usuários...")
        # Define o nome do arquivo ZIP e o caminho
        zip_name = file_names["users"].replace(".csv", ".zip")
        zip_path = path_directories["users"].replace(".csv", ".zip")
        
        # Cria o arquivo ZIP e adiciona o CSV nele
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(path_directories["users"], arcname=file_names["users"])
        
        logger.info(f"Backup de usuários criado com sucesso!")
        # Retorna o arquivo ZIP para download
        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de usuários não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar um novo usuário: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")