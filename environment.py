#!/usr/bin/env python3
import os
from dotenv import load_dotenv


class LoadEnv:
    def __init__(self) -> None:
        load_dotenv()
        self.app_name = os.environ.get("app_name")
        self.app_host = os.environ.get("app_host")
        self.app_port = os.environ.get("app_port")
        self.app_debug = os.environ.get("app_debug")

        self.email_service = os.environ.get("email_service")
        self.email_default_sender = os.environ.get("email_default_sender")
        self.email_service_rmq_echange = os.environ.get("email_service_rmq_echange")
        self.email_service_rmq_routekey = os.environ.get("email_service_rmq_routekey")

        self.hasura_db_host = os.environ.get("hasura_db_host")
        self.hasura_db_port = os.environ.get("hasura_db_port")
        self.hasura_realm_username = os.environ.get("hasura_realm_username")
        self.hasura_realm_password = os.environ.get("hasura_realm_password")
        self.hasura_realm_host = os.environ.get("hasura_realm_host")
        self.hasura_realm_port = os.environ.get("hasura_realm_port")
        self.hasura_realm_client_id = os.environ.get("hasura_realm_client_id")
        self.hasura_realm_grant_type = os.environ.get("hasura_realm_grant_type")
        self.hasura_admin_secret = os.environ.get("hasura_admin_secret")

        self.api_username = os.environ.get("api_username")
        self.api_password = os.environ.get("api_password")
        self.api_url = os.environ.get("api_url")
        self.api_invoice_url = os.environ.get("api_invoice_url")
        self.api_payment_url = os.environ.get("api_payment_url")
        self.client_secret = os.environ.get("client_secret")
        self.client_id = os.environ.get("client_id")

        self.storage_endpoint = os.environ.get("storage_endpoint")
        self.storage_access_key = os.environ.get("storage_access_key")
        self.storage_secret_key = os.environ.get("storage_secret_key")
        self.storage_bucket_name = os.environ.get("storage_bucket_name")

        self.rmq_user = os.environ.get("rmq_user")
        self.rmq_pass = os.environ.get("rmq_pass")
        self.rmq_host = os.environ.get("rmq_host")
        self.rmq_port = os.environ.get("rmq_port")
        self.rmq_vhost = os.environ.get("rmq_vhost")
        self.rmq_queue = os.environ.get("rmq_queue")
        self.rmq_exchange = os.environ.get("rmq_exchange")

        self.redis_host = os.environ.get("redis_host")
        self.redis_port = os.environ.get("redis_port")
