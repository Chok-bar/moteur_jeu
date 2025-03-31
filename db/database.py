from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import sys
import os
import socket

# Ajouter le répertoire parent au chemin de recherche pour pouvoir importer config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, logger

def is_hostname_resolvable(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

# Try the configured host first, fall back to localhost if not resolvable
db_host = DB_CONFIG['host']
if not is_hostname_resolvable(db_host) and db_host == "db":
    logger.warning(f"Could not resolve hostname '{db_host}', falling back to localhost")
    db_host = "localhost"

# Construire l'URL de connexion SQLAlchemy
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{db_host}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Créer le moteur SQLAlchemy
engine = create_engine(DB_URL, echo=False)

# Créer une factory de sessions
session_factory = sessionmaker(bind=engine)

# Créer un contexte de session thread-safe
Session = scoped_session(session_factory)

# Classe de base pour les modèles
Base = declarative_base()

def init_db():
    """Initialiser la base de données et créer les tables si elles n'existent pas."""
    try:
        # Importer les modèles pour s'assurer qu'ils sont enregistrés auprès de SQLAlchemy
        from .models import Party, Role, Player, PlayerInParty, Turn, PlayerPlay
        
        # Créer les tables dans la base de données
        Base.metadata.create_all(engine)
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise
