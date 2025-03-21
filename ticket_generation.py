import csv
import os
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Constants for layout
PAGE_WIDTH, PAGE_HEIGHT = A4
TICKET_WIDTH = PAGE_WIDTH / 4  # 4 tickets per row
TICKET_HEIGHT = PAGE_HEIGHT / 4  # 4 tickets per column
LOGO_PATH = "logo.jpeg"
LOGO_SIZE = 50
QR_SIZE = 100

def generate_qr_code(name, ticket_code, qr_filename):
    """Generate QR code embedding Name and Ticket Code."""
    qr_data = f"Noms : {name}\nCode : {ticket_code}"
    qr = qrcode.QRCode(version=2, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(qr_filename)

def create_ticket_page(csv_filename, output_pdf="tickets.pdf"):
    """Generate the PDF tickets from CSV file."""
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        beneficiaries = list(reader)

    c = canvas.Canvas(output_pdf, pagesize=A4)

    for i, beneficiary in enumerate(beneficiaries):
        name = beneficiary['Name']
        ticket_code = beneficiary['Ticket Code']

        row = (i % 16) // 4  # Determine row (0, 1, 2, or 3)
        col = (i % 16) % 4  # Determine column (0, 1, 2, or 3)

        x_offset = col * TICKET_WIDTH
        y_offset = PAGE_HEIGHT - (row + 1) * TICKET_HEIGHT

        # Draw Border
        c.rect(x_offset, y_offset, TICKET_WIDTH, TICKET_HEIGHT)

        # Add Logo LOWER in the center
        logo = ImageReader(LOGO_PATH)
        logo_x = x_offset + (TICKET_WIDTH - LOGO_SIZE) / 2
        logo_y = y_offset + TICKET_HEIGHT - 60
        c.drawImage(logo, logo_x, logo_y, width=LOGO_SIZE, height=LOGO_SIZE)

        # Display Ticket Code
        c.setFont("Helvetica-Bold", 12)
        text_x = x_offset + 10
        text_y = logo_y - 20
        c.drawString(text_x, text_y, f"Code : {ticket_code}")

        # Generate QR Code (Contains Name & Ticket Code)
        qr_filename = f"qr_{i}.png"
        generate_qr_code(name, ticket_code, qr_filename)

        # Add QR Code
        qr_x = x_offset + (TICKET_WIDTH - QR_SIZE) / 2
        qr_y = y_offset + 20
        qr = ImageReader(qr_filename)
        c.drawImage(qr, qr_x, qr_y, width=QR_SIZE, height=QR_SIZE)

        # Add "Q1-2025" at bottom-left
        c.setFont("Helvetica", 10)
        c.drawString(x_offset + 10, y_offset + 10, "Q1-2025")

        # Remove the QR image after embedding it
        os.remove(qr_filename)

        # Ensure a new page after every 16 tickets
        if (i + 1) % 16 == 0:
            c.showPage()

    # Ensure the last page is saved
    c.save()

# Run the function with the CSV file
create_ticket_page("beneficiaries.csv")
print("Successfully Done!")