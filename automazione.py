import pandas as pd
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from mail import send_email
from sqlalchemy import create_engine, text
from pdf import crea_pdf
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

pdf_output_folder = os.getenv("PDF_OUTPUT_FOLDER")
os.makedirs(pdf_output_folder, exist_ok=True)

output_excel_file = os.getenv("OUTPUT_EXCEL_FILE")

with engine.connect() as connection:
    query = "SELECT * FROM users;"
    df = pd.read_sql_query(query, connection)

# Se non esiste la colonna la inserisco
if 'inviato' not in df.columns:
    df.insert(0, 'inviato', '')

df['numero_tessera'] = pd.to_numeric(df['numero_tessera'], errors='coerce')

filtered_df = df[df['manuale'] != 'Sì']

massimo_valore = df.loc[df['manuale'] != 'Sì', 'numero_tessera'].max()
print("Massimo valore: " + str(massimo_valore))

numero_tessera = (massimo_valore + 1) if pd.notnull(massimo_valore) else 231001
print("NUMERO TESSERA: " + str(numero_tessera))

if numero_tessera >= 231400:
    raise ValueError("Errore: il range per il numero della tessera è stato superato.")

if any((df['numero_tessera'] == numero_tessera) & (df['manuale'] == 'Sì') & (df['inviato'] == 'SI')):
    numero_tessera += 1
    print(f"Numero tessera incrementato a: {numero_tessera}")

# LOGICA 
for index, row in df.iterrows():
    if row['approvato'] == 'SI' and pd.isnull(row['numero_tessera']):
        df.at[index, 'numero_tessera'] = numero_tessera  
        numero_tessera += 1  
    elif row['approvato'] == 'SI' and row['manuale'] == 'Sì':
        numero_tessera_man = row['numero_tessera']  
        df.at[index, 'numero_tessera'] = numero_tessera_man

soci_approvati = df[(df['approvato'] == 'SI') & (df['inviato'] != 'SI')]

for index, row in soci_approvati.iterrows():
    nome_str = row['nome'].split()[0]
    pdf_filename = os.path.join(pdf_output_folder, f'{nome_str}_{row["cognome"]}_{int(row["numero_tessera"])}.pdf')
    crea_pdf(int(row['numero_tessera']), nome_str, row['cognome'], str(pdf_filename)) 
    send_email(row['email'], pdf_filename) 
    df.at[index, 'inviato'] = 'SI'

# Ottimizzazione dell'aggiornamento del database
with engine.connect() as connection:
    try:
        # Prepara i dati da aggiornare
        update_data = []
        for _, row in df.iterrows():
            update_data.append({
                'numero_tessera': row['numero_tessera'],
                'inviato': row['inviato'],
                'id': row['id']
            })

        # Prepara la query di aggiornamento
        update_query = text("""
            UPDATE users
            SET numero_tessera = :numero_tessera,
                inviato = :inviato
            WHERE id = :id
        """)

        # Esegui l'aggiornamento in batch (utilizzando execute per parametri)
        result = connection.execute(update_query, update_data)
        print(f"Aggiornate righe: {result.rowcount}")
    except Exception as e:
        print(f"Errore durante l'aggiornamento batch: {e}")

# Esportazione dei dati su Excel
df.to_excel(output_excel_file, index=False)
print(f"Dati esportati in {output_excel_file}.")
print(f"Tessere generate e salvate nella cartella '{pdf_output_folder}'.")
