import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_party_details

@frappe.whitelist()
def invoice_on_submit(doc, method):
    party_type = None
    if doc.doctype == 'Sales Invoice':
        party_type = 'Customer'
    else:
        party_type = 'Supplier'
    party_details = get_party_details(company= doc.company, party_type= party_type, party= doc.customer if party_type == 'Customer' else doc.supplier, date= doc.posting_date)
    #frappe.throw(str(party_details['party_balance']))
    frappe.db.set_value(doc.doctype, doc.name, 'party_balance_after_invoice', party_details['party_balance'])