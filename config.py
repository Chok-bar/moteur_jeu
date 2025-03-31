import logging
import os

# Configuration de la base de données
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),  
    "database": os.environ.get("DB_NAME", "tp_info"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "postgres"),
    "port": os.environ.get("DB_PORT", "5432")
}

# Configuration du serveur gRPC
SERVER_PORT = int(os.environ.get("SERVER_PORT", "9990"))

# Configuration du jeu
BOARD_SIZE = 10
MAX_PLAYERS_PER_GAME = 8

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
