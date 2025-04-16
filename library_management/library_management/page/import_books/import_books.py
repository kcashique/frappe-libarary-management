import frappe, requests


@frappe.whitelist()
def import_books(
    number_of_books, title="", authors="", isbn="", publisher="", starting_page=1
):
    """
    Import books from Frappe Library API
    Args:
        number_of_books: Number of books to import (max 100)
        title: Filter by book title
        authors: Filter by book authors
        isbn: Filter by book ISBN
        publisher: Filter by book publisher
        starting_page: Starting page number for API pagination

    Returns:
        dict: Result of import operation
    """
    number_of_books = int(number_of_books)
    starting_page = int(starting_page)

    if number_of_books <= 0 or number_of_books > 100:
        frappe.throw("Numbeer of books must be between 1 to 100")

    # calculate how many api we need to make
    books_per_page = 20
    num_pages = int(number_of_books / books_per_page)

    all_books = []
    current_page = starting_page

    for i in range(num_pages + 1):
        params = {"page": current_page}

        if title:
            params["title"] = title

        if authors:
            params["authors"] = authors

        if isbn:
            params["isbn"] = isbn

        if publisher:
            params["publisher"] = publisher

        try:
            response = requests.get(
                "https://frappe.io/api/method/frappe-library", params=params
            )
            response.raise_for_status()

            books_data = response.json().get("message", [])

            if not books_data:
                break

            all_books.extend(books_data)
            current_page += 1

            if len(all_books) >= number_of_books:
                all_books = all_books[:number_of_books]
                break

        except Exception as e:
            frappe.log_error(
                f"Error fetching books from API: {str(e)}", "Library API Import Error"
            )
            frappe.throw(f"Error fetching books: {str(e)}")

    imported_books = []
    existing_count = 0

    # check book is alreagy exist
    for book_data in all_books:
        if frappe.db.exists("Book", {"isbn": book_data.get("isbn")}):
            existing_count += 1
            continue

        # create new books
        try:
           new_book = frappe.new_doc("Book")

           new_book.title = book_data.get("title")
           new_book.author = book_data.get("authors")
           new_book.isbn = book_data.get("isbn")
           new_book.publisher = book_data.get("publisher")
           new_book.num_pages = book_data.get("num_pages")
           new_book.publication_date = book_data.get("publication_date")
           new_book.langague_code = book_data.get("langague_code")
           new_book.avarage_rating = book_data.get("avarage_rating")
           new_book.stock = 1

           new_book.insert()
           frappe.db.commit()

           imported_books.append({
               "isbn"  : new_book.isbn,
               "authors" : new_book.author,
               "title" : new_book.title,
               "publisher" : new_book.publisher
           })

        except Exception as e:
            frappe.log_error(f"Error importing book {book_data.get('title')}: {str(e)}", "Library Book Import Error")

    return {
        "imported_count": len(imported_books),
        "existing_count": existing_count,
        "total_fetched" : len(all_books),
        "imported_books" : imported_books
    }
