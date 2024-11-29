from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_facture_pdf(facture):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Facture ID: {facture['_id']}")
    c.drawString(100, 730, f"Date d'émission: {facture['date_emission']}")
    c.drawString(100, 710, f"Montant HT: {facture['montantHT']} TND")
    c.drawString(100, 690, f"TVA: {facture['TVA'] * 100}%")
    c.drawString(100, 670, f"Montant Total: {facture['total']} TND")
    c.drawString(100, 650, f"Statut: {facture['statut']}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
