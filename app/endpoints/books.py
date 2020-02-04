from app import db, api
from app.models.authors import Author
from app.models.books import Book
from app.models.schemas import BookSchema, CreateBookSchema
from flask_restful import Resource
from flask import request
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError


class BookAPI(Resource):

    def get(self, id):
        book = Book.query.filter_by(id=id).first()
        if book is None:
            response = {
                'message': 'book does not exist'
            }
            return response, 404
        else:
            book_schema = BookSchema()
            result = book_schema.dumps(book)
            response = {
                'data': result
            }
        return response


class BookListAPI(Resource):
    def get(self):
        books = Book.query.order_by(Book.id).all()
        if books is None:
            response = {
                'message': 'there are no books'
            }
            return response, 404
        else:
            books_schema = BookSchema(many=True)
            result = books_schema.dumps(books)
            response = {
                'data': result
            }
            return response

    def post(self):
        data = request.get_json()
        create_book_schema = CreateBookSchema()
        errors = create_book_schema.validate(data)
        if len(errors) == 0:
            b = Book(
                title=data['title'],
                description=data['description']
            )
            authors = Author.query.filter(Author.id.in_(data['authors'])).all()
            for a in authors:
                b.authors.append(a)
            try:
                db.session.add(b)
                db.session.commit()

            except SQLAlchemyError as e:
                db.session.rollback()
                if type(e).__name__ == 'IntegrityError':
                    response = {
                        'message': 'Error inserting new book: ' + e.orig.args[0],
                    }
                else:
                    response = {
                        'message': 'DB error: ' + e.orig.args[0]
                    }
                return response, 500

            return "", 204   
        else:
            response = {
                'message': 'there were errors with the book submission',
                'errors': errors
            }
            return response, 400


class AuthorBookListAPI(Resource):
    def get(self, author_id):
        books = Book.query.filter(Book.authors.any(id=author_id)).all()
        if len(books) == 0:
            response = {
                'message': 'no books by author'
            }
            return response, 404
        else:
            book_schema = BookSchema(many=True)
            result = book_schema.dumps(books)
            response = {
                'data': result
            }
            return response


class BookTitleSearchAPI(Resource):
    def get(self, keyword):
        books = Book.query.filter(or_(Book.title.ilike(f'%{keyword}%'), Book.description.ilike(f'%{keyword}%'))).all()
        if len(books) == 0:
            response = {
                'message': 'no books match'
            }
            return response, 404
        else:
            book_schema = BookSchema(many=True)
            result = book_schema.dumps(books)
            response = {
                'data': result
            }
            return response


api.add_resource(BookAPI, '/books/<int:id>', endpoint='book')
api.add_resource(BookListAPI, '/books', endpoint='books')
api.add_resource(AuthorBookListAPI, '/books/author/<int:author_id>', endpoint='books_by_author')
api.add_resource(BookTitleSearchAPI, '/books/search/<string:keyword>', endpoint='book_title_search')
