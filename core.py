import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os
import io


def pdf_to_txt(pdf_file, output_text_file):
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


def page_to_image(page, is_two_paged : bool = False, split_x : int | None = None) -> list[Image.Image]:

    pixmap = page.get_pixmap().tobytes()
    image = Image.open(io.BytesIO(pixmap))

    if is_two_paged:
        return list(split_image(image, split_x))
    
    return [image]

def split_image(image : Image.Image, split_x : int | None = None):
    width, height = image.size

    split_x = split_x if split_x != None else width/2

    left = image.crop((0, 0, split_x, height))
    right = image.crop((split_x, 0, width, height))

    return (left, right)

def crop_header(image : Image.Image, margin : int = 0):
    width, height = image.size

    return image.crop((0, margin, width, height))

def crop_footer(image: Image.Image, margin : int = 0):
    width, height = image.size

    return image.crop((0, 0, width, height - margin))