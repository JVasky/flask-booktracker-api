from app import db, api
from app.models.users import User
from app.models.schemas import UserSchema, CreateUserSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError


class UserAPI(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            response = {
                'message': 'user does not exist'
            }
            return response, 404
        else:
            user_schema = UserSchema()
            result = user_schema.dumps(user)
            response = {
                'data': result
            }
            return response


class UserListAPI(Resource):
    def get(self):
        page = request.args.get('page')
        if page is not None and page != '0':
            try:
                page = int(page)
            except ValueError:
                return {
                    'message': 'Invalid page'
                }, 400
            users = User.query.order_by(User.id).paginate(page, 30, False).items
        else:
            users = User.query.order_by(User.id).all()

        if users is None or len(users) == 0:
            response = {
                'message': 'there are no users'
            }
            return response, 404
        else:
            users_schema = UserSchema(many=True)
            result = users_schema.dumps(users)
            response = {
                'data': result
            }
            return response

    def post(self):
        data = request.get_json()
        if len(data) == 0:
            return {
                "message": "Request params required"
            }, 400
        create_user_schema = CreateUserSchema()
        errors = create_user_schema.validate(data)
        if len(errors) == 0:
            u = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            u.set_password(data['password'])
            try:
                db.session.add(u)
                db.session.commit()

            except SQLAlchemyError as e:
                db.session.rollback()
                if type(e).__name__ == 'IntegrityError':
                    response = {
                        'message': 'Error inserting new user: ' + e.orig.args[0],
                    }
                else:
                    response = {
                        'message': 'DB error: ' + e.orig.args[0]
                    }
                return response, 500

            user_schema = UserSchema()
            result = user_schema.dumps(u)
            response = {
                'data': result
            }
            return "", 204  
        else:
            response = {
                'message': 'there were errors with the user submission',
                'errors': errors
            }
            return response, 400


api.add_resource(UserAPI, '/users/<int:user_id>', endpoint='user')
api.add_resource(UserListAPI, '/users', endpoint='users')
