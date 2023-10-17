import pandas as pd
import json

class JSONToCSVConverter:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def load_json_data(self):
        with open(self.input_file, "r") as f:
            return json.load(f)

    def convert_to_csv(self, data):
        csv_data = []
        for page_number, page_data in data.items():
            for block in page_data["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        csv_row = {
                            "page_number": page_number,
                            "type": block["type"],
                            "text": span.get("text", ""),
                            "size": span.get("size", ""),
                            "font": span.get("font", ""),
                            "color": span.get("color", ""),
                            "ascender": span.get("ascender", ""),
                            "descender": span.get("descender", ""),
                            "origin_x": span.get("origin", [])[0],
                            "origin_y": span.get("origin", [])[1],
                            "bbox_x1": span.get("bbox", [])[0],
                            "bbox_y1": span.get("bbox", [])[1],
                            "bbox_x2": span.get("bbox", [])[2],
                            "bbox_y2": span.get("bbox", [])[3],
                            "dir_x0": line.get("dir", [])[0],
                            "dir_x1": line.get("dir", [])[1],
                            "wmode": line.get("wmode", ""),
                            "flags": span.get("flags", ""),
                            "class": span.get("class", "")
                        }
                        csv_data.append(csv_row)
        return pd.DataFrame(csv_data)

    def save_to_csv(self, df):
        df.to_csv(self.output_file, index=False)

INPUT_DATA = "results/data.json"
OUTPUT_DATA = "results/output.csv"

converter = JSONToCSVConverter(INPUT_DATA, OUTPUT_DATA)

json_data = converter.load_json_data()
csv_data = converter.convert_to_csv(json_data)

converter.save_to_csv(csv_data)
