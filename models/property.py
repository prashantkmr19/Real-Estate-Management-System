from db import db


class PropertyModel(db.Model):
    __tablename__ = "property"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    features = db.Column(db.Text, nullable=False)
    units = db.relationship('UnitModel', backref='property', lazy=True)
