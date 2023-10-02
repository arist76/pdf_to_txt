import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os


def pdf_to_txt(pdf_file, output_text_file):
    """
    Converts a PDF file with scanned content to a text file.

    Args:
        pdf_file (str): Path to the input PDF file.
        output_text_file (str): Path to the output text file.
    """

    # Initialize the text file for writing
    with open(output_text_file, "w", encoding="utf-8") as text_file:
        pdf_document = fitz.open(pdf_file)

        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            image = page.get_pixmap()
            image_path = f"page_{page_number + 1}.png"
            image.save(image_path)

            # Use pytesseract to extract text from the image
            text = pytesseract.image_to_string(Image.open(image_path), lang="amh")
            text_file.write(text)
            text_file.write("\n")

            # Remove the temporary image file
            os.remove(image_path)

        pdf_document.close()


if __name__ == "__main__":
    pdf_file = "ፍቅር-እስከ-መቃብር-.pdf"
    output_text_file = "ፍቅር-እስከ-መቃብር-.txt"

    pdf_to_txt(pdf_file, output_text_file)
