from app import api, db
from app.models.authors import Author
from app.models.books import Book
from app.models.schemas import AuthorSchema, CreateAuthorSchema
from app.jwt_custom import admin_required
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError


class AuthorListAPI(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page')
        if page is not None and page != '0':
            try:
                page = int(page)
            except ValueError:
                return {
                    'message': 'Invalid page'
                }, 400
            authors = Author.query.order_by(Author.id).paginate(page, 30, False).items
        else:
            authors = Author.query.order_by(Author.id).all()
        if authors is None:
            response = {
                'message': 'there are no authors'
            }
            return response, 404
        else:
            authors_schema = AuthorSchema(many=True)
            result = authors_schema.dumps(authors)
            response = {
                'data': result
            }
            return response

    @admin_required
    def post(self):
        data = request.get_json()
        create_author_schema = CreateAuthorSchema()
        errors = create_author_schema.validate(data)
        if len(errors) == 0:
            data = create_author_schema.load(data)
            if Author.query.filter(and_(
                                        Author.first_name == data['first_name'], 
                                        Author.middle_name == data['middle_name'],
                                        Author.last_name == data['last_name'])).first() is not None:
                return {
                    "message": "Author already exists!"
                }, 400
            a = Author(
                first_name=data['first_name'],
                middle_name=data['middle_name'],
                last_name=data['last_name'],
                bio=data['bio']
            )
            if len(data['books']) > 0:
                books = Book.query.filter(Book.id.in_(data['books'])).all()
                for b in books:
                    a.books.append(b)
            try:
                db.session.add(a)
                db.session.commit()

            except SQLAlchemyError as e:
                db.session.rollback()
                if type(e).__name__ == 'IntegrityError':
                    response = {
                        'message': 'Error inserting new author: ' + e.orig.args[0],
                    }
                else:
                    response = {
                        'message': 'DB error: ' + e.orig.args[0]
                    }
                return response, 500

            return "", 201   
        else:
            response = {
                'message': 'there were errors with the author submission',
                'errors': errors
            }
            return response, 400

    def put(self):
        data = request.get_json()
        create_author_schema = CreateAuthorSchema()
        errors = create_author_schema.validate(data)
        if(len(errors) > 0):
            response = {
                'message': 'there were errors with the author update',
                'errors': errors
            }
            return response, 400
        author = Author.query.filter_by(id=data['id']).first()
        if author is None:
            response = {
                'message': 'author does not exist'
            }
            return response, 404
        else:
            author.first_name = data['first_name']
            author.middle_name = data['middle_name']
            author.last_name = data['last_name']
            author.bio = data['bio']
            db.session.commit()
            return "", 204


class AuthorPendingListAPI(Resource):
    @admin_required
    def get(self):
        authors = Author.query.filter_by(approved=False).order_by(Author.id).all()
        if len(authors) == 0:
            response = {
                'message': 'There are no authors'
            }
            return response, 404
        else:
            authors_schema = AuthorSchema(many=True)
            result = authors_schema.dumps(authors)
            response = {
                'data': result
            }
            return response


class AuthorAPI(Resource):
    @jwt_required
    def get(self, author_id):
        author = Author.query.filter_by(id=author_id).first()
        if author is None:
            response = {
                'message': 'author does not exist'
            }
            return response, 404
        else:
            author_schema = AuthorSchema()
            result = author_schema.dumps(author)
            response = {
                'data': result
            }
            return response


class AuthorApprovalAPI(Resource):
    @admin_required
    def put(self, id):
        author = Author.query.filter_by(id=id).first()
        if author is None:
            response = {
                'message': 'author does not exist'
            }
            return response, 404
        else:
            author.approved = True
            db.session.commit()
            return "", 204


api.add_resource(AuthorListAPI, '/authors', endpoint='authors')
api.add_resource(AuthorPendingListAPI, '/authors/pending', endpoint='authors-pending')
api.add_resource(AuthorAPI, '/authors/<int:author_id>', endpoint='author')
api.add_resource(AuthorApprovalAPI, '/authors/approve/<int:author_id>', endpoint='approve-author')
