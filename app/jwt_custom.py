from functools import wraps
from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_claims
)
from . import jwt


# custom decorator to verify admin
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if 'admin' not in claims['roles'] and 'developer' not in claims['roles']:
            return {
                'message': 'Admins only!'
            }, 403
        else:
            return fn(*args, **kwargs)
    return wrapper


def dev_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if 'developer' not in claims['roles']:
            return {
                'message': 'Developers only!'
            }, 404
        else:
            return fn(*args, **kwargs)
    return wrapper

# Add roles to claims on token creation
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': user['roles']}

# Add username to identity on token creation
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user['username']
