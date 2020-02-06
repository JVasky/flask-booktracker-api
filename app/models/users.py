from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class LowerCaseText(db.TypeDecorator):
    # Converts strings to lower case

    impl = db.String(30)

    def process_bind_param(self, value, dialect):
        return value.lower()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(LowerCaseText, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(30), index=True, nullable=False)
    last_name = db.Column(db.String(30), index=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_dt = db.Column(db.DateTime, server_default=db.func.now())
    modified_dt = db.Column(db.DateTime, onupdate=db.func.now())
    roles = db.relationship('Role', secondary='user_roles')
    user_ratings = db.relationship('Book', secondary='ratings')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    users = db.relationship(User, secondary='user_roles')


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        primary_key=True
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey(Role.id),
        primary_key=True
    )
