import fitz

class PDFProcessor:
    def __init__(self, input_data, output_data, pages=2):
        self.input_data = input_data
        self.output_data = output_data
        self.pages = pages

    def pdf_to_text(self):
        text = ""
        with fitz.open(self.input_data) as pdf_document:
            num_pages_to_read = min(self.pages, pdf_document.page_count)
            for page_number in range(num_pages_to_read):
                page = pdf_document.load_page(page_number)
                text += page.get_text()
        return text

    def save_text_to_file(self, text):
        with open(self.output_data, "w", encoding="utf-8") as output_file:
            output_file.write(text)

INPUT_DATA = "data/1.pdf"
OUTPUT_DATA = "results/raw.txt"
PAGES = 2

pdf_processor = PDFProcessor(INPUT_DATA, OUTPUT_DATA, PAGES)

raw_text = pdf_processor.pdf_to_text()
pdf_processor.save_text_to_file(raw_text)
