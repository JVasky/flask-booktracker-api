from app import app, db
from app.models.users import User
from app.models.schemas import UserSchema, CreateUserSchema
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError


@app.route('/login', methods=['POST'])
def login():
    return "login"


@app.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page')
    if page is not None:
        page = int(page)

    if page is None or page == 0:
        users = User.query.order_by(User.id).all()
    else:
        users = User.query.order_by(User.id).paginate(page, 30, False).items
    if users is None or len(users) == 0:
        response = {
            'message': 'there are no users'
        }
        return jsonify(response), 404
    else:
        users_schema = UserSchema(many=True)
        result = users_schema.dumps(users)
        response = {
            'data': result
        }
        return jsonify(response)


@app.route('/users', methods=['POST'])
def create_user():
    create_user_schema = CreateUserSchema()
    data = request.form
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
            return jsonify(response), 500

        user_schema = UserSchema()
        result = user_schema.dumps(u)
        response = {
            'data': result
        }
        return jsonify(response), 20    
    else:
        response = {
            'message': 'there were errors with the user submission',
            'errors': errors
        }
        return jsonify(response), 400
