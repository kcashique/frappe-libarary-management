frappe.pages['import-books'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'None',
		single_column: true
	});

	// load html content
	$(frappe.render_template("import_books", {})).appendTo(page.body);

	page.book_importer = new BookImporter(page)
}

class BookImporter {
	constructor(page) {
		this.page = page;
		this.bind_events();
	}

	bind_events() {
		$("#import_books_btn").on('click', () => this.import_books());
	}

	import_books() {
		const number_of_books = parseInt($("#number_of_books").val()) || 20;
		const title = $("#title").val() || '';
		const authors = $("#authors").val() || '';
		const isbn = $("#isbn").val() || '';
		const publisher = $("#publisher").val() || '';
		const starting_page = parseInt($("#starting_page").val()) || 20;

		// Validate input
		if (number_of_books <= 0 || number_of_books > 100) {
			frappe.throw(__('Number of books must be between 1 and 100'));
			return;
		}

		// Show progress section
		$('.import-results').show();
		$('#import_status').text('Fetching books from Frappe Library API...');
		$('#import_progress').width('0%').attr('aria-valuenow', 0).text('0%');
		$('#books_list').empty();

		// server call implimentation
		frappe.call({
			method: "library_management.library_management.page.import_books.import_books.import_books",
			args: {
				"number_of_books": number_of_books,
				"title": title,
				"authors": authors,
				"isbn": isbn,
				"publisher": publisher,
				"starting_page": starting_page
			},
			callback: (r) => {
				if (r.message) {
					const result = r.message;

					//updating results
					$('#import_status').text(`Imported ${result.imported_count} books succesfullly. ${result.existing_count} books already existed.`);

					//set progress 100%
					$("#import_progrss").width('100%').attr("aria-valuenow", 100).text('100%');

					//display the list of imported books
					if (result.imported_books.length > 0) {
						let html = '<div class="table-responsive"><table class="table table-bordered">';
						html += '<thead><tr><th>ISBN</th><th>Title</th><th>Authors</th><th>Publisher</th></tr></thead>';
						html += '<tbody>';

						result.imported_books.forEach(book => {
							html += `<tr>
								<td>${book.isbn}</td>
								<td>${book.title}</td>
								<td>${book.authors}</td>
								<td>${book.publisher}</td>
							</tr>`;
						});

						html += '</tbody></table></div>';
						$("#books_list").html(html);
					} else {
						$("#books_list").html('<div class="alert alert-warning "> No new books where imported.</div>');
					}
				}
			},
			error: (r) => {
				$("#import-status").text('Error Importing Books : ' + r.message);
				$("#import-progress").addClass('bg-danger');
			}
		});
	}
}