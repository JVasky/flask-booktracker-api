from app import db, api
from app.models.authors import Author
from app.models.books import Book
from app.models.users import User
from app.models.ratings import Ratings
from app.models.schemas import BookSchema, CreateBookSchema, RatingsSchema
from app.jwt_custom import admin_required
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask_restful import Resource
from flask import request
from sqlalchemy.exc import SQLAlchemyError


class BookAPI(Resource):
    @jwt_required
    def get(self, id):
        book = Book.query.filter_by(id=id).first()
        if book is None:
            response = {
                'message': 'book does not exist'
            }
            return response, 404
        else:
            book_schema = BookSchema(exclude=['approved', 'user_ratings'])
            result = book_schema.dumps(book)
            response = {
                'data': result
            }
        return response


class BookPendingListAPI(Resource):
    @admin_required
    def get(self):
        books = Book.query.filter_by(approved=False).order_by(Book.id).all()
        if len(books) == 0:
            response = {
                'message': 'There are no books'
            }
            return response, 404
        else:
            books_schema = BookSchema(exclude=['authors', 'user_ratings'], many=True)
            result = books_schema.dumps(books)
            response = {
                'data': result
            }
            return response


class BookListAPI(Resource):
    @jwt_required
    def get(self):
        books = Book.query.filter_by(approved=True).order_by(Book.id).all()
        if len(books) == 0:
            response = {
                'message': 'There are no books'
            }
            return response, 404
        else:
            books_schema = BookSchema(many=True, exclude=['approved', 'user_ratings'])
            result = books_schema.dumps(books)
            response = {
                'data': result
            }
            return response

    @jwt_required
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

            return "", 201   
        else:
            response = {
                'message': 'there were errors with the book submission',
                'errors': errors
            }
            return response, 400


class ReadBookListAPI(Resource):
    @jwt_required
    def get(self, user_id=None):
        if user_id is not None:
            claims = get_jwt_claims()
            if 'admin' not in claims['roles'] and 'developer' not in claims['roles']:
                return {
                    'message': 'Admins only!'
                }, 403
            user = User.query.filter_by(id=user_id).first()
        else:
            username = get_jwt_identity()
            user = User.query.filter_by(username=username).first()
        if user is None:
            response = {
                'message': 'user does not exist'
            }
            return response, 404
        books = Ratings.query.filter_by(user_id=user.id).all()
        if len(books) == 0:
            response = {
                'message': 'no books read'
            }
            return response, 404
        else:
            ratings_schema = RatingsSchema(many=True)
            result = ratings_schema.dumps(books)
            response = {
                'data': result
            }
            return response


class AuthorBookListAPI(Resource):
    @jwt_required
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
    @jwt_required
    def get(self, keyword):
        books = Book.query.filter(db.or_(Book.title.ilike(f'%{keyword}%'), Book.description.ilike(f'%{keyword}%'))).all()
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


class BookApprovalAPI(Resource):
    @admin_required
    def put(self, id):
        book = Book.query.filter_by(id=id).first()
        if book is None:
            response = {
                'message': 'book does not exist'
            }
            return response, 404
        else:
            book.approved = True
            db.session.commit()
            return "", 204


api.add_resource(BookAPI, '/books/<int:id>', endpoint='book')
api.add_resource(BookListAPI, '/books', endpoint='books')
api.add_resource(ReadBookListAPI, '/books/read', '/books/read/<int:user_id>', endpoint='read-books')
api.add_resource(BookPendingListAPI, '/books/pending', endpoint='books-pending')
api.add_resource(BookApprovalAPI, '/books/approve/<int:id>', endpoint='approve-book')
api.add_resource(AuthorBookListAPI, '/books/author/<int:author_id>', endpoint='books_by_author')
api.add_resource(BookTitleSearchAPI, '/books/search/<string:keyword>', endpoint='book_title_search')
