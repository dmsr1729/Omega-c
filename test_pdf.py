from modules.pdf_processor import extract_text

pdf_path = "data/mohan_sameer.pdf"

text = extract_text(pdf_path)

print("Extracted PDF Content:")
print(text)