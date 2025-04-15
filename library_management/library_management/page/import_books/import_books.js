frappe.pages['import-books'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'None',
		single_column: true
	});

	// load html content
	$(frappe.render_template("import_books", {})).appendTo(page.body);
}