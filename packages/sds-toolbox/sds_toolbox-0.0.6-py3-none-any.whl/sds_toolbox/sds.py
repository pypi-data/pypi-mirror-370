import subprocess
import socket
import time
import os 
import pandas as pd
from db import get_db

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

def query_to_df(_SQL, batch_size : int =10000) -> pd.DataFrame:
    """
    Function to execute a SQL query and return the results as a DataFrame.

    Args:
    _SQL: str, SQL query to execute
    batch_size: int, size of each batch to fetch

    Returns:
    pd.DataFrame, DataFrame containing the results of the query
    """
    try:
        db = next(get_db())
        results = db.execute(_SQL)
        
        # Initialize an empty list to store DataFrames
        dataframes = []
        
        # Fetch data in batches
        while True:
            batch = results.fetchmany(batch_size)
            if not batch:
                break
            # Convert batch to DataFrame and append to list
            dataframes.append(pd.DataFrame(batch, columns=results.keys()))
        
        # Concatenate all the DataFrames
        df = pd.concat(dataframes, ignore_index=True)
        db.close()
        return df
    except Exception as e:
        print(e)
        db.rollback()
    

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
