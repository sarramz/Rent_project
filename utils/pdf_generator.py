from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

def generate_facture_pdf(facture: dict) -> BytesIO:
    try:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.drawString(100, 800, f"Facture N°: {facture.get('numero_facture', 'N/A')}")
        pdf.drawString(100, 780, f"Date d'émission: {facture.get('date_emission', 'N/A')}")
        pdf.drawString(100, 760, f"ID Locataire: {facture.get('locataire_id', 'N/A')}")
        pdf.drawString(100, 740, f"ID Réservation: {facture.get('reservation_id', 'N/A')}")
        pdf.drawString(100, 720, f"Montant HT: {facture.get('montantHT', 0):.2f} €")
        pdf.drawString(100, 700, f"TVA: {facture.get('TVA', 0) * 100:.0f} %")
        pdf.drawString(100, 680, f"Montant Total: {facture.get('total', 0):.2f} €")
        pdf.drawString(100, 660, f"Statut: {facture.get('statut', 'N/A')}")
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise ValueError(f"Error generating PDF: {e}")
