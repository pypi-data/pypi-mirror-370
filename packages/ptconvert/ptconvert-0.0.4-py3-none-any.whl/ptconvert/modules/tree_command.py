from ._baseclass import BaseClass

import csv, re, json
from ptlibs import ptmisclib

class TreeCommandParser(BaseClass):
    def __init__(self, ptjsonlib: object):
        self.ptjsonlib: object = ptjsonlib

    def convert(self, args) -> list:
        """
        Main entry point: read tree command output (JSON or text) and convert to nodes.
        """
        try:
            file_type, data = self.load_tree_file(args.input)
            if file_type == "json":
                result_nodes = self.parse_tree_json(data)
            elif file_type == "text":
                result_nodes = self.parse_tree_text(data)
            return result_nodes
        except Exception as e:
            print(e)

    def load_tree_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()  # read the entire file
                try:
                    # try to parse JSON
                    data = json.loads(content)
                    return "json", data
                except json.JSONDecodeError:
                    # not JSON → return as plain text
                    return "text", content
        except Exception as e:
            print(f"Error reading file: {e}")
            return None, None

    def parse_tree_json(self, data: list) -> list:
        """
        Parse JSON output from `tree -J` into node objects.
        """
        root = self.ptjsonlib.create_node_object("treeRoot", properties={"name": "root"})
        nodes = [root]

        def walk_tree(json_nodes, parent_key):
            for node in json_nodes:
                # create node object for current node
                node_obj = self.ptjsonlib.create_node_object(
                    "treeNode",
                    parent=parent_key,
                    properties={"name": node.get("name", "")}  # safer
                )
                nodes.append(node_obj)

                # recursively handle children
                if isinstance(node.get("contents"), list) and node["contents"]:
                    walk_tree(node["contents"], node_obj["key"])

        # top-level may be a list of nodes
        if isinstance(data, list):
            walk_tree(data, root["key"])
        else:
            # fallback: treat as single node
            walk_tree([data], root["key"])
        return nodes

    def parse_tree_text(self, text: str) -> list:
        """
        Parse plain text output from `tree` (Unicode or ASCII) into node objects.
        """
        root = self.ptjsonlib.create_node_object("treeRoot", properties={"name": "root"})
        nodes = [root]

        stack = [(0, root)]  # (level, node)

        for line in text.splitlines():
            stripped = line.rstrip()
            if not stripped or stripped.strip() == '.':
                continue

            # Remove known visual prefixes
            line_clean = re.sub(r'^[\s│|`]+[-–─]*\s*', '', stripped)
            # Calculate approximate level by counting leading spaces / visual columns
            indent_len = len(stripped) - len(stripped.lstrip(' '))
            level = indent_len // 4  # assume 4 spaces per level as a default

            # Find the correct parent node in the stack
            while stack and stack[-1][0] >= level + 1:
                stack.pop()
            parent_node = stack[-1][1]

            # Create node
            node_obj = self.ptjsonlib.create_node_object(
                "treeNode",
                parent=parent_node["key"],
                properties={"name": line_clean.strip()}
            )
            nodes.append(node_obj)
            stack.append((level + 1, node_obj))

        return nodes


    def open_file(self, input_file: str, mode: str = "r"):
        """
        Open a file and return the file handler.

        Args:
            input_file (str): Path to the file.
            mode (str): File opening mode (default is 'r' for read).

        Returns:
            file object: The opened file handler.

        Raises:
            SystemExit: If the file is not found (via ptjsonlib.end_error).
        """
        try:
            return open(input_file, mode, encoding="utf-8")
        except FileNotFoundError:
            self.ptjsonlib.end_error(f"{input_file} not found", True)

    def is_json(self, file_handler):
        """
        Check if an opened file handler contains valid JSON and return its content.
        """
        try:
            json.load(file_handler)
            return True
        except json.JSONDecodeError:
            return False
