import pytesseract
import io
import re
import os
import subprocess

from docx import Document
from PIL import Image
from pdf2image import convert_from_bytes

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\keixc\AppData\Environment\tesseract\tesseract.exe"
poppler_path = r"C:\Users\keixc\AppData\Environment\poppler\Library\bin"

def extract_fields(text):
    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    return {
        "name": find(r"(Name|Full Name)[\s:]+([A-Za-z\s]+)"),
        "dob": find(r"(DOB|Date of Birth)[\s:]+([\d\/\.-]+)"),
        "id_number": find(r"(ID|ID No\.?|Document No\.?)\s*[:\-]?\s*([A-Z0-9\-]+)")
    }

def extract_document_text(file):
    filename = getattr(file, "name", "").lower()
    # filename = file.filename.lower()
    file.seek(0)
    data = file.read()
    print("file name:", filename)
    print("file size:", len(data), "bytes")
    try:
        if filename.endswith(".docx"):
            print("Detected DOCX, extracting text...")
            doc = Document(io.BytesIO(data))
            full_text = "\n".join(p.text for p in doc.paragraphs)
            return full_text.strip()

        elif filename.endswith((".jpg", ".jpeg", ".png")):
            img = Image.open(io.BytesIO(data))
            text = pytesseract.image_to_string(img)
            return text.strip()

        elif filename.endswith(".pdf"):
            with open("temp.pdf", "wb") as f:
                f.write(data)
            cmd = os.path.join(poppler_path, "pdftotext.exe")
            output = subprocess.run([cmd, "temp.pdf", "-"], capture_output=True)
            pages = output.stdout.decode(errors="ignore")
            extracted = []
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                extracted.append(text)
            final_text = "\n".join(extracted)
            return final_text.strip()

        else:
            print("Unsupported file type:", filename)
            return ""
    except Exception as e:
        print("ocr failed:")
        print(e)
        return ""



