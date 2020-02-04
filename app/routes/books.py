from app import app
from app.models.books import Book
from app.models.schemas import BookSchema
from flask import jsonify


@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.order_by(Book.id).all()
    if books is None:
        response = {
            'message': 'there are no books'
        }
        return jsonify(response), 404
    else:
        books_schema = BookSchema(many=True)
        result = books_schema.dumps(books)
        response = {
            'data': result
        }
        return jsonify(response)


@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        response = {
            'message': 'book does not exist'
        }
        return jsonify(response), 404
    else:
        book_schema = BookSchema()
        result = book_schema.dumps(book)
        response = {
            'data': result
        }
        return jsonify(response)


@app.route('/books/author/<author_id>', methods=['GET'])
def get_books_by_author(author_id):
    books = Book.query.filter(Book.authors.any(id=author_id)).all()
    if len(books) == 0:
        response = {
            'message': 'no books by author'
        }
        return jsonify(response), 404
    else:
        book_schema = BookSchema(many=True)
        result = book_schema.dumps(books)
        response = {
            'data': result
        }
        return jsonify(response)


@app.route('/books/title/search/<title>', methods=['GET'])
def search_titles(title):
    books = Book.query.filter(Book.name.ilike(f'%{title}%')).all()
    if len(books) == 0:
        response = {
            'message': 'no books match'
        }
        return jsonify(response), 404
    else:
        book_schema = BookSchema(many=True)
        result = book_schema.dumps(books)
        response = {
            'data': result
        }
        return jsonify(response)