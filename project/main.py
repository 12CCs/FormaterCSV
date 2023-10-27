import json
import grobid_tei_xml
import unicodedata
import fitz

import os
import xml.etree.ElementTree as ET

from grobid_client.grobid_client import GrobidClient
from unidecode import unidecode

CONFIG_PATH = "./config.json"

INPUT_PDF_PATH = "./resources/input_pdf"
OUTPUT_XML_PATH = "./resources/xml_out/"
OUTPUT_JSON_PATH = "./resources/json_out/"
OUTPUT_PDF_PATH = "./resources/pdf_out/"

PAGES = 2

client = GrobidClient(config_path=CONFIG_PATH)
client.process("processFulltextDocument", INPUT_PDF_PATH, output=OUTPUT_XML_PATH,  generateIDs=True, consolidate_header=True, consolidate_citations=True, include_raw_citations=True, include_raw_affiliations=True, tei_coordinates=True, segment_sentences=True, force=True, verbose=False)

ACTION_ATTRIBUTES = [
    'full_name',
    'given_name',
    'surname',
    'email',
    'title'
]
ATTRIBUTE_COLOR_MAP = {
    'full_name': (0, 1, 0),
    'given_name': (1, 0, 0),
    'surname': (0, 0, 1),
    'email': (0, 1, 1),
    'title': (1, 0, 1),
    'abstract': (1, 1, 0),
}

file_list = os.listdir(OUTPUT_XML_PATH)
for xml_file_name in file_list:
    if not xml_file_name.endswith('.xml'):
        continue
    
    xml_file_path = os.path.join(OUTPUT_XML_PATH, xml_file_name)
    with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
        doc = grobid_tei_xml.parse_document_xml(xml_file.read())


    json_file_path = os.path.join(OUTPUT_JSON_PATH, xml_file_name[:-15] + '.json')
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(doc.to_dict(), json_file, indent=2, ensure_ascii=True)

    with open(json_file_path, 'r') as file:
        doc = json.load(file)

    pdf_folder_file = os.path.join(INPUT_PDF_PATH, xml_file_name[:-15] + '.pdf')
    pdf_document = fitz.open(pdf_folder_file)
  
    def iterate_doc(doc, action, action_attributes):
        for key, value in doc.items():
            if key in action_attributes:
                action(doc, key)
            elif isinstance(value, dict):
                iterate_doc(value, action, action_attributes)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        iterate_doc(item, action, action_attributes)

    def common_action(doc, key):
        search_text = unidecode(doc[key])
        
        for page in pdf_document:
            if page.number >= PAGES:
                break
            
            normalized_string = unicodedata.normalize('NFC', search_text)
            transformed_string = ''.join(c for c in normalized_string if not unicodedata.combining(c))

            for text_instance in page.search_for(transformed_string):
                if search_text[0].isupper() and not page.get_textbox(text_instance)[0].isupper():
                    continue

                page.draw_rect(text_instance, color=ATTRIBUTE_COLOR_MAP[key], width=2)

    def abstract_action(doc, key):
        abstract_text = doc[key]

        for page in pdf_document:
            if page.number >= PAGES:
                break

            for text_instance in page.search_for('Abstract'):
                page.draw_rect(text_instance, color=ATTRIBUTE_COLOR_MAP['abstract'], width=2)

            text_instance_y0, text_instance_y1 = None, None
            text_instance_x0, text_instance_x1 = None, None

            abstract_text_chunks = []
            # TODO: Iteration number should go from max to min
            iteration = 250

            for i in range(0, len(abstract_text), iteration):
                abstract_text_chunks.append(abstract_text[i:i+iteration])

            for chunk in abstract_text_chunks:
                for text_instance in page.search_for(chunk):
                    if text_instance_x0 is None or text_instance_x0 > text_instance[0]:
                        text_instance_x0 = text_instance[0]

                    if text_instance_x1 is None or text_instance_x1 < text_instance[2]:
                        text_instance_x1 = text_instance[2]

                    if text_instance_y0 is None or text_instance_y0 > text_instance[1]:
                        text_instance_y0 = text_instance[1]

                    if text_instance_y1 is None or text_instance_y1 < text_instance[3]:
                        text_instance_y1 = text_instance[3]

            if text_instance_x0 is not None and text_instance_y0 is not None and text_instance_x1 is not None and text_instance_y1 is not None:
                page.draw_rect([text_instance_x0, text_instance_y0, text_instance_x1, text_instance_y1], color=ATTRIBUTE_COLOR_MAP['abstract'], width=2)
        
    def save_pdf():
        pdf_output_path = os.path.join(OUTPUT_PDF_PATH, xml_file_name[:-15] + '.pdf')
        pdf_document.save(os.path.join(pdf_output_path))
            
    iterate_doc(doc['header'], common_action, ACTION_ATTRIBUTES)
    abstract_action(doc, 'abstract')

    save_pdf()









