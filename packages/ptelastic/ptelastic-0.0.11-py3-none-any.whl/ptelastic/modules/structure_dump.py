"""
Elasticsearch data structure test

Contains:
- StrucDump to perform the data structure test
- run() function as an entry point for running the test
"""

import http
from http.client import responses
from mimetypes import inited

from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch data structure test"


class StrucDump:
    """
    This class gets all indexes from an ES instance and then dumps what fields each index contains
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _get_indices(self) -> list:
        """
        This method retrieves all available indexes at an ES instance

        :return: List of indexes if successful. Empty list otherwise
        """
        response = self.http_client.send_request(method="GET", url=self.args.url+"_cat/indices?pretty", headers=self.args.headers)

        if response.status_code != HTTPStatus.OK:
            ptprint(f"Error fetching indices. Received response: {response.status_code} {response.text}", "ERROR",
                    not self.args.json, indent=4)
            return []

        try:
            indices = [line.split()[2] for line in response.text.strip().split("\n") if line.strip()]
        except Exception as e:
            ptprint(f"Error when reading indices: {e}", "ERROR", not self.args.json, indent=4)
            return []

        return indices


    def _get_fields(self, mapping, prefix="") -> list:
        """
        This method recursively collects all field paths from ES mapping.

        :return: List of fields in an index mapping
        """
        fields = []
        props = mapping["properties"]

        for field_name, field_info in props.items():
            full_name = f"{prefix}{field_name}" if not prefix else f"{prefix}.{field_name}"
            fields.append(full_name)

            if "properties" in field_info:
                fields.extend(self._get_fields(field_info, prefix=full_name))

        return fields


    def run(self) -> None:
        """
        Executes the Elasticsearch data structure test

        This method gets all indices with the _get_indices() method and then prints fields in an index by sending a request to
        the /<index name> endpoint and then retrieving all the fields with the method _get_fields()

        If the -vv/--verbose switch is provided, the method prints hidden indices (indices starting with .) along all other indices.
        """
        for index in self._get_indices():
            if not self.args.verbose and index.startswith("."):
                continue

            response = self.http_client.send_request(method="GET", url=self.args.url + index)

            if response.status_code != HTTPStatus.OK:
                ptprint(f"Error fetching index {index}. Received response: {response.status_code} {response.text}",
                        "ERROR",
                        not self.args.json, indent=4)
                continue

            response = response.json()

            try:
                fields = self._get_fields(mapping=response[index]["mappings"])
            except KeyError as e:
                ptprint(f"Index {index} has no mappings with {e} field", "ERROR", not self.args.json, indent=4)
                continue

            ptprint(f"Index {index}", "INFO", not self.args.json, indent=4)
            ptprint(', '.join(fields), "INFO", not self.args.json, indent=8)

def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the StrucDump test"""
    StrucDump(args, ptjsonlib, helpers, http_client, base_response).run()
