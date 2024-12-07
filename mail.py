import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv  

load_dotenv()

def send_email(to_address, pdf_filename):
    from_address = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')

    #creazione messaggio
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = 'Tessera Associativa - Derry Rock Pub'

    #body
    body = 'In allegato trovi la tua tessera associativa.'
    msg.attach(MIMEText(body, 'plain'))

    #pdf allegato
    attachment = MIMEBase('application', 'octet-stream')
    with open(pdf_filename, 'rb') as attachment_file:
        attachment.set_payload(attachment_file.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_filename)}')
    msg.attach(attachment)

    #invio
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server: 
            server.starttls() 
            server.login(from_address, password) 
            server.send_message(msg) 
        print(f"Email inviata a {to_address} con successo!")
    except Exception as e:
        print(f"Errore nell'invio dell'email: {e}")
