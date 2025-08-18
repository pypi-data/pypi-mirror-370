from ._baseclass import BaseClass
import yaml
import json

class SwaggerParser(BaseClass):
    def __init__(self, ptjsonlib: object):
        self.ptjsonlib: object = ptjsonlib

    def load_yaml_or_json(self, input_file: str) -> dict:
        """Load the input file as either YAML or JSON, return parsed as a dictionary."""
        try:
            with open(input_file, "r", encoding="utf-8") as file:
                content = file.read()
                try:
                    # Attempt to parse as YAML and return as dictionary (JSON equivalent)
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    try:
                        # Fallback to JSON parsing
                        return json.loads(content)
                    except json.JSONDecodeError:
                        self.ptjsonlib.end_error(f"{input_file} is neither valid YAML nor JSON", True)
        except FileNotFoundError:
            self.ptjsonlib.end_error(f"{input_file} not found", True)

    def convert(self, args) -> list:
        content = self.load_yaml_or_json(args.input)
        root: dict = self.ptjsonlib.create_node_object("webApi", properties={"name": content.get("info").get("title"), "webApiType": "webApiTypeRest", "description": content.get("info").get("description")})
        nodes_list = [root]
        for path, methods in content["paths"].items():
            endpoint_node: dict = self.ptjsonlib.create_node_object("webApiEndpoint", parent=root["key"], properties={"name": path, "url": path})
            nodes_list.append(endpoint_node)

            for method, details in methods.items():
                method_node = self.ptjsonlib.create_node_object("webApiMethod", parent=endpoint_node["key"], properties={
                    "name": method.upper(),
                    "webHttpMethod": f"webHttpMethod{method.capitalize()}",
                    "description": details.get("summary")
                })
                nodes_list.append(method_node)

                for parameter in details.get("parameters", []):
                    parameter_type: dict = parameter.get('type')

                    if parameter_type is None:
                        continue

                    parameter_node = self.ptjsonlib.create_node_object("webInput", parent=method_node["key"], properties={
                    "name": parameter["name"],
                    "description": parameter.get("description"),
                    "webInputType": f"webInputType{parameter_type.capitalize()}" if parameter_type is not None else None
                })
                    nodes_list.append(parameter_node)

        return nodes_list