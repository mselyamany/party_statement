// Copyright (c) 2023, Infinity Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Party Statement Of Account', {
	refresh: function(frm) {
		frm.set_query("party_type", function() {
			return {
				"filters": {
					"name": ["in",["Customer", "Supplier"]],
				}
			};
		});

	},
	get_statement: function(frm){
		frappe.call({
			method: "get_statement",
			doc: frm.doc,
			freeze: true,
			freeze_message: "Getting Statement......",
			callback: function(r) {
				console.log(r)
				if(r.message){
					frm.clear_table('details');
					r.message.forEach(line => {
						var row = frm.add_child('details');
						row.transaction_type = line.transaction_type;
						row.voucher_type = line.voucher_type;
						row.voucher_no = line.voucher_no;
						row.posting_date = line.posting_date;
						row.transaction_amount = line.amount_in_account_currency;
						row.currency = line.account_currency;
						row.amount_in_base_currency = line.amount
						row.paid_amount = line.paid_amount;
					});	
					frm.refresh_field('details');
				}
			}
		});

	},
	get_party_info: function(frm){
		frappe.call({
			method: "get_party_info",
			doc: frm.doc,
			freeze: true,
			freeze_message: "Getting Party Information......",
			callback: function(r) {
				//console.log(r.message)
				if(r.message){
					frm.set_value('party_balance_in_party_currency', r.message.balance)
					frm.set_value('balance_in_base_currency', r.message.balance_base)
					frm.set_value('last_payment_amount', r.message.last_payment_amount)
					frm.set_value('last_payment_number', r.message.last_payment_voucher)
					frm.set_value('last_payment_date', r.message.last_payment_date)
					frm.set_value('party_account_currency', r.message.currency)
					frm.set_value('party_name', r.message.party_name)
					frm.set_value('party_group_name', r.message.group_name)
				}
			}
		});
	},
	party_type: function(frm){
		frm.set_value('party', null)
		frm.set_value('party_name', null)
		frm.set_value('party_group_name', null)
		frm.clear_table('details');
		frm.refresh_field('details');
		frm.trigger('get_party_info');
	},
	party: function(frm){
		frm.clear_table('details');
		frm.refresh_field('details');
		frm.trigger('get_party_info');
	},
	from_date: function(frm){
		frm.clear_table('details');
		frm.refresh_field('details');
	},
	to_date: function(frm){
		frm.clear_table('details');
		frm.refresh_field('details');
	},
	company: function(frm){
		frm.clear_table('details');
		frm.refresh_field('details');
		frm.trigger('get_party_info');
	},
	posting_date: function(frm){
		frm.clear_table('details');
		frm.refresh_field('details');
		frm.trigger('get_party_info');
	},
});
