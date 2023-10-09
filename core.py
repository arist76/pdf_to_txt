import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageOps
import os
import io
from rich.progress import Progress
import numpy as np
import rich


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



def scan_image(
    img : str | Image.Image | fitz.Page, 
    output_file : str,
    is_two_paged : bool,
    split_at : int | None,
    header_margin : float,
    footer_margin : float,
    invert: bool,
    from_cli : bool = False,
):  
    with open(output_file, "a") as output_txt_file:
        if isinstance(img, str):
            image = [Image.open(img)]
            if is_two_paged:
                image =  list(split_image(image[0], split_at))
        elif isinstance(img, fitz.Page):
            image = page_to_image(img, is_two_paged, split_at)
        
        for img in image:
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGB')

            img = crop_header(img, header_margin)
            img = crop_footer(img, footer_margin)
            
            if invert:
                img = ImageOps.invert(img)

            # convert image to text
            text = pytesseract.image_to_string(np.array(img), lang="amh")
            output_txt_file.write(text)
            output_txt_file.write("\n\n" + "_"*50 + "\n\n")

def scan_pdf(
    pdf_file : str,
    output_file : str,
    is_two_paged : bool,
    split_at : int | None,
    begin_page : int,
    end_page : int,
    header_margin : float,
    footer_margin : float,
    invert : bool,
    from_cli : bool = False
):
    def execute(pdf_document, progress = None):
        for page in pdf_document.pages(begin_page, end_page):
            scan_image(page, output_file, is_two_paged, split_at, header_margin, footer_margin, invert)            

            # update progress bar
            try:
                progress.update(task1,advance=1)
            except AttributeError:
                pass

    pdf_document = fitz.open(pdf_file)
    if from_cli:
        with Progress() as progress:
            task1 = progress.add_task(f"[green] Processing {os.path.basename(pdf_file)}\n", total = pdf_document.page_count)
            execute(pdf_document, progress)
    else:
        execute(pdf_document)

    pdf_document.close()

