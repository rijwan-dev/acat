import pytesseract
import io
import re

from PIL import Image
from pdf2image import convert_from_bytes

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\keixc\AppData\Environment\tesseract\tesseract.exe"

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
        if filename.endswith(".pdf"):
            pages = convert_from_bytes(data)
            extracted = []
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                extracted.append(text)
            final_text = "\n".join(extracted)
            return final_text.strip()
        img = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(img)
        print("ocr output:")
        print(text)
        return text.strip()
    except Exception as e:
        print("ocr failed:")
        print(e)
        return ""

