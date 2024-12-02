import logging
import logging.config
import yaml
from utils.generate_logs import generate_logs

# Inicializando arquivos de logs
generate_logs();

# Carregar configuração do arquivo YAML
with open('./services/configs.yaml', 'r') as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

# Criar loggers específicos
users_logger = logging.getLogger("users")
messages_logger = logging.getLogger("messages")
products_logger = logging.getLogger("products")
favorites_logger = logging.getLogger("favorites")
sales_logger = logging.getLogger("sales")

# Define os cabeçalhos para cada tabela
headers = {
    "users": ["id", "name", "age", "cpf", "gender", "phone_number", "address", "email", "password"],
    "messages": ["id", "user_sent_id", "user_received_id", "title", "description", "created_at"],
    "products": ["id", "seller_id", "title", "description", "category", "price", "quantity", "image_url"],
    "favorites": ["id", "user_id", "product_id"],
    "sales": ["id", "seller_id", "buyer_id", "product_id", "quantity", "created_at"]
};

# Nomeando diretório de armazenamento dos dados
storage_directory = "data";

# Nomeando arquivos CSV
file_names = {
    "users": "users.csv",
    "messages": "messages.csv",
    "products": "products.csv",
    "favorites": "favorites.csv",
    "sales": "sales.csv"
};

# Nomeando caminho para os arquivos CSV
path_directories = {
    "users": f"{storage_directory}/users.csv",
    "messages": f"{storage_directory}/messages.csv",
    "products": f"{storage_directory}/products.csv",
    "favorites": f"{storage_directory}/favorites.csv",
    "sales": f"{storage_directory}/sales.csv"
}