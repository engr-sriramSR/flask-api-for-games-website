from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    surname = fields.Str()
    username = fields.Str(required=True)
    email = fields.Email(required=True, unique=True)
    password = fields.Str(required=True, load_only=True)

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class UserUpdateSchema(Schema):
    first_name = fields.Str()
    surname = fields.Str()
    email = fields.Str()

class UserInfoSchema(Schema):
    first_name = fields.Str()
    surname = fields.Str()
    email = fields.Str()

class UserPasswordChange(Schema):
    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, load_only=True)

class DeleteUser(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)