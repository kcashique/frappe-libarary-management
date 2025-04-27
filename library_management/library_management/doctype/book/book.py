# Copyright (c) 2025, kcashique and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Book(Document):
	pass


def validate_book(doc, method):
	if doc.stock < 0:
		frappe.throw("No Stock Avialbele Now")