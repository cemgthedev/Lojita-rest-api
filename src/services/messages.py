from datetime import datetime as dt
from models import Message
from utils.generate_id import generate_id
from services.configs import headers, file_names, path_directories, messages_logger as logger
import csv
import hashlib
import zipfile

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/messages")
async def create_message(message: Message):
    try:
        logger.info(f"Criando uma nova mensagem...");
        
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
                message.created_at = dt.now();
                
                # Adicionar a linha com os dados da requisição
                writer.writerow(dict(message));
                
                logger.info(f"Mensagem criada com sucesso!");
                return {"message": "Message created successfully", "data": message};
        else:
            if not sent_exist:
                logger.warning(f"Usuário com ID {message.user_sent_id} não encontrado");
            if not receiver_exist:
                logger.warning(f"Usuário com ID {message.user_received_id} não encontrado");
            return {"message": "User not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar uma nova mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/messages/{id}")
async def get_message(id: str):
    try:
        logger.info(f"Buscando mensagem com ID: {id}")
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            for row in reader:
                if row["id"] == id:
                    logger.info(f"Mensagem encontrada: {row}")
                    return {"message": row};
            logger.warning(f"Mensagem com ID {id} não encontrada")
            return {"message": "Message not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao buscar uma mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/messages/{id}")
async def update_message(id: str, message: Message):
    try:
        logger.info(f"Atualizando mensagem com ID: {id}")
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
                
                logger.info(f"Mensagem atualizada com sucesso!");
                return {"message": "Message updated successfully"};
            else:
                logger.warning(f"Mensagem com ID {id} não encontrada")
                return {"message": "Message not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao atualizar uma mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/messages/{id}")
async def delete_message(id: str):
    try:
        logger.info(f"Removendo mensagem com ID: {id}")
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
                
                logger.info(f"Mensagem removida com sucesso!");
                return {"message": "Message deleted successfully"};
            else:
                logger.warning(f"Mensagem com ID {id} não encontrada")
                return {"message": "Message not found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao remover uma mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/messages")
async def get_messages(
    subject: str = Query(None, description="Assunto da mensagem"),
    min_datetime: dt = Query(None, description="Data e horário mínimo da mensagem"),
    max_datetime: dt = Query(None, description="Data e horário máximo da mensagem"),
    fst_user_id: str = Query(None, description="ID do primeiro usuário da mensagem"),
    snd_user_id: str = Query(None, description="ID do segundo usuário da mensagem")
):
    try:
        logger.info(f"Buscando mensagens...")
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            filtered_rows = [
                row for row in rows
                if (
                    (subject is None or subject.lower() in (row["title"].lower() + row["description"].lower())) and
                    (min_datetime is None or min_datetime <= dt.fromisoformat(row["created_at"])) and
                    (max_datetime is None or max_datetime >= dt.fromisoformat(row["created_at"])) and
                    (
                        fst_user_id is None or snd_user_id is None or
                        (
                            fst_user_id == row["user_sent_id"] and snd_user_id == row["user_received_id"] or
                            fst_user_id == row["user_received_id"] and snd_user_id == row["user_sent_id"]
                        )
                    )
                )
            ]
            
            # Ordenação decrescente das mensagens por data (semelhante a ordem cronológica de um chat)
            filtered_rows.sort(key=lambda x: dt.fromisoformat(x["created_at"]), reverse=True)
            
            if len(filtered_rows) > 0:
                logger.info(f"Mensagens encontradas com sucesso!")
                return {"messages": filtered_rows};
            else:
                logger.info(f"Nenhuma mensagem encontrada!")
                return {"message": "No messages found"};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao buscar mensagens: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/quantity/messages")
async def get_quantity_messages():
    try:
        logger.info(f"Calculando quantidade de mensagens...");
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            logger.info(f"Quantidade de mensagens encontradas: {len(rows)}")
            return {"quantity": len(rows)};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao calcular quantidade de mensagens: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/hash256/messages")
async def get_hash256_messages():
    try:
        logger.info(f"Calculando hash256 de mensagens...");
        with open(path_directories["messages"], mode="rb") as file:
            hash256 = hashlib.sha256();
            
            # Tamanho de 100kb para calculo do hash
            kbytes = 100 * 1024
            
            # Lendo o arquivo em blocos de 100kb para evitar o uso de muita memória e atualizando cálculo do hash
            for block in iter(lambda: file.read(kbytes), b''):
                hash256.update(block);
            
            logger.info(f"Hash256 de mensagens gerado com sucesso! Hash: {hash256.hexdigest()}");
            # Retornando o hash 256 em formato hexadecimal
            return {"hash256": hash256.hexdigest()};
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao calcular hash256 de mensagens: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/backup/messages")
async def get_backup_messages():
    try:
        logger.info(f"Criando backup de mensagens...")
        
        # Define o nome do arquivo ZIP e o caminho
        zip_name = file_names["messages"].replace(".csv", ".zip")
        zip_path = path_directories["messages"].replace(".csv", ".zip")
        
        # Cria o arquivo ZIP e adiciona o CSV nele
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(path_directories["messages"], arcname=file_names["messages"])

        logger.info(f"Backup de mensagens criado com sucesso!")
        # Retorna o arquivo ZIP para download
        return FileResponse(
            path=zip_path,
            filename=zip_name,
            media_type="application/zip"
        )
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")
    except Exception as e:
        logger.error(f"Erro ao criar backup de mensagens: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/chats/{id}")
async def get_chats(id: str):
    try:
        logger.info(f"Buscando chats...")
        with open(path_directories["messages"], mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file);
            rows = list(reader);
            
            # Filtra os IDs únicos conforme a lógica
            filtered_ids = set()
            for row in rows:
                if row["user_sent_id"] == id:
                    filtered_ids.add(row["user_received_id"])
                elif row["user_received_id"] == id:
                    filtered_ids.add(row["user_sent_id"])

            if filtered_ids:
                logger.info("Chats encontrados com sucesso!")
                chats = list(filtered_ids)
                
                with open(path_directories["users"], mode="r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file);
                    rows = list(reader);
                    
                    users = [
                        {
                            "id": row["id"], 
                            "name": row["name"],
                            "age": row["age"],
                            "phone_number": row["phone_number"],
                            "gender": row["gender"],
                            "address": row["address"],
                        }
                        for row in rows if row["id"] in chats
                    ]
                    
                    logger.info("Chats retornados com sucesso!")
                    return {"chats": users}
            else:
                logger.warning("Nenhum chat encontrado!")
                return {"message": "No chats found"}
    except FileNotFoundError as e:
        logger.error(f"Arquivo .csv de mensagens não encontrado: {e}")
        raise HTTPException(status_code=500, detail="XML file not found")