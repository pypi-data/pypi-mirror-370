import json

import defusedxml.ElementTree as ET

class BaseClass:
    def convert(self, content):
        raise NotImplementedError("Subclasses should implement this!")


    def load_json(self, input_file: str):
        try:
            with open(input_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            self.ptjsonlib.end_error(f"{input_file} not found", True)
        except json.JSONDecodeError:
            self.ptjsonlib.end_error(f"Error deserializing {input_file} file", True)


    def load_xml(self, input_file: str):
        try:
            # Parse the XML file
            tree = ET.parse(input_file)
            return tree

        except FileNotFoundError:
            self.ptjsonlib.end_error(f"{input_file} not found", True)
        except json.JSONDecodeError:
            self.ptjsonlib.end_error(f"Error deserializing {input_file} file", True)
