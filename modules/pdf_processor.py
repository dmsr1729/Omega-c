from pypdf import PdfReader


def extract_pages(pdf_path):

    reader = PdfReader(pdf_path)

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text and text.strip():

            extracted_pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return extracted_pages


def extract_text(pdf_path):

    pages = extract_pages(pdf_path)

    extracted_text = ""

    for page in pages:
        extracted_text += page["text"] + "\n"

    return extracted_text