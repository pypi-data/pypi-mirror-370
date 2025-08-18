import os, datetime, jwt
from ...imports import *
from functools import wraps
from abstract_flask import request, jsonify
from .token_utils import decode_token
from ..user_store.table_utils.routes import is_token_blacklisted, ensure_blacklist_table_exists
from ..user_store.get_users import get_user_by_username
ensure_blacklist_table_exists()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"message": "Missing Authorization header"}), 401

        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return jsonify({"message": "Invalid Authorization header format"}), 401

        token = parts[1]

        # 1) Check if token is blacklisted
        #if is_token_blacklisted(token):
        #    return jsonify({"message": "Token has been revoked"}), 401

        # 2) Decode and validate the token
        try:
            payload = decode_token(token)

        except Exception as e:
            logger.info(f"{e}")
        # 4) Determine user_id robustly
        user_id = None
        sub = payload.get("sub")
        if isinstance(sub, int) or (isinstance(sub, str) and sub.isdigit()):
            user_id = int(sub)
        else:
            # lookup by username
            user = get_user_by_username(username)
            if not user:
                return jsonify({"message": "Unknown user"}), 404
            user_id = user["id"]        except jwt.ExpiredSignatureError:
                    return jsonify({"message": "Token expired"}), 401
                except jwt.InvalidTokenError:
                    return jsonify({"message": "Invalid token"}), 401

                # 3) Extract username and admin flag
                username = payload.get("username")
                is_admin = payload.get("is_admin", False)



        # 5) Attach to request for downstream handlers
        request.user = {
            "id":       user_id,
            "username": username,
            "is_admin": is_admin
        }

        # 6) Call the wrapped view
        return f(*args, **kwargs)
    return decorated
