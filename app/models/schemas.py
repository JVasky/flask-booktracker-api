from .authors import Author
from .books import Book
from .users import User, Role
from app import ma
from marshmallow import validates, ValidationError
from marshmallow.validate import Length
import re


class LowerCased(ma.Field):
    # Field that de/serializes to a lowercase string

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.lower()

    def _deserialize(self, value, attr, data, **kwargs):
        return value.lower()


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        exclude = ["password"]

    roles = ma.Pluck('RoleSchema', 'name', many=True)


class RoleSchema(ma.ModelSchema):
    class Meta:
        model = Role


class CreateUserSchema(ma.Schema):
    username = LowerCased(required=True, validate=Length(max=30))
    email = ma.Str(required=True, validate=Length(max=120))
    first_name = ma.Str(required=True, validate=Length(max=30))
    last_name = ma.Str(required=True, validate=Length(max=30))
    password = ma.Str(required=True, validate=Length(min=8))
    active = ma.Str(missing=True)
    roles = ma.List(ma.Str(validate=Length(max=30)), missing=['user'])

    @validates('email')
    def is_valid_email(self, value):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if not re.search(regex, value):
            raise ValidationError("Email must be in valid format!")

    @validates('password')
    def is_valid_password(self, value):
        '''
        Should have at least one number.
        Should have at least one uppercase and one lowercase character.
        Should have at least one special symbol.
        Should be at least 8 characters long.
        '''
        regex = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$'
        pat = re.compile(regex)
        mat = re.search(pat, value)
        if not mat:
            raise ValidationError("Password invalid!")

    class Meta:
        model = User
        exclude = ["password"]


class LoginSchema(ma.Schema):
    username = ma.Str(required=True, validate=Length(max=30))
    password = ma.Str(required=True, validate=Length(min=8))


class BookSchema(ma.ModelSchema):
    class Meta:
        model = Book
        exclude = ['user_ratings']

    authors = ma.List(ma.HyperlinkRelated('author', url_key='author_id'))


class CreateBookSchema(ma.Schema):
    title = ma.Str(required=True, validate=Length(max=30))
    description = ma.Str(required=True, validate=Length(max=120))
    authors = ma.List(ma.Integer, required=True)

    class Meta:
        model = Book


class AuthorSchema(ma.ModelSchema):
    class Meta:
        model = Author

    books = ma.List(ma.HyperlinkRelated('book', url_key='id'))


class CreateAuthorSchema(ma.Schema):
    first_name = ma.Str(required=True, validate=Length(max=100))
    middle_name = ma.Str(validate=Length(max=100), missing=None)
    last_name = ma.Str(validate=Length(max=100), missing=None)
    bio = ma.Str(validate=Length(max=100000), missing=None)
    books = ma.List(ma.Integer, missing=[])


class UpdateAuthorSchema(ma.Schema):
    first_name = ma.Str(required=True, validate=Length(max=100))
    middle_name = ma.Str(validate=Length(max=100), missing=None)
    last_name = ma.Str(validate=Length(max=100), missing=None)
    bio = ma.Str(validate=Length(max=100000), missing=None)
    approved = ma.Boolean(missing=False)


class RatingsSchema(ma.Schema):
    rating = ma.Str()
    notes = ma.Str()
    book = ma.Nested(BookSchema)
