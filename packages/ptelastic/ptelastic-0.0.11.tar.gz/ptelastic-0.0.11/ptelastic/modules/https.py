"""
Elasticsearch HTTP/S test

This module tests if an Elasticsearch instance is running on HTTPS or HTTP
"""

import http
from http import HTTPStatus
from http.client import responses

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch HTTP/S test"


class HttpTest:
    """
    This class tests to see if the host has Elasticsearch running on HTTP or HTTPS
    """

    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _check_http(self, url) -> None:
        """
        This method checks to see if the provided URL is really running on HTTP by sending a GET request and looking
        at the response

        If the server responds with an HTTP 200 OK, we print a message and add a vulnerability to the JSON output

        If not, we print a message that the server is running HTTPS

        :param url: Host to test
        :return:
        """
        if url == self.args.url:
            response = self.base_response
        else:
            response = self.http_client.send_request(url, method="GET", headers=self.args.headers, allow_redirects=False)

        if response.status_code in [HTTPStatus.OK, HTTPStatus.UNAUTHORIZED]:
            ptprint(f"The host is running HTTP", "VULN", not self.args.json, indent=4)
            self.ptjsonlib.add_vulnerability("PTV-ELASTIC-MISC-HTTP")
        else:
            ptprint(f"The host is not running on HTTP", "OK", not self.args.json, indent=4)


    def _check_url(self) -> str:
        """
        This method edits the provided URL.

        Adds '\\http://' to the begging of the URL if no protocol is provided

        www.example.com:9200 -> \\http://www.example.com:9200

        Doesn't do anything if a protocol is provided

        :return: Edited URL
        """

        url = self.args.url

        if "http://" not in url and "https://" not in url:
            return "http://" + url

        return url


    def run(self) -> None:
        """
        Executes the Elasticsearch HTTP/S test

        Edits the URL if necessary and checks if the host is really running HTTP or not

        If we're provided with an HTTPS URL, we just print a message that says the host is running HTTPS
        """

        url = self._check_url()

        if "http://" in url:
            self._check_http(url)
            return

        ptprint(f"The host is not running on HTTP", "OK", not self.args.json, indent=4)


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the HTTP/S test"""
    HttpTest(args, ptjsonlib, helpers, http_client, base_response).run()
