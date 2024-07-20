#!/usr/bin/env python3

__author__ = "Marius Cucuruz"
__license__ = "BSD License"

import json
import datetime
from pathlib2 import Path
import pdfkit
from environment import LoadEnv
from Service.logg import Log
from Service.Data.graphQuery import Query
from Service.Data.caching import Caching
from Service.proxy import InvoiceProxy
from Service.RMQ.consumer import RMQConsumer
from Service.RMQ.producer import RMQProducer
from Service.storage import Storage


class Main:
    """
    Document Service
    """
    def __init__(self):
        self.env = LoadEnv()
        self.log = Log(__class__.__name__)
        self.graph_ql = Query()
        self.exchange = RMQProducer()
        self.storage = Storage(bucket_name=self.env.storage_bucket_name)
        self.invoice_proxy = InvoiceProxy()


    def rmq_callback(self, ch, method, properties, body):
        """
        RMQ callback
        """
        self.log.info(f"---[ Listener::{properties} ]---")

        message_received = body.decode("utf-8")
        message_json = json.loads(message_received)

        actual_invoice_data = message_json
        if "GBP" in message_json:
            actual_invoice_data = message_json["GBP"]

        if (
            "pdf_html" in actual_invoice_data
            and isinstance(actual_invoice_data["pdf_html"], str)
            and len(actual_invoice_data["pdf_html"]) > 0
        ):
            session_id = actual_invoice_data["sessions"][0]["internal_id"]
            pdf_filename = actual_invoice_data["pdf_filename"] or "tmp.pdf"
            unique_filename = f"{session_id}_{pdf_filename}"

            invoice_url = self.write_to_local_file(
                pdf_contents=actual_invoice_data["pdf_html"] or "",
                pdf_filename=unique_filename,
            )

            actual_invoice_data["invoice_url"] = invoice_url

        result = self.graph_ql.message_handler(
            json.dumps(actual_invoice_data), properties
        )
        self.log.info(f"Query Result: {result}.")

        if properties.reply_to:
            if self.exchange.connect():
                self.exchange.produce(
                    exchange=self.env.rmq_exchange,
                    routing_key=properties.reply_to,
                    json_data=result,
                    correlation_id=properties.correlation_id,
                )

        return None


    def write_to_local_file(self, pdf_contents: str, pdf_filename: str):
        """
        Write PDF to local file
        """
        basefilename = Path(pdf_filename)
        tmp_file = f"pdfs/{basefilename.name}"

        if pdf_contents.startswith("%PDF-1.4"):
            with open(tmp_file, mode="w", encoding="UTF-8") as local_file_pdf:
                local_file_pdf.write(pdf_contents)
        else:
            try:
                pdf_options = {
                    "orientation": "Landscape",
                    "page-size": "A4",
                    "margin-top": "1.75cm",
                    "margin-left": "1.75cm",
                    "margin-bottom": "1.75cm",
                    "margin-right": "1.75cm",
                }
                pdfkit.from_string(
                    input=pdf_contents,
                    output_path=tmp_file,
                    options=pdf_options,
                )
            except Exception as ex:
                self.log.error(f"PDF error {tmp_file}: {ex}.")
                return tmp_file

        local_asset = Path(tmp_file)

        if self.storage.is_ready():
            self.storage.upload_object(local_asset.absolute())
            return self.storage.share_object_get_url(local_asset.name, 999)

        return local_asset.name


    def email_via_rmq(self, recipient: str, body_text: str, subject_text:str="Req Email via RMQ by Document Service"):
        """
        Publish message to email service.
        """
        try:
            payload = {
                "sender": self.env.email_default_sender,
                "recipients": [recipient, "accounts@example.com"],
                "subject": subject_text,
                "body": body_text,
                "bucket": self.env.storage_bucket_name,
                "attachments": ["pdfs/tmp.pdf"],
            }

            self.exchange.produce(
                json_data=json.dumps(payload),
                correlation_id=datetime.datetime.now(),
                exchange=self.env.email_service_rmq_echange,
                routing_key=self.env.email_service_rmq_routekey,
            )

        except Exception as ex:
            self.log.warning(f"Email service cannot accept request: {ex}")
            return False

        return True


    def get_invoice(self, invoiceId: str):
        """
        Store the details of the request to be processed later.
        """
        try:
            the_document = self.graph_ql.find(invoiceId)
            self.log.info(f"Acknowledge receipt: {the_document}.")

        except Exception as ex:
            self.log.warning(f"Cannot process request: {ex}")
            return False

        return json.loads(the_document)


class RMQListener:
    """
    RMQListener class
    """
    def __init__(self, callback):
        self.callback = callback
        self.queue = RMQConsumer()
        self.env = LoadEnv()
        self.caching = Caching().get_client()

    def init_consumer(self):
        """
        Initialize consumer
        """
        if self.queue.connect():
            if self.queue.declare_consumer(callback=self.callback):
                try:
                    self.queue.start_consumer()
                except KeyboardInterrupt:
                    self.caching.set("status", "unhealthy")
                    print("Keyboard Interrupt.")
                    exit(0)


if __name__ == "__main__":
    main = Main()
    rmq = RMQListener(main.rmq_callback)
    rmq.init_consumer()
