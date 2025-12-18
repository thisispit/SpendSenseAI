import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(path):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    
    c.drawString(100, 750, "Bank Statement")
    c.drawString(100, 730, "Account: 123456789")
    
    # Table Header
    y = 700
    headers = ["Date", "Description", "Amount", "Category"]
    x_positions = [50, 150, 350, 450]
    
    for i, h in enumerate(headers):
        c.drawString(x_positions[i], y, h)
        
    y -= 20
    
    data = [
        ("2024-02-01", "Paycheck", "4000", "Income"),
        ("2024-02-05", "Rent", "-1200", "Housing"),
        ("2024-02-10", "Supermarket", "-200", "Food"),
        ("2024-02-15", "Online Course", "-50", "Education"),
        ("2024-02-20", "Cinema", "-30", "Entertainment"),
    ]
    
    for row in data:
        for i, item in enumerate(row):
            c.drawString(x_positions[i], y, item)
        y -= 20
        
    c.save()

if __name__ == "__main__":
    create_pdf("sample_statement.pdf")
