from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from datetime import timedelta
from app.models.user import User
from app import jwt
from sqlalchemy.exc import SQLAlchemyError
from app.models.database import session_scope

login_bp = Blueprint('login', __name__)

@login_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        with session_scope() as session:
            user = session.query(User).filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                role = 'admin' if user.is_admin else 'user'
                access_token = create_access_token(
                    identity=user.id,
                    additional_claims={'role': role},
                    expires_delta=timedelta(hours=100)
                )
                return jsonify({
                    "message": "Login successful",
                    "access_token": access_token,
                    "role": role
                }), 200
            return jsonify({"message": "Invalid credentials"}), 401
    except SQLAlchemyError as e:
        # Log the error here
        return jsonify({"message": "An error occurred during login"}), 500
