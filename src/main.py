from models import *
from utils.generate_tables import generate_tables
from utils.generate_logs import generate_logs
from services.configs import headers, storage_directory
from services.users import router as users_router
from services.messages import router as messages_router
from services.products import router as products_router
from services.favorites import router as favorites_router
from services.sales import router as sales_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Origens permitidas
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os headers
)

# Inicializando arquivos CSV
generate_tables(storage_directory, headers);

# Rota de teste
@app.get("/")
def read_root():
    return {"message": "Seja bem vindo a Lojita"}

# Incluindo rotas de usuários
app.include_router(users_router);

# Incluindo rotas de mensagens
app.include_router(messages_router);

# Incluindo rotas de produtos
app.include_router(products_router);

# Incluindo rotas de favoritos
app.include_router(favorites_router);

# Incluindo rotas de vendas
app.include_router(sales_router);