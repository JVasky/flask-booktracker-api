from app import api, db
from app.models.users import User, Role
from app.models.schemas import CreateUserSchema, UserSchema, LoginSchema
from flask import request, current_app as app
from flask_restful import Resource
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.jwt_custom import dev_required
from sqlalchemy.exc import SQLAlchemyError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
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


class SignUpAPI(Resource):
    def post(self):
        data = request.get_json()
        if 'roles' in data:
            del data['roles']
        if data is None or len(data) == 0:
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
            roles = Role.query.filter(Role.name.in_(data['roles'])).all()
            for r in roles:
                u.roles.append(r)
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
            sendWelcomeEmail(u)
            return "", 201  
        else:
            response = {
                'message': 'there were errors with the user submission',
                'errors': errors
            }
            return response, 400


def sendWelcomeEmail(user):
    fromaddr = app.config['SMTP_FROM_EMAIL']
    toaddr = user.email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Welcome to Booktracker!'
    body = f"""<h3>Welcome to BookTracker {user.first_name}!</h3> <p>Your username is {user.username}.
    Feel free to login and start journaling your reading adventures.</p>

    <p>Happy reading!</p>
    
    ~ Jim""" 
    msg.attach(MIMEText(body, 'html'))
    server = smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(app.config['SMTP_USER'], app.config['SMTP_PASSWORD'])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)


api.add_resource(LoginAPI, '/login', endpoint='login')
api.add_resource(SignUpAPI, '/signup', endpoint='signup')
api.add_resource(DevTokenAPI, '/create-dev-token', endpoint='create-dev-token')
