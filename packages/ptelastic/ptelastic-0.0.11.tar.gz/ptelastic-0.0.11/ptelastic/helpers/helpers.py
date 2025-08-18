"""
Helpers module for shared functionality used across test modules.
"""

import json
import os

from ptlibs.http.http_client import HttpClient
from ptlibs.ptprinthelper import ptprint

class Helpers:
    def __init__(self, args: object, ptjsonlib: object, http_client: object):
        """Helpers provides utility methods"""
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.http_client = http_client


    def print_header(self, test_label):
        ptprint(f"Testing: {test_label}", "TITLE", not self.args.json, colortext=True)

    def check_node(self, node_type: str) -> str:
        """
        This method goes through all available nodes and checks if the node of type exists.

        :param str node_type: Type of node to look for
        :return: Key of @node_type node. Empty string otherwise
        """
        for node in self.ptjsonlib.json_object["results"]["nodes"]:
            if node["type"] == node_type:
                return node["key"]

        return ""