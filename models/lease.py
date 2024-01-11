from db import db


class LeaseModel(db.Model):
    __tablename__ = "lease"

    id = db.Column(db.Integer, primary_key=True)
    agreement_end_date = db.Column(db.Date, nullable=False)
    monthly_rent_date = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)