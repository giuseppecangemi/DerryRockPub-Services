import pandas as pd
import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv 

load_dotenv()

def export_data_to_excel(database_url, excel_file_path):
    url = urlparse(database_url)
    conn = psycopg2.connect(
        database=url.path[1:],  #rimozione '/' all'inizio
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    query = "SELECT * FROM users;"
    df = pd.read_sql_query(query, conn)
    df.to_excel(excel_file_path, index=False)
    print(f"Dati esportati in {excel_file_path}.")

    #chiusura connessione
    conn.close()

if __name__ == "__main__":
    excel_file_path = 'dati_soci.xlsx'
    DATABASE_URL = os.getenv('DATABASE_URL')

    export_data_to_excel(DATABASE_URL, excel_file_path)
