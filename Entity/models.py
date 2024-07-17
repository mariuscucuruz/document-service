from pydantic import BaseModel
from typing import Optional, List
import uuid


class Invoice(BaseModel):
    id: uuid.UUID
    date: str
    total_cost: float
    payment_type: str
    invoice_provider: str
    issuer_address: str
    issuer_details: str
    invoice_url: str
    # items: [InvoiceItem!]


class InvoiceItem(BaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    date: str
    total: float
    session_id: float
    rfid_card: float


class EmailRequest(BaseModel):
    recepient: str
    body_text: str
    subject_text: str


class EmailInvoiceRequest(BaseModel):
    recepient: Optional[str]
    username: Optional[str]
    bdr_id: Optional[str]
    invoice_id: Optional[str]
    invoice_number: Optional[str]
    invoice_url: Optional[str]
    date_range_from: Optional[str]
    date_range_until: Optional[str]
