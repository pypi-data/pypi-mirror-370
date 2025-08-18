#!/usr/bin/python3
"""
    Copyright (c) 2024 Penterep Security s.r.o.

    ptconvert is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ptconvert is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of

    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ptconvert.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import json
import os
import sys; sys.path.extend([__file__.rsplit("/", 1)[0], os.path.join(__file__.rsplit("/", 1)[0], "modules")])
import importlib

from _version import __version__
from ptlibs import ptjsonlib, ptprinthelper

class PtConvert:
    def __init__(self):
        self.ptjsonlib = ptjsonlib.PtJsonLib()

    def run(self, args):
        parser_class = getattr(self.load_and_get_module(args.format.replace('-', "_")), f"{format_string(args.format.capitalize())}Parser")
        try:
            nodes_list = parser_class(self.ptjsonlib).convert(args)
        except Exception as e:
            print(e)
            self.ptjsonlib.end_error(f"Error occured inside {parser_class}", True)
        self.ptjsonlib.add_nodes(nodes_list)
        self.ptjsonlib.set_status("finished")
        print(self.ptjsonlib.get_result_json())
        self.save_json(args.output, nodes_list)

    def save_json(self, input_file: str, result: list):
        with open(input_file, "w") as file:
            file.write(json.dumps(result, indent=4))

    def load_and_get_module(self, module_name):
        try:
            return importlib.import_module(f"modules.{module_name}")
        except ImportError as e:
            self.ptjsonlib.end_error(f"Error importing {module_name}: {e}", True)

def format_string(s):
    """Return a string with hyphens removed and the following character capitalized."""
    return ''.join(s[i].upper() if i > 0 and s[i - 1] == '-' else s[i] for i in range(len(s)) if s[i] != '-')


def get_modules_help(extension=".py"):
    """Make dynamic help through available modules"""
    folder_path: str = os.path.join(os.path.dirname(__file__), "modules")
    available_modules = [f for f in os.listdir(folder_path) if (os.path.join(folder_path, f) and (f.endswith(extension) and f[0] != "_"))]
    sorted_modules = sorted((["", "", f"{file_name.split('.')[0].replace('_', '-')}", f"{format_string(file_name.split('.')[0].replace('_', '-').capitalize())} " + "format"] for file_name in available_modules), key=lambda x: x[2])
    return sorted_modules


def get_help():
    return [
        #{"description": ["ptconvert"]},
        {"usage": ["ptconvert <options>"]},
        {"usage_example": [
            "ptconvert -f swagger -i swagger_file.json -o penterep.json"
        ]},
        {"options": [
            ["-i",  "--input",       "<file>",                       "Set input file"],
            ["-o",  "--output",      "<output>",                     "Set output file"],
            ["-f",  "--format",      "<format>",                     "Set input file format to:"],
            *get_modules_help(),
            ["", "", "", ""],

            ["",  "--csv",           "<path-to-csv>",                "Set path to CSV file"],
            ["",  "--use-texts", "",                                 "Use texts from Burp Report"],
            ["",  "--parse-url", "",                                 "Parse URLs in Burp Report"],
            ["", "", "", ""],

            ["-v",  "--version",     "",                             "Show script version and exit"],
            ["-h",  "--help",        "",                             "Show this help message and exit"],
        ]
        }]


def parse_args():
    parser = argparse.ArgumentParser(add_help=False, usage=f"{SCRIPTNAME} <options>")
    parser.add_argument("-i",  "--input",      type=str, required=True)
    parser.add_argument("-o",  "--output",     type=str, required=True)
    parser.add_argument("-f",  "--format",     type=lambda s: s.lower(), required=True, choices=([module[2].lstrip() for module in get_modules_help()]))

    parser.add_argument("--csv",               type=str)
    parser.add_argument("--parse-url",         action="store_true")
    parser.add_argument("--use-texts",         action="store_true")
    parser.add_argument("-v",  "--version",    action="version", version=f"%(prog)s {__version__}")

    parser.add_argument("--socket-address",    type=str, default=None)
    parser.add_argument("--socket-port",       type=str, default=None)
    parser.add_argument("--process-ident",     type=str, default=None)


    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptprinthelper.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()
    ptprinthelper.print_banner(SCRIPTNAME, __version__, False)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptconvert"
    args = parse_args()
    script = PtConvert()
    script.run(args)


if __name__ == "__main__":
    main()
