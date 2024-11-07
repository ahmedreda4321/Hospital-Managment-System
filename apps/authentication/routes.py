# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from flask import render_template, redirect, request, url_for,flash
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm,DoctorForm
from apps.authentication.models import Users,Doctor
from uuid import uuid4
from apps.authentication.util import verify_pass
from werkzeug.utils import secure_filename


# @blueprint.route('/')
# def route_default():
#     return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            if user.active or True:
                login_user(user)
                next_url =  request.args.get('next')
                if next_url:
                    return redirect(location=next_url)
                return redirect(url_for('home_blueprint.index'))
            else:
                flash('Please Wait for Account Approval','danger')
                return redirect(url_for('home_blueprint.index'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong Username or Password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    doctor_form=DoctorForm(request.form)
    if request.method == 'POST' and create_account_form.validate():
        print('registering')
        username = request.form['username']
        email = request.form['email']
        role=request.form['role']
        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form,doctor_form=doctor_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form,doctor_form=doctor_form)
       
        

        pic = request.files.get('profile_pic')
        if pic:
            print('found pic')
            print(pic.name)
            # Check if the file has a name and is allowed
            if pic.filename != '' and '.' in pic.filename and pic.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                # Securely generate a new name for the file
                new_name = str(uuid4()) + secure_filename(pic.filename)
                mutable_dict = request.form.to_dict()
                pic.save('apps/static/profile_pics/'+new_name)
                # Now you can modify the dictionary
                mutable_dict['profile_pic'] = new_name
                print('correct extention and adding to database')
                # Create the Users instance with the updated data
                user = Users(**mutable_dict)
                

            else:
                print('found bad extenstion')
                return render_template('accounts/register.html',
                                   msg='Wrong Image Extension',
                                   success=False,
                                   form=create_account_form)
        else:
            print('didnt find pic')
            user = Users(**request.form)
        db.session.add(user)
        db.session.commit()
        if role=='2':
            doc=Doctor(user_id=user.id,specialization=request.form['specialization'])
            db.session.add(doc)
            db.session.commit()
        # Delete user from session
        logout_user()
        flash('Account Created Successfully please wait for Approval','success')
        return redirect(url_for('home_blueprint.index'))

    else:
        return render_template('accounts/register.html', form=create_account_form,doctor_form=doctor_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('authentication_blueprint.login',next=request.url))


@blueprint.errorhandler(403)
def access_forbidden(error):
     return redirect(url_for('home_blueprint.index'))


@blueprint.errorhandler(404)
def not_found_error(error):
     return redirect(url_for('home_blueprint.index'))


@blueprint.errorhandler(500)
def internal_error(error):
     return redirect(url_for('home_blueprint.index'))
