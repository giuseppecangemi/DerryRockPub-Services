from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import datetime
import os
from dotenv import load_dotenv  

load_dotenv()

def crea_pdf(numero_tessera, nome, cognome, path_out):
    original_pdf_path = os.getenv("ORIGINAL_PDF_PATH")
    font_path = os.getenv("FONT_PATH")
    
    if not original_pdf_path or not font_path:
        print("Errore: Percorsi dei file non specificati nelle variabili d'ambiente.")
        return

    data_corrente = datetime.datetime.now().strftime("%d/%m/%Y")

    if not os.path.exists(font_path):
        print(f"Font non trovato: {font_path}")
        return

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    pdfmetrics.registerFont(TTFont('Kredit', font_path))
    c.setFont("Kredit", 12)
    c.setFillColorRGB(0.8, 0.8, 0.8)  #grigio molto chiaro
    c.drawString(400, 720, f"{data_corrente}")  
    c.drawString(50, 145, f"{data_corrente}")  
    c.drawString(455, 700, f"{numero_tessera}")
    c.drawString(345, 670, f"{nome} {cognome}")  

    c.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)

    original_pdf = PdfReader(original_pdf_path)
    output_pdf = PdfWriter()

    for i in range(len(original_pdf.pages)):
        page = original_pdf.pages[i]
        page.merge_page(overlay_pdf.pages[0])
        output_pdf.add_page(page)

    with open(path_out, "wb") as output_stream:
        output_pdf.write(output_stream)

    print(f"PDF modificato salvato come '{path_out}'.")
