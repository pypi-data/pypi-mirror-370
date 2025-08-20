import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from settings import get_settings

settings = get_settings()

if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    db.Base = Base
    try:
        db.execute(text("SELECT 1"))
        yield db

    except OperationalError as e:

        ## Erreur de connexion Réseau
        if "connection to server" in str(e):
            _msg = "⛓️‍💥 Erreur de connexion réseau à la base de données."
            if "PROXY" in settings.ENVIRONMENT:
                _msg += " Vérifiez que le proxy est bien lancé."
        
        ## Erreur d'authentification
        if "password authentication failed" in str(e):
            _msg = "🔑 Erreur d'authentification à la base de données."
            _msg += " Vérifiez que les identifiants sont bien configurés."
            _msg += " (DB_USER : {}, DB_PASS : {}, DB_NAME : {})".format(settings.DB_USER, settings.DB_PASS, settings.DB_NAME)

        _msg += f" Erreur: {e}"
        logging.error(_msg)
        raise Exception(_msg)

    finally:
        db.close()

def get_scoped_session():
    logging.debug("Creating scoped session...")
    return scoped_session(SessionLocal)