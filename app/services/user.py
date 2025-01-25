from flask import request
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from app.models.user import User
from werkzeug.security import generate_password_hash
from app.models.database import session_scope
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'company_id': fields.Integer,
    'is_admin': fields.Boolean
}

def check_existing_user(email):
    try:
        with session_scope() as session:
            user_exists = session.query(User).filter_by(email=email).first() is not None
            if user_exists:
                return True
    except SQLAlchemyError as e:
        # Log the error here
        print(e)
        return False
    return None

class UserResource(Resource):
    @marshal_with(user_fields)
    @marshal_with(user_fields)
    def get(self, user_id=None):
        try:
            with session_scope() as session:
                if user_id:
                    user = session.query(User).get(user_id)
                    if not user:
                        return {'message': 'User not found'}, 404
                    # Create a dictionary with user data
                    user_data = {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'company_id': user.company_id,
                        'is_admin': user.is_admin
                    }
                    return user_data
                else:
                    users = session.query(User).all()
                    # Create a list of dictionaries with user data
                    users_data = [{
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'company_id': user.company_id,
                        'is_admin': user.is_admin
                    } for user in users]
                    return users_data
        except SQLAlchemyError as e:
            # Log the error here
            return {'message': 'An error occurred while fetching user(s)'}, 500

    @marshal_with(user_fields)
    def post(self, user_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('company_id', type=int, required=True)
        parser.add_argument('is_admin', type=bool, default=False)
        args = parser.parse_args()

        with session_scope() as session:
            if check_existing_user(email=args['email']):
                return {'message': 'User with this email already exists'}, 400

            new_user = User(
                name=args['name'],
                email=args['email'],
                company_id=args['company_id'],
                is_admin=args['is_admin']
            )
            new_user.set_password(args['password'])

            session.add(new_user)
            session.flush()  # This will assign an ID to new_user if it's using auto-increment

            # Create a dictionary representation of the user
            result = {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'company_id': new_user.company_id,
                'is_admin': new_user.is_admin
            }

        return result, 201

    @marshal_with(user_fields)
    def patch(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('company_id', type=int)
        parser.add_argument('is_admin', type=bool)
        args = parser.parse_args()

        try:
            with session_scope() as session:
                user = session.query(User).get(user_id)
                if not user:
                    return {'message': 'User not found'}, 404

                for key, value in args.items():
                    if value is not None:
                        if key == 'password':
                            setattr(user, 'password_hash', generate_password_hash(value))
                        else:
                            setattr(user, key, value)

                session.flush()
                return user
        except SQLAlchemyError as e:
            # Log the error here
            return {'message': 'An error occurred while updating the user'}, 500

    def delete(self, user_id):
        try:
            with session_scope() as session:
                user = session.query(User).get(user_id)
                if not user:
                    return {'message': 'User not found'}, 404

                session.delete(user)
                return {'message': 'User deleted successfully'}, 200
        except SQLAlchemyError as e:
            # Log the error here
            return {'message': 'An error occurred while deleting the user'}, 500

