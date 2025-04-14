# Copyright (c) 2025, kcashique and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, today, getdate


class LibraryTransaction(Document):
	pass


def validate_transaction(doc, method):
	if doc.transaction_type == "Issue":
		# checking members outstanding dues.
		member =frappe.get_doc("Member", doc.member)
		if member.out_standing_debt >= 500:
			frappe.throw(f"Cannot issue books to {member.full_name} due to outstanding debt of {member.outstanding_debt}.")
		
		# cheking books avialability
		book = frappe.get_doc("Books", doc.book)
		if book.stock <=0:
			frappe.throw(f"Book {book.title} is out of stock")
		
		# set expected return date with 14 days
		if not doc.expected_return_date:
			doc.doc.expected_return_date= add_days(doc.issue_date, 14)

	elif doc.transaction_type == "Return":
		# find original issue transaction
		issue_transaction = frappe.get_list(
			"Library Transactions",
			filters={
				"transaction_type": "issue",
				"book":doc.book,
				"member":doc.member,
				"status": "Issued"
			},
			order_by="issue_date desc",
			limit=1
		)
		if not issue_transaction:
			frappe.throw("No matching issue transactions")
		
		# rent fee calculation - 10/day, fine 20/day
		issue_doc = frappe.get_doc("Library Transactions", issue_transaction[0].name)
		days_borrowed= date_diff(doc.return_date or today(),issue_doc.issue_date)
		expected_days= date_diff(issue_doc.expected_return_date, issue_doc.issue_date)

		if days_borrowed <= expected_days:
			doc.rent_fee = days_borrowed * 10
		else:
			due_dates= days_borrowed - expected_days
			doc.rent_fee = (expected_days * 10) + (due_dates * 20)
		
		frappe.db.set_value("Library Transaction", issue_doc.name, "Status", "Returned")
	
	
		