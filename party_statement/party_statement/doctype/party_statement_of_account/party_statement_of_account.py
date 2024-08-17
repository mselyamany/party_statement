# Copyright (c) 2023, Infinity Systems and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_balance_on
from erpnext.accounts.party import get_party_details, get_party_account_currency


class PartyStatementOfAccount(Document):
	def validate(self):
		pass
	
	@frappe.whitelist()
	def get_statement(self):
		date_filter = ''
		
		if self.date_to:
			date_to = self.date_to
		else:
			date_to = self.posting_date
		if self.date_to and self.date_from:
			date_filter = "AND posting_date BETWEEN '{0}' and '{1}'".format(self.date_from, date_to)
		sql = """
			SELECT 
				if(debit>0, debit, credit) as amount,
				(CASE 
					WHEN voucher_type = 'Sales Invoice' and credit > 0 THEN 'Credit Note'
					WHEN voucher_type = 'Purchase Invoice' and debit > 0 THEN 'Debit Note'
					ELSE voucher_type
				END) AS transaction_type,
				posting_date, party_type, party, account_currency, voucher_type, voucher_no, is_cancelled,
				if(debit_in_account_currency > 0 , debit_in_account_currency, credit_in_account_currency) as amount_in_account_currency,
				0 as paid_amount
			FROM `tabGL Entry`

			WHERE 
				party = '{0}'
				AND party_type = '{1}'
				AND is_cancelled = 0
				AND company = '{2}'
				{3}
			ORDER By posting_date ASC
		""".format(self.party, self.party_type, self.company, date_filter)

		#frappe.throw(sql)

		sql =  frappe.db.sql(sql, as_dict = 1)
		for row in sql:
			if row['voucher_type'] in ['Sales Invoice', 'Purchase Invoice', 'Payment Entry', 'Enhanced Payment Entry']:
				row['paid_amount'] = frappe.db.get_value(row['voucher_type'], row['voucher_no'], 'paid_amount')
		return sql

	@frappe.whitelist()
	def get_party_info(self):
		if not self.party_type or not self.party or not self.company or not self.posting_date:
			return
		full_name_field = 'customer_name' if self.party_type == 'Customer' else 'supplier_name'
		group_code_field = 'customer_group' if self.party_type == 'Customer' else 'supplier_group'
		group_name_field = 'customer_group_name' if self.party_type == 'Customer' else 'supplier_group_name'
		
		party_name = frappe.db.get_value(self.party_type, self.party, full_name_field)
		
		group_code = frappe.db.get_value(self.party_type, self.party, group_code_field)
		
		group_name = frappe.db.get_value(self.party_type + ' Group', group_code, group_name_field)
		
		balance = get_balance_on(date = self.posting_date,party_type= self.party_type, party= self.party, company= self.company, in_account_currency= True)
		balance_base = get_balance_on(date = self.posting_date,party_type= self.party_type, party= self.party, company= self.company, in_account_currency= False)
		currency = ''
		last_payment_info = frappe.db.sql("""
			SELECT 
				if(debit>0, debit, credit) as amount,
				posting_date, party_type, party, account_currency, voucher_type, voucher_no, is_cancelled,
				if(debit_in_account_currency > 0 , debit_in_account_currency, credit_in_account_currency) as amount_in_account_currency
			FROM 
				`tabGL Entry`
			WHERE 
				party = '{0}'
				AND party_type = '{1}'
				AND is_cancelled = 0
				AND company = '{2}'
				AND voucher_type in ('Payment Entry', 'Enhanced Payment Entry')
			ORDER By creation DESC
		""".format(self.party, self.party_type, self.company), as_dict= 1)
		
		party_info = {
				'balance': balance,
				'balance_base': balance_base,
				'currency': get_party_account_currency(party= self.party, party_type= self.party_type, company= self.company),
				'party_name': party_name,
				'group_name': group_name
			}
		if last_payment_info:
			last_payment_info = last_payment_info[0]

			party_info = {
				'balance': balance,
				'balance_base': balance_base,
				'currency': last_payment_info['account_currency'],
				'last_payment_voucher': last_payment_info['voucher_no'],
				'last_payment_amount': last_payment_info['amount_in_account_currency'],
				'last_payment_date': last_payment_info['posting_date'],
				'party_name': party_name,
				'group_name': group_name
			}
		
		return party_info
		
