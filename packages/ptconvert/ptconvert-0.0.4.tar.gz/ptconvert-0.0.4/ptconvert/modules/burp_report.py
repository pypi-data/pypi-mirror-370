from ._baseclass import BaseClass

import csv, re, json

from ptlibs import ptmisclib
from ptlibs.ptpathtypedetector import PtPathTypeDetector

class BurpReportParser(BaseClass):
    def __init__(self, ptjsonlib: object):
        self.ptjsonlib: object = ptjsonlib

    def convert(self, args) -> list:
        if not args.csv:
            self.ptjsonlib.end_error("--csv parameter is required for BurpReportParser module", True)

        try:
            tree = self.load_xml(args.input)
            root_element = tree.getroot()
        except Exception as e:
            raise

        result_node_list: list = []
        with open(args.csv, "r") as file:
            csv_reader = csv.reader(file)

            for issue in root_element.findall('issue'):
                issue_type = self.get_text_safely(issue.find("type"))
                issue_host = self.get_text_safely(issue.find("host"))
                issue_location = self.get_text_safely(issue.find("location"))

                if args.use_texts:
                    issue_name = self.get_text_safely(issue.find("name"))
                    issue_path = self.get_text_safely(issue.find("path"))
                    issue_host_ip = issue.find("host").get("ip") if issue_host else ""
                    issue_severity = self.get_text_safely(issue.find("severity"))
                    issue_background = self.get_text_safely(issue.find("issueBackground"))
                    issue_remediation = self.get_text_safely(issue.find("remediationBackground"))
                    issue_detail = self.get_text_safely(issue.find("issueDetail"))

                    if issue.find("issueDetailItems") is not None: # Get parent
                        issue_detail_items = [self.get_text_safely(item) for item in issue.find("issueDetailItems").findall('issueDetailItem')] if issue.find("issueDetailItems") is not None else []
                    else:
                        issue_detail_items = []

                    request_response = issue.find("requestresponse")
                    if request_response is not None:
                        issue_request = self.get_text_safely(request_response.find("request"))
                        issue_response = self.get_text_safely(request_response.find("response"))
                        issue_request_method = request_response.find("request").get("method")
                    else:
                        issue_request = issue_response = issue_request_method = None

                    issue_references = self.get_text_safely(issue.find("references"))

                    issue_vulnerability_classifications = self.get_text_safely(issue.find("vulnerabilityClassifications"))
                    issue_cwe = self.get_cwe_from_vulnerability_classifications(issue_vulnerability_classifications)

                # Find correct row in CSV file
                found_record = False
                for row in csv_reader:
                    hex_issue_type = hex(int(issue_type))[2:]
                    if row[0].lstrip("0") == hex_issue_type:
                        penterep_vuln_code, penterep_root_node, penterep_target_node = row[3], row[4], row[5]
                        found_record = True
                        file.seek(0) # set reading position back to start
                        break
                if not found_record:
                    file.seek(0)
                    penterep_root_node = penterep_target_node = penterep_vuln_code = None

                vulnerability: dict = {"vulnCode": penterep_vuln_code}
                if args.use_texts:
                    vulnerability.update(
                        {
                            "name": issue_name,
                            "vulnLocation": issue_location,
                            "vulnSeverity": issue_severity,
                            "vulnDescription": ptmisclib.clean_html(issue_background),
                            "vulnRecommendation": ptmisclib.clean_html(issue_remediation),
                            "vulnDisplays": ptmisclib.clean_html(issue_detail),
                            "vulnCwe": issue_cwe
                        })

                if args.parse_url:
                    node_list: list = self.ptjsonlib.parse_url2nodes(issue_host + issue_location)
                    if node_list:
                        node_list[0]["parentType"] = penterep_root_node
                        node_list[-1]["vulnerabilities"].append(vulnerability)
                        for n in node_list:
                            result_node_list.append(n)
                else:
                    node = self.ptjsonlib.create_node_object(
                        node_type = "webSource",
                        parent_type = penterep_root_node,
                        properties = {
                            "url": issue_host + issue_location,
                            "name": issue_location,
                            "webSourceType": PtPathTypeDetector().get_type(issue_location)
                        },
                        vulnerabilities=[vulnerability]
                    )
                    result_node_list.append(node)

        return result_node_list

    def get_text_safely(self, element):
        return element.text if element is not None and element.text is not None else ""

    def get_cwe_from_vulnerability_classifications(self, vulnerability_classification: str) -> str:
        """Retrieve CWE from provided <vulnerability_classification> element"""
        # Returns only the first occurence of CWE list
        return re.findall(r"CWE-(\d*)", vulnerability_classification)[0]