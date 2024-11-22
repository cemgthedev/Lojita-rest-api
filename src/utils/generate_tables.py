import csv
import os

# Define os cabeçalhos para cada tabela
headers = {
    "users": ["id", "name", "age", "cpf", "gender", "phone_number", "address", "email", "password"],
    "messages": ["id", "user_sent_id", "user_received_id", "title", "description"],
    "products": ["id", "seller_id", "title", "description", "price", "quantity"],
    "favorites": ["id", "user_id", "product_id"],
    "sales": ["id", "seller_id", "buyer_id", "product_id", "date"]
}

# Função para criar um arquivo CSV com apenas os cabeçalhos, se o arquivo não existir
def create_csv(directory_name, filename, header):
    filepath = os.path.join(directory_name, filename)  # Caminho completo para o arquivo
    if not os.path.exists(filepath):  # Verifica se o arquivo já existe
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file);
            writer.writerow(header);
        print(f"Arquivo '{filepath}' criado com os cabeçalhos: {header}");
    else:
        print(f"Arquivo '{filepath}' já existe. Nenhuma ação necessária.");

def generate_tables(directory_name, headers):
    # Cria o diretório "data" se ele ainda não existir
    os.makedirs(directory_name, exist_ok=True);
    
    print("Gerando arquivos CSV...");
    # Cria um arquivo CSV para cada tabela
    for table, header in headers.items():
        create_csv(directory_name, f"{table}.csv", header);