from app import db, api
from app.models.users import User, Role
from app.models.schemas import UserSchema, CreateUserSchema, LoginSchema
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.jwt_custom import admin_required


class LoginAPI(Resource):
    def post(self):
        data = request.get_json()
        if len(data) == 0:
            return {
                "message": "Request params required"
            }, 400
        login_schema = LoginSchema()
        errors = login_schema.validate(data)
        if len(errors) != 0:
            response = {
                'message': 'there were errors with the user submission',
                'errors': errors
            }
            return response, 400
        data = login_schema.load(data)
        user = User.query.filter_by(username=data['username']).first()
        if user is None:
            return {
                'message': 'Invalid username or password'
            }, 401
        if user.check_password(data['password']):
            users_schema = UserSchema()
            u = users_schema.dump(user)
            token = create_access_token(identity=u)
            return {
                'token': token
            }, 200
        else:
            return {
                "message": "Invalid username or password"
            }, 401


class UserAPI(Resource):
    @admin_required
    def get(self, user_id):
        user = User.query.options(db.joinedload(User.roles)).filter_by(id=user_id).first()
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

    @jwt_required
    def post(self):
        data = request.get_json()
        if len(data) == 0:
            return {
                "message": "Request params required"
            }, 400
        create_user_schema = CreateUserSchema()
        errors = create_user_schema.validate(data)
        if len(errors) == 0:
            data = create_user_schema.load(data)

            # check username
            user = User.query.filter_by(username=data['username']).first()
            if user is not None:
                return {
                    'message': 'Username exists!'
                }, 400
            
            # check email
            user = User.query.filter_by(email=data['email']).first()
            if user is not None:
                return {
                    'message': 'Email exists!'
                }, 400

            # create user
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
            return "", 201  
        else:
            response = {
                'message': 'there were errors with the user submission',
                'errors': errors
            }
            return response, 400


api.add_resource(UserAPI, '/users/<int:user_id>', endpoint='user')
api.add_resource(UserListAPI, '/users', endpoint='users')
api.add_resource(LoginAPI, '/login', endpoint='login')
