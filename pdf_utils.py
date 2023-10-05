import typer
from rich.progress import Progress
import rich
import os
import fitz
from core import page_to_image, crop_footer, crop_header
import pytesseract
from typing import Union

app = typer.Typer()

@app.command()
def scan_pdf(
        pdf_file : str,
        output_file : str = typer.Option(None , "-o", "--output-file"),
        is_two_paged : bool = typer.Option(False, "-t", "--two-paged"),
        split_at : int = typer.Option(None, "--split-at"),
        begin_page : int = typer.Option(1, "--page-begin"),
        end_page : int = typer.Option(None, "--page-end"),
        header_margin : float = typer.Option(0, "--header-margin"),
        footer_margin : float = typer.Option(0, "--footer-margin")
):
    """Converts a pdf file with amharic language contents to text.

    Args:
        pdf_file (str): The pdf file to be converted
        output_file (str, optional): Text output file, defaults to the pdf_file name with .txt extension.
        is_two_paged (bool, optional): Specify if the an image contains two pages. Defaults to False.
        split_at (int, optional): If it has two pages where to split vertically. Defaults to spliting exactly in half.
        begin_page (int, optional): The page of the pdf to begin with. Defaults to 1.
        end_page (int, optional): The page of the pdf in which the parsing stops. Defaults to the last page of the pdf.
        header_margin (float, optional): Header margin to crop out. Defaults to 0.
        footer_margin (float, optional): Footer margin to crop out. Defaults to 0.
    """
    try:
        if output_file == None:
            output_file = os.path.basename(pdf_file)[:-4] + ".txt"

        if end_page == None:
            end_page = float("inf")

        with Progress() as progress:
            with open(output_file, "w") as output_txt_file:
                pdf_document = fitz.open(pdf_file)

                task1 = progress.add_task(f"[green] Processing {os.path.basename(pdf_file)}\n", total = pdf_document.page_count)

                # real_page_count = 0  # counts pages for two paged images

                for page in pdf_document.pages(begin_page, end_page):
                    for image in page_to_image(page, is_two_paged, split_at):
                        image = crop_header(image, header_margin)
                        image = crop_footer(image, footer_margin)

                        # convert image to text
                        text = pytesseract.image_to_string(image, lang="amh")

                        output_txt_file.write(text)             

                    # update progress bar
                    progress.update(task1,advance=1)
                
                pdf_document.close()
    except KeyboardInterrupt:
        os.remove(output_file)
        rich.print("[red] Aborted!!!")

if __name__ == "__main__":
    app()