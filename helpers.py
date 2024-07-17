import re
import uuid
from Entity.models import Invoice


generic_error_message = "there has been an error, unable to complete request"
invoice_not_found = "no invoice found"
invoice_no_items = "invoice has no items"


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def extract_ids(query_string, variable1, variable2):
    id1 = None
    id2 = None

    regex1 = rf'{variable1}: {{_eq: "([^"]+)"}}|{variable1}: "([^"]+)"'
    regex2 = rf'{variable2}: {{_eq: "([^"]+)"}}|{variable2}: "([^"]+)"'

    match1 = re.search(regex1, query_string)
    if match1:
        id1 = match1.group(1) or match1.group(2)

    match2 = re.search(regex2, query_string)
    if match2:
        id2 = match2.group(1) or match2.group(2)

    if id1 is None and id2 is None:
        raise AttributeError(
            f"Both {variable1} and {variable2} not found in query string"
        )
    if id1 is None and id2 is not None:
        raise AttributeError(f"{variable1} not found in query string")
    if id2 is None and id1 is not None:
        raise AttributeError(f"{variable2} not found in query string")

    return id1, id2


def make_invoice_model(data):
    invoice_response = [Invoice(invoice_id=item["invoice_id"]) for item in data]

    if len(invoice_response) == 0:
        invoice_response = invoice_no_items

    return invoice_response


def implode_list(listObj, glue: str = ", "):
    if listObj is not None and listObj is not list:
        listed = [str(x) for x in listObj]
        return glue.join(listed)

    return glue.join(listObj)
