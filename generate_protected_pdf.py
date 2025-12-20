from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pdfencrypt import StandardEncryption

def create_protected_pdf(path, pwd):
    enc = StandardEncryption(pwd, canPrint=1, canCopy=1, canModify=1)
    c = canvas.Canvas(path, pagesize=letter, encrypt=enc)
    
    c.drawString(100, 750, "Protected Bank Statement")
    c.drawString(100, 730, "Account: 123456789")
    
    # Table Header
    y = 700
    headers = ["Date", "Description", "Amount", "Category"]
    x_positions = [50, 150, 350, 450]
    
    for i, h in enumerate(headers):
        c.drawString(x_positions[i], y, h)
    
    y -= 20
    c.drawString(50, y, "2024-03-01")
    c.drawString(150, y, "Secret Transaction")
    c.drawString(350, y, "999")
    c.drawString(450, y, "Secret")
    
    c.save()
    print(f"Created {path} with password '{pwd}'")

if __name__ == "__main__":
    create_protected_pdf("protected.pdf", "secret123")
