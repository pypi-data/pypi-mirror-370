"""
Elasticsearch availability test

This module implements a test that checks if the provided host is running Elasticsearch or not

Contains:
- IsElastic to perform the availability test
- run() function as an entry point for running the test
"""

import http
from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch availability test"


class IsElastic:
    """
    This class checks to see if a host is running Elasticsearch by looking for JSON content in the hosts response
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _check_text(self, response: Response) -> bool:
        return "elasticsearch" in response.text.lower()


    def run(self) -> None:
        """
        Executes the Elasticsearch availability test

        Sends an HTTP GET request to the provided URL and checks to see if we get JSON content as a response.

        JSON content not in response - calls ptjsonlib.end_error() to stop execution of all further modules.

        JSON content in response - Check if content contains a security exception in the case of a 401 Unauthorized response or
        "X-elastic-product: Elasticsearch" header in the case of a 200 OK response
        """

        response = self.base_response

        try:
            if "application/json" not in response.headers["content-type"]:
                #ptprint(f"The host is not running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
                #return
                self.ptjsonlib.end_error("The host is not running Elasticsearch", self.args.json)
        except KeyError:
            #ptprint(f"The host is not running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
            #return
            self.ptjsonlib.end_error("The host is not running Elasticsearch", self.args.json)

        if response.status_code == HTTPStatus.UNAUTHORIZED:
            response_json = response.json()

            try:
                if self._check_text(response):
                    ptprint(f"The host is running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
                elif response_json["error"]["root_cause"][0]["type"] == "security_exception":
                    ptprint(f"The host might be running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
            except KeyError:
                ptprint(f"The host is probably not running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)

        elif response.status_code == HTTPStatus.OK:
            try:
                if response.headers["X-elastic-product"] == "Elasticsearch":
                    ptprint(f"The host is running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
            except KeyError:
                if self._check_text(response):
                    ptprint(f"The host is running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
                elif "application/json" in response.headers["Content-Type"]:
                    ptprint(f"The host might be running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)
        else:
            self.ptjsonlib.end_error("The host is not running Elasticsearch", self.args.json)
            #ptprint(f"The host is not running ElasticSearch", "INFO", not self.args.json, colortext=False, indent=4)



def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the IsElastic test"""
    IsElastic(args, ptjsonlib, helpers, http_client, base_response).run()
