from ._baseclass import BaseClass

class UrlWordlistParser(BaseClass):
    # TODO: parser outputu externich nastroju (e.g. dirb)
    def __init__(self, ptjsonlib: object):
        self.ptjsonlib: object = ptjsonlib

    def convert(self, args) -> list:
        file_lines = self.read_file(args.input)

        node = self.ptjsonlib.create_node_object("wordlist")
        for line in file_lines:
            line = line.strip()
            node["vulnerabilities"].append(line.strip())

        nodes_list = [root]

    def read_file(self, file_location):
        with open(file_location, "r", errors="ignore") as file:
            return file.readlines()