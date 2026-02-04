# backend/utils.py
from fpdf import FPDF

def generate_pdf_from_text(summary_text: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    # Cleaning markdown so it looks professional in the final report
    clean_text = summary_text.replace("**", "").replace("* ", "- ")
    
    # multi_cell handles line wrapping for long AI summaries
    pdf.multi_cell(0, 10, txt=clean_text)
    
    # Return as bytes for the API response
    return pdf.output(dest='S').encode('latin-1', errors='replace')
