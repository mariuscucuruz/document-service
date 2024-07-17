SAVE_INVOICE_MUTATION = """
mutation SaveInvoice {
    insert_invoice(objects: {
        [qlInvoiceFieldsPlaceholder], 
        invoice_items: {
            data: {[qlInvoiceItemsFieldsPlacehoder]}
        }
    }) {returning {id}}
}
"""

EMAIL_INVOICE_REQUEST_MUTATION = """
mutation EmailInvoiceRequest {
  insert_email_request_queue(objects: {[qlEmailInvoiceRequestPlaceholder]})
  {returning {uuid created_at}}
}
"""

FETCH_INVOICE_BY_UUID_QUERY = """
query FetchInvoice {
  invoice (where: {invoice_items: {[qlInvoiceItemAttributeValueObjPlaceholder]}}) {
  invoice (where: {id: {_eq: "66791656-174c-4540-a848-b09a0c8d410c"}}) {

      invoice_url
    payment_status
    invoice_items {
      internal_id
      bdr_id
    }
  }
}
"""

FETCH_INVOICE_BY_BDR_QUERY = """
query FetchInvoice {
  invoice (where: {invoice_items: {[qlInvoiceItemAttributeValueObjPlaceholder]}}) {
    invoice_url
    payment_status
    invoice_items {
      internal_id
      bdr_id
    }
  }
}
"""