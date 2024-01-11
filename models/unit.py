from db import db


class UnitModel(db.Model):
    __tablename__ = "unit"

    id = db.Column(db.Integer, primary_key=True)
    rent_cost = db.Column(db.Float, nullable=False)
    unit_type = db.Column(db.String(10), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)