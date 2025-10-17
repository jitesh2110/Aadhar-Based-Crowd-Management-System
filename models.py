from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class aadharinfo(db.Model):
    aadhar_number = db.Column(db.BigInteger,primary_key = True)
    name = db.Column(db.String(250))
    dob = db.Column(db.DateTime)
    gender = db.Column(db.String(20))
    address = db.Column(db.Text)
    phone_number = db.Column(db.BigInteger)
    fingerprint_data = db.Column(db.LargeBinary,nullable=True)
    face_embedding = db.Column(db.LargeBinary,nullable = True)

    logs = db.relationship("entrylogs",back_populates="card")


class entrylogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aadhar_number = db.Column(db.BigInteger,db.ForeignKey('aadharinfo.aadhar_number'), nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.now)
    entry_place = db.Column(db.Text)
    current_place = db.Column(db.Text)
    visited_places = db.Column(db.Text)
    status = db.Column(db.Text, default='active')

    card = db.relationship("aadharinfo", back_populates="logs")
