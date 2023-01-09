from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from models import UserModel
from schemas import UserSchema, UserUpdateSchema, UserLoginSchema, UserInfoSchema, UserPasswordChange, DeleteUser
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, create_refresh_token
from blocklist import BLOCKLIST


blp = Blueprint("users", __name__, description="Users details process.")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="A user with that email id already exists.")
        
        user = UserModel(    
                        first_name = user_data["first_name"],
                        surname = user_data["surname"],
                        username = user_data["username"],
                        email = user_data["email"],
                        password = pbkdf2_sha256.hash(user_data["password"])
                        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A user with that username already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the user.")
        
        return {"message": "User created successfully."}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_credentials):
        user = UserModel.query.filter(UserModel.username == user_credentials["username"]).first()
        if user and pbkdf2_sha256.verify(user_credentials["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        
        abort(401, message="Invalid credentials")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

@blp.route("/my-info")
class UserInfo(MethodView):
    @jwt_required()
    @blp.response(200, UserInfoSchema)
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id == user_id).first()
        return user

@blp.route("/change/password")
class ChangePassword(MethodView):
    @jwt_required()
    @blp.arguments(UserPasswordChange)
    def post(self, password_data):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if pbkdf2_sha256.verify(password_data["old_password"], user.password):
            user.password = pbkdf2_sha256.hash(password_data["new_password"])
        else:
            abort(400, message="Wrong Password")
        db.session.add(user)
        db.session.commit()
        return {"message": "Password Reset Successful."}, 200

@blp.route("/<string:username>/update")
class UserUpdate(MethodView):
    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserInfoSchema)
    def put(self, update_data, username):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        if update_data["first_name"]:
            user.first_name = update_data["first_name"]
        if update_data["surname"]:
            user.surname = update_data["surname"]
        if update_data["email"]:
            user.email = update_data["email"]
        
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/admin/users")
class UserList(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        return UserModel.query.all()
    
    @jwt_required()
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="A user with that email id already exists.")
        new_user = UserModel(    
                        first_name = user_data["first_name"],
                        surname = user_data["surname"],
                        username = user_data["username"],
                        email = user_data["email"],
                        password = pbkdf2_sha256.hash(user_data["password"])
                        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A user with that username already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the user.")
        
        return new_user

@blp.route("/admin/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    def delete(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User" + str(user_id) + "deleted."}

    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, first_name, username):
        user = UserModel.query.get_or_404(username)
        if user:
            user.first_name = first_name
        
        db.session.add(user)
        db.session.commit()

        return user

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200

@blp.route("/delete/account")
class DeleteUserAccount(MethodView):
    @jwt_required(fresh=True)
    @blp.arguments(DeleteUser)
    def delete(self, credentials):
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id);
        if user.username == credentials["username"] and pbkdf2_sha256.verify(credentials["password"], user.password):
            db.session.delete(user)
            db.session.commit()
            return {"message": "User Deleted."}, 200
        else:
            return {"message": "Invalid credentials"}, 401