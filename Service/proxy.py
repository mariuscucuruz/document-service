import base64
from environment import LoadEnv
import json
from Service.logg import Log
import requests


class InvoiceProxy:
    def __init__(self):
        self.env = LoadEnv()
        self.logging = Log(self.__class__.__name__)

        self.setApiKey()
        self.setTokens()

        if not self.isReady():
            self.logging.info("Proxy Client is not ready...")

        self.logging.info(f"Proxy Client instantiated with key: {self.api_key}.")

    def requestInvoice(self, emp_session_id: str, email: str):
        response = None

        if not self.api_key:
            self.setApiKey()

        if not self.access_token:
            self.setTokens()

        request_url = self.invoice_endpoint
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-auth": self.api_key,
            "Authorization": f"Bearer {self.access_token}",
        }
        request_body = json.dumps({"emp_session_id": emp_session_id, "email": email})

        try:
            response = requests.post(
                url=request_url,
                headers=request_headers,
                data=request_body
            )
            self.logging.info(f"Response: {response}")

            if response.status_code != 200:
                self.logging.error(
                    f"Invoice not found: {response.status_code}: {response.content}"
                )
                return response.content

            responseJson = response.json()
            self.logging.info(f"Proxy Response: {responseJson}")

            return responseJson

        except Exception as ex:
            self.logging.warning(f"Invoice by proxy failed: {ex}")

        return response

    def isReady(self):
        try:
            if not self.setTokens():
                self.logging.info(f"Proxy not reachable: {self.env.api_url}.")
            else:
                self.logging.info(f"Proxy URL: {self.invoice_endpoint}.")

        except Exception as ex:
            self.logging.error(f"API Client error: {ex}.")
            return False

        return True

    def setApiKey(self):
        if (
            self.env.api_username is None
            or self.env.api_password is None
        ):
            self.logging.error(f"The API auth details are not defined!")
            return

        auth_string = (
            self.env.api_username + ":" + self.env.api_password
        ).encode()
        self.api_key = base64.b64encode(auth_string).decode()

        return self.api_key

    def setTokens(self):
        if self.env.api_url is None:
            self.logging.error(f"Proxy URL is not defined")
            return

        request_auth_url = self.env.api_url + "/oauth/token"
        request_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "api-auth": self.api_key,
        }
        request_body = {
            "grant_type": "password",
            "client_id": self.env.client_id,
            "client_secret": self.env.client_secret,
            "username": self.env.api_username,
            "password": self.env.api_password,
        }

        response = requests.post(
            url=request_auth_url, headers=request_headers, data=request_body
        )
        if response.status_code != 200:
            self.logging.error(
                f"Proxy Tokens Error: {response.status_code}: {response.content}"
            )
            return False

        self.invoice_endpoint = (
            self.env.api_url + self.env.api_invoice_url
        )
        self.payment_endpoint = (
            self.env.api_url + self.env.api_payment_url
        )

        responseJson = response.json()

        self.access_token = responseJson["access_token"]
        self.refresh_token = responseJson["refresh_token"]

        return True
