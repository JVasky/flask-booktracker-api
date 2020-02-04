from app import db, api
from app.models.authors import Author
from app.models.books import Book
from app.models.schemas import AuthorSchema
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError


class AuthorListAPI(Resource):
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


class AuthorAPI(Resource):
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


api.add_resource(AuthorListAPI, '/authors', endpoint='authors')
api.add_resource(AuthorAPI, '/authors/<int:author_id>', endpoint='author')
