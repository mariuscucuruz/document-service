import datetime
from fastapi import status, HTTPException
from graphql import GraphQLSyntaxError
from helpers import implode_list
import json
import requests
import time
from environment import LoadEnv
from Service.Data.caching import Caching
from Service.logg import Log
from Entity.exceptions import UnsuccessfulResponse
from Service.Data.list_of_queries import (SAVE_INVOICE_MUTATION, EMAIL_INVOICE_REQUEST_MUTATION, FETCH_INVOICE_BY_UUID_QUERY)
from Entity.models import EmailInvoiceRequest


class Query:
    def __init__(self):
        self.logging = Log(self.__class__.__name__)
        self.logging.info("GraphQL Instance created")
        self.env = LoadEnv()
        self.token_expire = 0
        self.refresh_expire = 0

        self.caching = Caching().get_client()

        self.hasura_endpoint = None
        self.headers = None
        self.access_token = None
        self.refresh_token = None

        self.build_jwt_token_retrieval_endpoint()
        self.build_endpoint()

    def build_endpoint(self):
        if self.env.hasura_db_host is None:
            self.logging.error("DB HOST is not defined")
            return
        if self.env.hasura_db_port is None:
            self.logging.error("DB PORT is not defined")
            return

        self.hasura_endpoint = (
            "http://"
            + self.env.hasura_db_host
            + ":"
            + self.env.hasura_db_port
            + "/v1/graphql"
        )
        self.headers = {
            "Content-Type": "application/json",
            "x-hasura-admin-secret": self.env.hasura_admin_secret,
        }


    def build_jwt_token_retrieval_endpoint(self):
        self.hasura_realm_jwt_retrieval_endpoint=None
        self.hasura_realm_jwt_retrieval_headers=None

        if self.env.hasura_realm_host is None:
            self.logging.error("Hasura realm HOST is not defined")
            return
        if self.env.hasura_realm_port is None:
            self.logging.error("Hasura realm PORT is not defined")
            return

        self.hasura_realm_jwt_retrieval_endpoint=(
            "https://"
            + self.env.hasura_realm_host
            + ":"
            + self.env.hasura_realm_port
            + "/realms/hasura/protocol/openid-connect/token"
        )
        self.hasura_realm_jwt_retrieval_headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }


    def retrieve_jwt(self):
        request_payload = {
            "grant_type": "password",
            "client_id": self.env.hasura_realm_client_id,
            "username": self.env.hasura_realm_username,
            "password": self.env.hasura_realm_password
        }
        self.validate_and_set_tokens(request_payload)


    def retrieve_jwt_refresh(self):
        request_payload = {
            "grant_type": "refresh_token",
            "client_id": self.env.hasura_realm_client_id,
            "refresh_token": self.refresh_token
        }
        self.validate_and_set_tokens(request_payload)


    def validate_and_set_tokens(self, request_payload):
        self.logging.info(f"Validate JWT: {request_payload}")

        try:
            response = requests.post(
                self.hasura_realm_jwt_retrieval_endpoint,
                data=request_payload,
                headers=self.hasura_realm_jwt_retrieval_headers,
                timeout=5
            )
        except requests.exceptions.InvalidURL as ex:
            self.logging.error(f"DB url error - {ex}")
        except Exception as ex:
            self.logging.error(f"retrieve_JWT_refresh: {ex}")

        if response.status_code != 200:
            self.logging.error(f"Status code = {response.status_code}")

        response_json = response.json()

        self.access_token = response_json["access_token"]
        self.refresh_token = response_json["refresh_token"]

        self.headers["Authorization"] = "Bearer " + self.access_token

        self.token_expire = time.time() + response_json["expires_in"] - 5
        self.refresh_expire = time.time() + response_json["refresh_expires_in"] - 5


    def token_handler(self):
        if time.time() > self.refresh_expire:
            self.logging.error(f"Retrieving JWT ({self.refresh_expire})")
            self.retrieve_jwt()
            return

        if time.time() > self.token_expire:
            self.logging.error(f"Refreshing JWT ({self.refresh_expire})")
            self.retrieve_jwt_refresh()
            return


    def exec(self, query: str, variables):
        response_json = {}
        request_payload = {"query": query, "variables": variables}

        try:
            self.token_handler()
            response = requests.post(
                self.hasura_endpoint,
                headers=self.headers,
                json=request_payload,
                timeout=5
            )
            response_json = response.json()
            self.logging.info(f"EXEC::Status::{response.status_code}::Payload::{request_payload}")

        except GraphQLSyntaxError as ex:
            self.logging.error(f"Graphql syntax error - {ex}")
        except requests.exceptions.InvalidURL as ex:
            self.logging.error(f"DB url error - {ex}")
        except Exception as ex:
            self.logging.error(f"exec: {ex}")

        self.logging.info(f"JSON Response: {response_json}")

        return json.dumps(response_json, indent=4)


    def message_handler(self, message_received: str, properties):
        self.logging.info(f"RMQ Payload: {message_received}.")

        message_received = message_received.replace(u"\xa0", u" ")
        msg_json = json.loads(message_received.strip())

        query, variables = self.payload_to_query(msg_json)

        if not query.startswith("mutation"):
            return (
                json.dumps(UnsuccessfulResponse.unrecognized()),
                message_received,
                None,
            )

        response = self.exec(query, variables)
        if response == json.dumps({}):
            return json.dumps(UnsuccessfulResponse.empty_db_response())

        return response


    def payload_to_query(self, message_payload):
        # handle invoice attributes:
        invoice_fields = self.filter_payload_to_invoice_fields(message_payload)
        invoice_fields_list = ''
        for key, value in invoice_fields.items():
            if value is not None:
                invoice_fields_list += str(key) + ': "' + str(value) + '",'

        # handle line items attributes:
        invoice_items_fields = self.filter_payload_to_invoice_items_fields(message_payload)
        invoice_items_fields_list = ''
        for line_item in invoice_items_fields:
            for key, value in line_item.items():
                if value is not None:
                    invoice_items_fields_list += str(key) + ': "' + str(value) + '",'

        query = SAVE_INVOICE_MUTATION.replace(
            "[qlInvoiceFieldsPlaceholder]", invoice_fields_list[:-1]
            ).replace(
            "[qlInvoiceItemsFieldsPlacehoder]", invoice_items_fields_list[:-1]
            )
        variables = {}
        self.logging.info(f"QUERY: {query}")

        return query, variables


    def filter_payload_to_invoice_fields(self, payload):
        query_fields = {}
        query_fields['date'] = datetime.date.today().strftime("%Y-%m-%d")

        if 'config' in payload:
            query_fields['invoice_currency'] = payload['config']['currency']
            query_fields['tax_rate'] = payload['config']['tax_rate']
            query_fields['tax_label'] = payload['config']['tax_label']

        if 'status' in payload:
            query_fields['payment_type'] = payload['status']['payment_status']
            query_fields['payment_status'] = payload['status']['payment_status']
            query_fields['payment_mandate'] = payload['status']['mandate']

        if 'summary' in payload:
            query_fields['amount_gross'] = payload['summary']['amount_gross']
            query_fields['amount_net'] = payload['summary']['amount_net']
            query_fields['amount_tax'] = payload['summary']['amount_tax']
            query_fields['total_cost'] = payload['summary']['invoice_total']
            query_fields['donations'] = payload['summary']['donations']

        if 'invoice' in payload:
            query_fields['invoice_number'] = payload['invoice']['invoice_number']
            query_fields['invoice_date'] = payload['invoice']['date']
            # query_fields['invoicee'] = payload['invoice']['to']['name']

        if 'branding' in payload:
            query_fields['invoice_provider'] = payload['branding']['registered_address']['name']
            query_fields['issuer_address'] = implode_list(payload['branding']['registered_address']['address']).replace('\r', '')
            query_fields['issuer_details'] = implode_list({
                payload['branding']['tax_registration'],
                payload['branding']['company_registration']
            }).replace('\r', '')

        if 'invoice_summary' in payload:
            query_fields['amount_gross'] = payload['invoice_summary']['amount_gross'] or None
            query_fields['amount_net'] = payload['invoice_summary']['amount_net'] or None
            query_fields['amount_tax'] = payload['invoice_summary']['amount_tax'] or None
            query_fields['donation_amount'] = payload['invoice_summary']['donation_amount'] or None


        if query_fields is None:
            self.logging.error(f"Error mapping invoice attributes: {payload}.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error mapping invoice attributes: {payload}.",
            )

        return query_fields


    def filter_payload_to_invoice_items_fields(self, payload):
        query_fields = []

        if 'sessions' in payload:
            for invoice_info in payload['sessions']:
                invoice_item = {}
                invoice_item['invoice_id'] = invoice_info['invoice_id']
                invoice_item['internal_id'] = invoice_info['internal_id']
                invoice_item['amount'] = invoice_info['amount']
                invoice_item['cardno'] = invoice_info['cardno']

                invoice_item['poi_id'] = invoice_info['poi_id']
                invoice_item['poi'] = invoice_info['poi']
                invoice_item['site'] = invoice_info['site']

                invoice_item['tariff'] = invoice_info['tariff']
                invoice_item['minutes'] = invoice_info['minutes']
                invoice_item['usage_amount'] = invoice_info['usage_amount']
                invoice_item['consum'] = invoice_info['consum']

                query_fields.append(invoice_item)

        return query_fields


    def record_invoice_to_email_request(self, payload: EmailInvoiceRequest):
        self.logging.info(f"Email Req Payload: {payload}.")

        payload = {
            "completed": False, 
            "invoice_id": payload.invoice_id or None, 
            "invoice_id": payload.invoice_id or None,
            "recipient": payload.recepient or None, 
            "invoice_url": payload.invoice_url or None, 
            "invoice_number": payload.invoice_number or None
        }

        query = EMAIL_INVOICE_REQUEST_MUTATION.replace(
            "[qlEmailInvoiceRequestPlaceholder]", json.dumps(payload))
        variables = {}
        self.logging.info(f"QUERY: {query}")

        response = self.exec(query, variables)
        if response == json.dumps({}):
            return json.dumps(UnsuccessfulResponse.empty_db_response())

        return response


    def find(self, payload):
        self.logging.info(f"Email Req Payload: {payload}.")

        query = FETCH_INVOICE_BY_UUID_QUERY.replace(
            "[qlEmailInvoiceRequestPlaceholder]", json.dumps(payload))
        variables = {}
        self.logging.info(f"QUERY: {query}")

        response = self.exec(query, variables)
        if response == json.dumps({}):
            return json.dumps(UnsuccessfulResponse.empty_db_response())

        return response
