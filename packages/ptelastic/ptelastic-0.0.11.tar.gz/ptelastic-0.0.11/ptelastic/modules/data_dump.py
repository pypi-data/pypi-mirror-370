"""
Elasticsearch data dump module

Contains:
- DataDump to perform the data dump
- run() function as an entry point for running the test
"""

import http
from http.client import responses
from http.cookiejar import cut_port_re
from mimetypes import inited
import json
from typing import Literal

from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch data dump module"


class DataDump:
    """
    This class dumps all data from indices in an Elasticsearch instance
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _get_data(self, data: dict, field: str):
        """
        This method retrieves the value assigned to the provided field in the index data
        """
        if "." in field:
            field = field.split(".")
            value = data
            for key in field:
                value = value[key]
        else:
            value = data[field]

        return value


    def _get_field(self, entry: dict) -> dict:
        """
        This method goes through all the fields provided with the -df/--dump-fields argument and retrieves its key:value pair from the data
        entry and then adds it to a dictionary that is returned by this method.

        :return: Dictionary with the desired fields and its values. Empty dictionary if the field/s is not found in the data entry
        """
        results = {"_id": entry["_id"], "_index": entry["_index"]}
        data = entry["_source"]

        for field in self.args.dump_field:
            try:
                results.update({field: self._get_data(data, field)})
            except KeyError as e:
                ptprint(f"The entry {entry} does not contain field {e}", "ERROR", self.args.verbose, indent=4)

        return results if len(results.keys()) > 2 else {}


    def _write_to_file(self, data) -> None:
        with open(self.args.out_file, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    def run(self) -> None:
        """
        Executes the Elasticsearch data dump

        This method sends an HTTP GET request to all the indices provided with the -di/--dump-index argument (all indices if none are provided)
        and dumps all data from it. If --df/--dump-fields are set, it extracts the desired fields from the data with the _get_field() method
        """

        for index in self.args.dump_index:
            response = self.http_client.send_request(method="GET",url=self.args.url + f"{index}/_search?size=10000")

            if response.status_code != HTTPStatus.OK:
                ptprint(f"Error when reading indices: Received response: {response.status_code} {response.text}",
                        "ERROR", not self.args.json, indent=4)
                continue

            data = response.json()["hits"]["hits"]  # limit 10 000 hits
            full_data = []

            if self.args.dump_field:

                for entry in data:
                    isolated_data = self._get_field(entry)
                    ptprint(isolated_data, "INFO", not self.args.json, indent=4) if isolated_data else None
                    full_data.append(isolated_data) if isolated_data else None

            else:
                ptprint(data, "INFO", not self.args.json, indent=4)
                full_data = data

            if self.args.out_file and full_data:
                self._write_to_file(full_data)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the DataDump test"""
    DataDump(args, ptjsonlib, helpers, http_client, base_response).run()
