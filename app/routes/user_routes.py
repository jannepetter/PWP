"""
User routes.
"""

import bcrypt
from flask import request, Blueprint
from app.models.user import User,  UserRequestSerialiser, UserResponseSerialiser
from app import db
from app.utils.func import create_token_response, extract_token_payload
users_blueprint = Blueprint("users_blueprint", __name__)


@users_blueprint.route("/users", methods=["GET"])
def get_users():
    """
    Users router.
    """
    users_query = User.query.all()
    return UserResponseSerialiser().dump(obj=users_query, many=True),   200


@users_blueprint.route("/users", methods=["POST"])
def post_users():
    """
    Users router.
    """
    data = request.json
    try:
        password = data["password"]
        username = data["username"]
    except KeyError:
        return {"message": "username and password are required"}, 400

    hashed_password = bcrypt.hashpw(password.encode(
        "utf-8"), bcrypt.gensalt()).decode("utf-8")

    new_user = UserRequestSerialiser().load(data={
        "username": username,
        "password": hashed_password
    })
    db.session.add(new_user)
    db.session.commit()
    return UserResponseSerialiser().dump(new_user),   201


@users_blueprint.route("/login", methods=["POST"])
def login():
    """
    Login
    """
    data = request.json
    try:
        username = data["username"]
        password = data["password"]
    except KeyError:
        return {"message": "username and password are required"}, 400

    user = User.query.filter_by(username=username).first()
    if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        payload = extract_token_payload(user)
        return create_token_response(payload)

    return {"message": "wrong username or password"}, 400
