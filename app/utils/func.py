"""
Functions.
"""
import os
import datetime
from flask import make_response
import jwt
from app.models.user import User


def create_token_response(payload):
    """
    Add tokens to cookies.
    """
    tokens = _create_tokens(payload)
    response = make_response({"message": "login_successful"}, 200)
    response.set_cookie("access_token", tokens["access_token"])
    response.set_cookie("refresh_token", tokens["refresh_token"])
    return response


def renew_tokens(response, decoded_refresh_token):
    """
    Renew tokens in response cookies.
    """
    token_username = decoded_refresh_token.get("username")
    user = User.query.filter_by(username=token_username).first()
    if not user:
        return response

    payload = extract_token_payload(user)
    tokens = _create_tokens(payload)
    response.set_cookie("access_token", tokens["access_token"])
    response.set_cookie("refresh_token", tokens["refresh_token"])
    return response


def extract_token_payload(user):
    """
    Extract token payload from user.
    """
    return {
        "id": user.id,
        "username": user.username
    }


def _create_tokens(payload):
    """
    Create access and refresh tokens.
    """
    token_key = os.getenv("TOKEN_SECRET", "")

    access_token = jwt.encode(
        payload={
            **payload,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5
                                                                   )
        }, key=token_key, algorithm="HS256",)
    refresh_token = jwt.encode(
        payload={
            **payload,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1
                                                                   )
        }, key=token_key, algorithm="HS256",)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def decode_token(token):
    """
    Decode token.
    """
    if token == "" or None:
        return None

    token_key = os.getenv("TOKEN_SECRET", "Verisekret")
    try:
        decoded_token = jwt.decode(
            token, key=token_key, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
    except jwt.InvalidTokenError:
        print("Invalid token.")

    return None


def _check_user_refresh_token(decoded_refresh_token):
    """
    Check user if access token has expired.

    For lacking of middleware, just check and do the renewing in after_request.
    """
    if not decoded_refresh_token:
        return False

    token_username = decoded_refresh_token.get("username")
    user = User.query.filter_by(username=token_username).first()
    other_checks = True
    if user and other_checks:
        # check user exists and is not banned etc
        return True

    return False


def has_logged_in(received_request, is_admin=False):
    """
    A simple way to check if user has logged in and return the decoded token.
    """

    access_token = received_request.cookies.get("access_token", None)
    if not access_token:
        return None

    decoded_access_token = decode_token(access_token)

    if decoded_access_token:
        return decoded_access_token

    refresh_token = received_request.cookies.get("access_token", None)
    if not refresh_token:
        return None

    decoded_refresh = decode_token(refresh_token)
    user_ok = _check_user_refresh_token(decoded_refresh)

    if user_ok:
        return decoded_refresh

    return None
