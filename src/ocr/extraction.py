import os
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

from pathlib import Path

PDF_PATH = "../../data/raw/CONTRATO_AP000000718.pdf"
OUTPUT_PATH = "../../data/ocr/CONTRATO_AP000000718_ocr.txt"


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from each page of the PDF.:
    """
    print(f"[*] Loading PDF: {pdf_path}")

    full_text = []
    for page_number in range(get_pdf_page_count(pdf_path)):
        print(f"[*] Processing page {page_number + 1}")
        page_text = ocr_page(pdf_path, page_number)
        full_text.append(page_text)
    
    return "\n\n".join(full_text)

def get_pdf_page_count(pdf_path: str) -> int:
    """
    Get the number of pages in the PDF.
    """
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        return len(reader.pages)

def ocr_page(pdf_path: str, page_number: int) -> str:
    """
    Convert a specific page to an image and perform Tesseract OCR.
    """
    images = convert_from_path(pdf_path, first_page=page_number+1, last_page=page_number+1)

    if not images:
        return ""

    img = images[0]
    text = pytesseract.image_to_string(img)
    return text


def save_text(text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[✓] OCR output saved to {output_path}")


if __name__ == "__main__":
    text = extract_text_from_pdf(PDF_PATH)
    save_text(text, OUTPUT_PATH)
