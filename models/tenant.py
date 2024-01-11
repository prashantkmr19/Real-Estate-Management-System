from db import db


class TenantModel(db.Model):
    __tablename__ = "tenant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    document_proofs = db.Column(db.Text, nullable=False)
    leases = db.relationship('LeaseModel', backref='tenant', lazy=True)