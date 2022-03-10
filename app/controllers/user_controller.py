from http import HTTPStatus

from flask import current_app, jsonify, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, NotFound

from app.configs.auth import auth
from app.models.user_model import UserModel
from app.services.register_login_service import validate_request
from app.services.user_admin_service import check_request_update


def signup():
    session = current_app.db.session
    
    data = request.get_json()

    validate_data = validate_request(data)

    password_to_hash = validate_data.pop("password")

    try:
        new_user: UserModel = UserModel(**validate_data)
        new_user.password = password_to_hash

        session.add(new_user)
        session.commit()

        return jsonify(new_user), HTTPStatus.CREATED

    except IntegrityError:
        return {"msg":"email already exists"}, HTTPStatus.CONFLICT

def signin():
    data = request.get_json()
    validate_data = validate_request(data, type_login=True)

    user: UserModel = UserModel.query.filter_by(email=validate_data["email"]).first()

    if not user:
        return {"message": "User not found"}, HTTPStatus.NOT_FOUND
    
    if not user:
        return {"message": "Unauthorized"}, HTTPStatus.UNAUTHORIZED

    user.verify_password(validate_data["password"])
    access_token = create_access_token(identity=user)

    return {"token": access_token}, HTTPStatus.OK
    
@auth.login_required
def get_user_all():

    all_users = UserModel.query.all()

    return jsonify(all_users), HTTPStatus.OK


@jwt_required()
def get_one_user():

    try:
        user = get_jwt_identity()

        return jsonify(user),HTTPStatus.OK
        
    except NotFound:
        return {"message": "User not found"},HTTPStatus.NOT_FOUND
     

@jwt_required()
def update_user():
    try:
        session = current_app.db.session

        user_on = get_jwt_identity()
        update_data = request.get_json()


        valid_request = check_request_update(update_data)

        user:UserModel = UserModel.query.get(user_on["user_id"])

        for key, value in valid_request.items():
            setattr(user, key, value)

        session.add(user)
        session.commit()

        return '', HTTPStatus.NO_CONTENT

    except BadRequest as e:
        return e.description, e.code

    except IntegrityError as error:
        if isinstance(error.orig, UniqueViolation):
            return { "error_message": "Product already exists"}, HTTPStatus.CONFLICT
           
@jwt_required()
def delete_user():
    session = current_app.db.session
    user_on = get_jwt_identity()

    user:UserModel = UserModel.query.get(user_on["user_id"])
    if not user:
        raise NotFound

    session.delete(user)
    session.commit()

    return '', HTTPStatus.NO_CONTENT