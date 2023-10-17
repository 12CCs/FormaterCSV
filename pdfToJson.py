import fitz
import json

class PDFProcessor:
    PARSE_COLUMNS = ["bbox", "origin", "dir"]
    EXCEPTION_COLUMNS = ["image"]

    def __init__(self, input_data, output_data, pages=2):
        self.input_data = input_data
        self.output_data = output_data
        self.pages = pages

    def process_pdf(self):
        doc = fitz.open(self.input_data)
        pdf_text = {}

        for i, page in enumerate(doc, start=0):
            if i < self.pages:
                pdf_text[i] = self.__process_page(page)
            
        doc.close()
        return pdf_text

    def save_output(self, data):
        with open(self.output_data, "w") as f:
            json.dump(data, f, indent=2)
    
    def __convert_to_list(self, data):
        return [float(x) for x in data]

    def __validate_structure(self, data):
        if isinstance(data, dict):
            for key, value in list(data.items()):
                if key in self.PARSE_COLUMNS:
                    data[key] = self.__convert_to_list(value)
                elif key in self.EXCEPTION_COLUMNS:
                    del data[key] 
                else:
                    self.__validate_structure(value)

        elif isinstance(data, list):
            for _, item in enumerate(data):
                self.__validate_structure(item)

    def __process_page(self, page):
        text_dict = page.get_text("dict")
        self.__validate_structure(text_dict)

        return text_dict

INPUT_DATA = "data/1.pdf"
OUTPUT_DATA = "results/data.json"
PAGES = 2

pdf_processor = PDFProcessor(INPUT_DATA, OUTPUT_DATA, PAGES)

pdf_text = pdf_processor.process_pdf()
pdf_processor.save_output(pdf_text)
