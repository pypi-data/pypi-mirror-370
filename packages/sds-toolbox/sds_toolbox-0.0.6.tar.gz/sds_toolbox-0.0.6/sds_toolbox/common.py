import subprocess
import socket
import time
import os 
import pandas as pd
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from pydantic_settings import BaseSettings
from pydantic import validator, FilePath, computed_field, field_validator
from functools import lru_cache
import datetime
import humanize

class Settings(BaseSettings):
    # DATABASE_URL: str = "sqlite:////tmp/sql_app.db"
    # Ajoutez d'autres paramètres de configuration ici

    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_NAME: str | None = None
    GCP_PROJECT: str | None = None
    GCP_DB_ZONE: str | None = None
    GCP_DB_INSTANCE: str | None = None
    GCP_APP_NAME: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    GAE_RUNTIME: str | None = None
    FORCE_CLOUD: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    GCP_SERVICE_ACCOUNT: str | None = None

    @computed_field()
    def ENVIRONMENT(self) -> str:
        if None in [self.DB_USER, self.DB_PASS, self.DB_NAME]:
            return "LOCAL+SQLITE"
        elif any([self.GAE_RUNTIME, self.FORCE_CLOUD]):
            return "GCP"
        else:
            return "LOCAL+PROXY"

    @computed_field()
    def DATABASE_URL(self) -> str:
        if self.ENVIRONMENT == "LOCAL+SQLITE":
            return "sqlite:////tmp/test.db"
        elif self.ENVIRONMENT == "GCP":
            INSTANCE_CONNECTION_NAME = (
                f"{self.GCP_PROJECT}:{self.GCP_DB_ZONE}:{self.GCP_DB_INSTANCE}"
            )
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@/{self.DB_NAME}?host=/cloudsql/{INSTANCE_CONNECTION_NAME}"
        else:
            return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # ?charset=utf8mb4"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


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


def create_dir(path: str) -> str:
    """
    Create a local directory if it doesn't exist.

    Args:
        path (str): The directory path to be created.

    Returns:
        str: The path of the created directory.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(path, "- directory created")
    return path

def save_df_to_pickle(df: pd.DataFrame, path: str, filename: str) -> str:
    """
    Write a DataFrame into a pickle file.
    
    Args:
        data (pd.DataFrame): The DataFrame to be written to the pickle file.
        path (str): The directory where the pickle file will be saved.
        filename (str): The name of the pickle file (without the extension).
    
    Returns:
        str: The full path to the saved pickle file.
    """
    file_path = os.path.join(path, filename + '.pickle')
    df.to_pickle(file_path)
    return file_path

def save_df_to_csv(df: pd.DataFrame, path: str, filename: str) -> str:
    """
    Write a DataFrame into a csv file.
    
    Args:
        data (pd.DataFrame): The DataFrame to be written to the pickle file.
        path (str): The directory where the pickle file will be saved.
        filename (str): The name of the pickle file (without the extension).
    
    Returns:
        str: The full path to the saved csv file.
    """
    file_path = os.path.join(path, filename + '.csv')
    df.to_csv(
        os.path.join(file_path),
        sep=",",
        encoding="utf-8",
        index=False,
        decimal=".",
    )
    return file_path

def is_port_in_use(port : int) -> bool:
    """
    Function to check if a port is in use.

    Args:
    port: int, port number to check

    Returns:
    bool, True if port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def launch_proxy_with_readiness_check(uri) -> subprocess.Popen:
    """
    Function to launch the Cloud SQL Proxy and check for readiness.

    Args:
    None

    Returns:
    subprocess.Popen, proxy process if ready, None otherwise
    """
    proxy_command = [
        "cloud_sql_proxy",
        f"-instances={uri}"
    ]
    
    # Launch proxy and capture logs
    process = subprocess.Popen(
        proxy_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    # Check logs for readiness
    start_time = time.time()
    timeout = 120
    while time.time() - start_time < timeout:
        line = process.stderr.readline()  # Proxy logs readiness on stderr
        if "Ready for new connections" in line:
            print("Proxy is ready for new connections.")
            return process
        time.sleep(0.5)

    print("Proxy did not become ready within the timeout.")
    process.terminate()
    return None

def stop_proxy():
    """
    Function to stop the Cloud SQL Proxy.

    Args:
    None

    Returns:
    None
    """
    os.system("pkill -f cloud_sql_proxy")
    print("Cloud SQL Proxy stopped.")

def query_to_df(_SQL, batch_size: int = 10000) -> pd.DataFrame:
    """
    Function to execute a SQL query and return the results as a DataFrame in memory.
    Optimized for ~1M rows.
    """
    import datetime
    import humanize
    import pandas as pd

    try:
        t0 = datetime.datetime.now()
        db = next(get_db())
        results = db.execute(_SQL)

        # Charger tous les batches dans une liste (concat une seule fois à la fin)
        dataframes = []
        while True:
            batch = results.fetchmany(batch_size)
            if not batch:
                break
            df_batch = pd.DataFrame(batch, columns=results.keys())
            dataframes.append(df_batch)

        # Une seule concaténation à la fin
        df = pd.concat(dataframes, ignore_index=True, copy=False)

        # Optimisation mémoire : convertir les colonnes quand c’est possible
        for col in df.select_dtypes(include="object").columns:
            num_unique = df[col].nunique()
            if num_unique / len(df) < 0.5:  # si beaucoup de répétitions
                df[col] = df[col].astype("category")
        for col in df.select_dtypes(include="int").columns:
            df[col] = pd.to_numeric(df[col], downcast="integer")
        for col in df.select_dtypes(include="float").columns:
            df[col] = pd.to_numeric(df[col], downcast="float")

        db.close()
        t1 = datetime.datetime.now()
        delta_time = humanize.precisedelta(t1 - t0, minimum_unit="milliseconds")
        print(f"Query executed in {delta_time}")
        print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        return df

    except Exception as e:
        print(e)
        db.rollback()
        
# def query_to_df(_SQL, batch_size : int =10000) -> pd.DataFrame:
#     """
#     Function to execute a SQL query and return the results as a DataFrame.

#     Args:
#     _SQL: str, SQL query to execute
#     batch_size: int, size of each batch to fetch

#     Returns:
#     pd.DataFrame, DataFrame containing the results of the query
#     """
#     try:
#         t0 = datetime.datetime.now()
#         db = next(get_db())
#         results = db.execute(_SQL)
        
#         # Initialize an empty list to store DataFrames
#         dataframes = []
        
#         # Fetch data in batches
#         while True:
#             batch = results.fetchmany(batch_size)
#             if not batch:
#                 break
#             # Convert batch to DataFrame and append to list
#             dataframes.append(pd.DataFrame(batch, columns=results.keys()))
        
#         # Concatenate all the DataFrames
#         df = pd.concat(dataframes, ignore_index=True)
#         db.close()
#         t1 = datetime.datetime.now()
#         delta_time = humanize.precisedelta(t1 - t0, minimum_unit="milliseconds")
#         print(f"Query executed in {delta_time}")
#         return df
#     except Exception as e:
#         print(e)
#         db.rollback()
    

def lst_to_str(lst : list) -> str:
    """
    Convert a list of strings to a string of comma-separated strings.

    Args:
    lst: list, list of strings to convert

    Returns:
    str, string of comma-separated strings
    """
    return "'" + "','".join(lst) + "'"

def lst_of_int(lst : list) -> str:
    """
    Convert a list of strings to a string of comma-separated strings.

    Args:
    lst: list, list of strings to convert

    Returns:
    str, string of comma-separated strings
    """
    return ", ".join(map(str, lst))

def filter_lang(lang : str, table_prefix : str ='p') -> str:
    """
    Function to filter by lang.

    Args:
    lang: str, value of lang to filter by

    Returns:
    str, SQL condition to filter by
    """
    if lang:
        condition = f"AND {table_prefix}.lang NOT IN ({lst_to_str(lang)})"
    else:  
        condition = ""
    return condition

def filter_by_date(field : str, start_date : str, end_date : str) -> str:
    """
    Function to filter by date.

    Args:
    field: str, field to filter by
    start_date: str, start date to filter by
    end_date: str, end date to filter by

    Returns:
    str, SQL condition to filter by
    """
    if start_date and end_date:
        condition = f"AND {field} BETWEEN '{start_date}' AND '{end_date}'"
    elif start_date and not end_date:
        condition = f"AND {field} >= '{start_date}'"
    elif not start_date and end_date:
        condition = f"AND {field} <= '{end_date}'"
    else:
        condition = ""
    return condition
