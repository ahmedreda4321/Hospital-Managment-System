# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, FormField, HiddenField, StringField, PasswordField, SelectField, SubmitField, FileField,DateTimeField,validators,SelectMultipleField
from wtforms.validators import Email, DataRequired, Length, Regexp
from flask_wtf.file import FileAllowed
import pandas as pd
from datetime import datetime, timedelta

# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                           id='username_login',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])

    first_name = StringField('First Name',
                             id='first_name',
                             validators=[DataRequired(), Length(min=3, max=64)])

    last_name = StringField('Last Name',
                            id='last_name',
                            validators=[DataRequired(), Length(min=3, max=64)])

    mobile_number = StringField('Mobile Number',
                                id='mobile_number',
                                validators=[DataRequired(), Length(min=11, max=11), Regexp(r'^01\d*$')])

    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])

    choices = [('1', 'Patient'), ('2', 'Doctor'), ('3', 'Administrative')]

    profile_pic = FileField('Profile Pic', id='pic_file', validators=[
                            FileAllowed(['jpg', 'png'])])

    role = SelectField('Role',
                       id='role_id', choices=choices,
                       validators=[DataRequired()])
    submit = SubmitField('Create Account')


class DoctorForm(FlaskForm):
    choices = [
        'Dermatologist',
        'Allergist',
        'Gastroenterologist',
        'Hepatologist',
        'Osteopathic',
        'Endocrinologist',
        'Pulmonologist',
        'Cardiologist',
        'Neurologist',
        'Internal Medcine',
        'Pediatrician',
        'Common Cold',
        'Cardiologist',
        'Phlebologist',
        'Osteoarthristis',
        'Rheumatologists',
        'Otolaryngologist',
        'Gynecologist',
    ]
    specialization = SelectField('Specialty',
                                 id='speciality_id', choices=choices,
                                 validators=[DataRequired()])


class UpdateDoctor(FlaskForm):
    id = HiddenField('user_id')
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])

    first_name = StringField('First Name',
                             id='first_name',
                             validators=[DataRequired(), Length(min=3, max=64)])

    last_name = StringField('Last Name',
                            id='last_name',
                            validators=[DataRequired(), Length(min=3, max=64)])

    mobile_number = StringField('Mobile Number',
                                id='mobile_number',
                                validators=[DataRequired(), Length(min=11, max=11), Regexp(r'^01\d*$')])

    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                             id='pwd_create')

    profile_pic = FileField('Profile Pic', id='pic_file', validators=[FileAllowed(['png', 'pdf', 'jpg'], "wrong format!")])

    specialization = FormField(DoctorForm, 'specialization')
    submit = SubmitField('Update Account')


class UpdatePatient(FlaskForm):
    id = HiddenField('user_id')
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])

    first_name = StringField('First Name',
                             id='first_name',
                             validators=[DataRequired(), Length(min=3, max=64)])

    last_name = StringField('Last Name',
                            id='last_name',
                            validators=[DataRequired(), Length(min=3, max=64)])

    mobile_number = StringField('Mobile Number',
                                id='mobile_number',
                                validators=[DataRequired(), Length(min=11, max=11), Regexp(r'^01\d*$')])

    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                             id='pwd_create')

    profile_pic = FileField('Profile Pic', id='pic_file', validators=[FileAllowed(['png', 'pdf', 'jpg'], "wrong format!")])

    submit = SubmitField('Update Account')


class AddDoctor(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])

    first_name = StringField('First Name',
                             id='first_name',
                             validators=[DataRequired(), Length(min=3, max=64)])

    last_name = StringField('Last Name',
                            id='last_name',
                            validators=[DataRequired(), Length(min=3, max=64)])

    mobile_number = StringField('Mobile Number',
                                id='mobile_number',
                                validators=[DataRequired(), Length(min=11, max=11), Regexp(r'^01\d*$')])

    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                             id='pwd_create',validators=[DataRequired()])

    profile_pic = FileField('Profile Pic', id='pic_file', validators=[FileAllowed(['png', 'pdf', 'jpg'], "wrong format!")])

    specialization = FormField(DoctorForm, 'specialization')
    submit = SubmitField('Update Account')

class ManageAppoinmentsForm(FlaskForm):
    form_id=HiddenField('hiddenfield')
    doctor_id=SelectField('Doctor',validators=[DataRequired()])
    patient_id=SelectField('Patient',validators=[DataRequired()])
    date_time = DateTimeField('Date and Time', format=r'%Y-%m-%dT%H:%M', validators=[validators.Optional()])
    is_approved=SelectField('Approval',choices=[(0,'Declined'),(1,'Approved')],validators=[DataRequired()])
    submit=SubmitField('Submit')
    def validate_date_time(form, field):
        # Custom validation function to handle the input format
        if field.data is not None:
            try:
                print(field.data)
                field.data=field.data.strftime("%Y-%m-%d %H:%M:%S")
                # Attempt to parse the input string
                field.data = (datetime.strptime(field.data, r"%Y-%m-%dT%H:%M")).strftime(r"%Y-%m-%d %H:%M:%S")
                print(field.data)
            except ValueError:
                # If parsing fails, try with the other format
                try:
                    field.data = (datetime.strptime(field.data, r"%Y-%m-%d %H:%M:%S")).strftime(r"%Y-%m-%d %H:%M:%S")
                    print(field.data)
                except ValueError:
                    # If both parsing attempts fail, raise a validation error
                    raise validators.ValidationError('Invalid date and time format')

class AddAppoinmentsForm(FlaskForm):
    doctor_id=SelectField('Doctor',validators=[DataRequired()])
    patient_id=SelectField('Patient',validators=[DataRequired()])
    date_time = DateTimeField('Date and Time', format=r'%Y-%m-%dT%H:%M', validators=[validators.DataRequired()])
    submit=SubmitField('Submit')
class AddPatient(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])

    first_name = StringField('First Name',
                             id='first_name',
                             validators=[DataRequired(), Length(min=3, max=64)])

    last_name = StringField('Last Name',
                            id='last_name',
                            validators=[DataRequired(), Length(min=3, max=64)])

    mobile_number = StringField('Mobile Number',
                                id='mobile_number',
                                validators=[DataRequired(), Length(min=11, max=11), Regexp(r'^01\d*$')])

    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                             id='pwd_create',validators=[DataRequired()])

    profile_pic = FileField('Profile Pic', id='pic_file', validators=[FileAllowed(['png', 'pdf', 'jpg'], "wrong format!")])

    submit = SubmitField('Update Account')


class SymptomsFillForm(FlaskForm):
    data=pd.read_csv('predict.csv',index_col=0)
    choices=[(index,str(value).replace('_',' ')) for index, value in enumerate(data.columns)]
    symptoms=SelectMultipleField('Choose Your symptoms' ,choices=choices)

class AddAppoinmentFromPatient(FlaskForm):
    doctor_id=SelectField('Doctor',validators=[DataRequired()])
    date_time = DateTimeField('Date and Time', format=r'%Y-%m-%dT%H:%M', validators=[validators.DataRequired()])
    submit=SubmitField('Submit')

    def validate_date_time(form, field):
        # Custom validation function to handle the input format
        if field.data is not None:
            now = datetime.utcnow()  # Current UTC datetime
            one_day_in_future = now + timedelta(hours=12)
            
            if field.data <= one_day_in_future:
                raise validators.ValidationError('Date and time must be at least 12 hours in the future')