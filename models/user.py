from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db


class UserModel(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
