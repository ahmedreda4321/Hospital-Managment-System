# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass
from datetime import datetime


class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    profile_pic = db.Column(db.String(64), default='admin.png')
    password = db.Column(db.LargeBinary)
    active = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(32))
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    mobile_number = db.Column(db.String(11), nullable=False)
    def set_specialization(self,specialization):
        if self.doctor:
            self.doctor.specialization=specialization
            db.session.commit()
        
    @property
    def get_specialization(self):
        if self.doctor:
            return self.doctor.specialization
        return None

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'Users.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(255), nullable=False)
    # Add other doctor-specific fields here

    user = db.relationship(
        'Users', backref=db.backref('doctor', uselist=False))


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'Users.id'), unique=True, nullable=False)
    # Add other patient-specific fields here
    user = db.relationship(
        'Users', backref=db.backref('patient', uselist=False))
    symptoms = db.relationship(
        'Symptom', secondary='patient_symptom_association', backref='patients', lazy='dynamic')


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey(
        'Users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey(
        'Users.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    # Add other appointment-specific fields here
    doctor = db.relationship("Users", foreign_keys=[
                             doctor_id], backref="appoinment_as_doctor")
    patient = db.relationship("Users", foreign_keys=[
                              patient_id], backref="appoinment_as_patient")


patient_symptom_association = db.Table(
    'patient_symptom_association',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id')),
    db.Column('symptom_id', db.Integer, db.ForeignKey('symptom.id'))
)


class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
