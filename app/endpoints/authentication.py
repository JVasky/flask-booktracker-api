from app import api
from app.models.users import User
from app.models.schemas import UserSchema, LoginSchema
from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.jwt_custom import dev_required
import datetime


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
        user = User.query.filter_by(username=data['username'], active=True).first()
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


class DevTokenAPI(Resource):
    @dev_required
    def post(self):
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if user is None:
            return {
                'message': 'Invalid token'
            }, 401
        users_schema = UserSchema()
        u = users_schema.dump(user)
        expires = datetime.timedelta(days=365)
        token = create_access_token(u, expires_delta=expires)
        return {
            'token': token
        }, 201


api.add_resource(LoginAPI, '/login', endpoint='login')
api.add_resource(DevTokenAPI, '/create-dev-token', endpoint='create-dev-token')
