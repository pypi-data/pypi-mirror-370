"""
Elasticsearch user enumeration

This module enumerates what users are available on an Elasticsearch instance

Contains:
- Users class to perform the user enumeration
- run() function as an entry point for running the test
"""

import http
from json import JSONDecoder

from requests import Response
from http import HTTPStatus
from xml.etree.ElementPath import prepare_parent

from ptlibs import ptjsonlib
from ptlibs.ptprinthelper import ptprint

__TESTLABEL__ = "Elasticsearch user enumeration"


class Users:
    """
    This class enumerates what users are available, their roles and privileges
    """
    def __init__(self, args: object, ptjsonlib: object, helpers: object, http_client: object, base_response: object) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client
        self.base_response = base_response

        self.helpers.print_header(__TESTLABEL__)


    def _check_privileges(self, role: str, role_privileges: dict, user_properties: dict):
        """
        This method enumerates all privileges assigned to a specific role by going through the JSON output provided by the /_security/roles endpoint.

        Adds the privileges to the JSON output
        """
        indices = role_privileges[role]['indices']
        applications = role_privileges[role]['applications']

        for index in indices:
            privileges = index["privileges"]
            if index["names"][0] == '*':
                index_name = "ALL"
            else:
                index_name = ', '.join(index['names'])

            user_properties["roles"][role].append({index_name: privileges})

            ptprint(f"Privileges on indices: {index_name}: {', '.join(privileges).upper()}; Can edit restricted indices: "
                    f"{index["allow_restricted_indices"]}",
                    "VULN", not self.args.json, indent=12)

        for app in applications:
            privileges = "ALL" if app["privileges"][0] == '*' else app["privileges"]
            privileges_name = "ALL" if app["privileges"][0] == '*' else ', '.join(app["privileges"]).upper()
            app_name = "app_ALL" if app["application"] == "*" else "app_" + app["application"]

            user_properties["roles"][role].append({app_name: privileges})

            ptprint(f"Privileges on application: {app_name}: {privileges_name}",
                    "VULN", not self.args.json, indent=12)

    def _print_user(self, user_properties: dict, check_roles: bool, role_privileges: dict) -> None:
        """
        This method prints the user information to the terminal. If the user has a role of 'superuser', we print it in red

        If we're able to list roles from the /_security/role endpoint, we enumerate privileges assigned to the roles of a user
        with the _check_privileges method
        """
        ptprint(f"Found user: {user_properties['username']}", "VULN", not self.args.json, indent=4)
        ptprint(f"Email: {user_properties['email']}", "VULN", not self.args.json, indent=8)

        roles = set(user_properties["roles"])

        for role in roles:
            if role == "superuser":
                ptprint(f"\033[0mRole: \033[31m{role}", "VULN", not self.args.json, indent=8, colortext=True)
            else:
                ptprint(f"Role: {role}", "VULN", not self.args.json, indent=8)
            if check_roles:
                self._check_privileges(role, role_privileges, user_properties)
            else:
                ptprint(f"Could not enumerate privileges","OK", not self.args.json, indent=4)



    def run(self) -> None:
        """
        Executes the Elasticsearch user enumeration

        Sends an HTTP GET request to the /_security/user endpoint and iterates through the JSON response.
        User by user adds the username, roles and email to the JSON output

        If the host returns an HTTP response other than 200 OK we exit
        """
        check_roles = False
        response = self.http_client.send_request(self.args.url+"_security/user", method="GET",
                                                 headers=self.args.headers, allow_redirects=False)

        if response.status_code != HTTPStatus.OK:
            ptprint(f"Could not enumerate users. Received status code: {response.status_code}",
                    "OK", not self.args.json, indent=4)
            return

        users = response.json()
        response = self.http_client.send_request(self.args.url + "_security/role", method="GET",
                                                 headers=self.args.headers, allow_redirects=False)
        if response.status_code == HTTPStatus.OK:
            check_roles = True

        for entry in users:
            user = users[entry]
            roles = dict([(role_name, privileges) for role_name, privileges in zip(user['roles'], [[]])])
            user_properties = {"username": user["username"], "email": user["email"], "roles": roles}
            json_node = self.ptjsonlib.create_node_object("user", properties=user_properties)
            self.ptjsonlib.add_node(json_node)
            self._print_user(user_properties, check_roles, response.json())


def run(args, ptjsonlib, helpers, http_client, base_response):
    """Entry point for running the IsElastic test"""
    Users(args, ptjsonlib, helpers, http_client, base_response).run()
