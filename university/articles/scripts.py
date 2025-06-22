from PyPDF2 import PdfReader
import io
from PyPDF2.errors import EmptyFileError

"""extract text form pdf file"""
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except EmptyFileError:
        print("The file is empty.")
        return ""
