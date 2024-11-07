# -*- encoding: utf-8 -*-

from apps.home import blueprint
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound
from apps.authentication.models import Users, Appointment, Doctor
from apps.authentication.forms import AddAppoinmentFromPatient, AddAppoinmentsForm, AddDoctor, AddPatient, ManageAppoinmentsForm, SymptomsFillForm, UpdateDoctor, DoctorForm, UpdatePatient
from apps import db
from apps.authentication.util import hash_pass
from werkzeug.utils import secure_filename
from uuid import uuid4
from datetime import datetime
import numpy as np
import pickle
import pandas as pd


@blueprint.route('/')
def index():
    return render_template('home/index.html')


@blueprint.route('/aboutus')
def aboutus():
    return render_template('home/aboutus.html')


@blueprint.route('/doctorclick')
def doctorclick():
    return render_template('doctor/doctorclick.html')


@blueprint.route('/adminclick')
def adminclick():
    return render_template('admin/adminclick.html')


@blueprint.route('/patientclick')
def patientclick():
    return render_template('patient/patientclick.html')


@blueprint.route('/adminlogin')
def adminlogin():
    return render_template('admin/adminlogin.html')


@blueprint.route('/admin_main')
@login_required
def admin_main():
    all_doctors = Users.query.filter_by(role='2').all()
    total_doctors = len(all_doctors)
    doctors_not_approved = Users.query.filter_by(
        role='2').filter_by(active=False).all()
    num_doctors_not_approved = len(doctors_not_approved)
    total_patients = len(Users.query.filter_by(role='1').all())
    num_patients_unapproved = len(Users.query.filter_by(
        role='1').filter_by(active=False).all())
    total_appointments = len(Appointment.query.all())
    num_appointments_unapproved = len(
        Appointment.query.filter_by(is_approved=False).all())
    last_doctors = Users.query.filter_by(role='2').order_by(
        Users.id.desc()).limit(3).all()  #
    specialization = []
    for doc in last_doctors:
        specialization.append(doc.doctor.specialization)
    last_patients = Users.query.filter_by(role='1').order_by(
        Users.id.desc()).limit(3).all()  #
    last_appointments = Appointment.query.order_by(
        Appointment.id.desc()).limit(5).all()  # .limit(3)

    return render_template('dash/includes/admin/admin_dash_main.html', num_doctors_not_approved=num_doctors_not_approved,
                           total_doctors=total_doctors,
                           total_patients=total_patients,
                           num_patients_unapproved=num_patients_unapproved,
                           total_appointments=total_appointments,
                           num_appointments_unapproved=num_appointments_unapproved,
                           last_doctors=last_doctors,
                           specialization=specialization,
                           last_patients=last_patients,
                           last_appointments=last_appointments
                           )


@blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('dash/dash_base.html')


@blueprint.route('/manage_doctor')
@login_required
def manage_doctor():
    all_doctors = Users.query.filter_by(role='2').all()
    specialization = []
    for doc in all_doctors:
        specialization.append(doc.doctor.specialization)
    return render_template('dash/includes/admin/admin_dash_manage_doctor.html', all_doctors=all_doctors, specialization=specialization)


@blueprint.route('/manage_patient')
@login_required
def manage_patient():
    all_doctors = Users.query.filter_by(role='1').all()

    return render_template('dash/includes/admin/admin_dash_manage_patient.html', all_patients=all_doctors)


@blueprint.route('/manage_appointments')
@login_required
def manage_appointments():
    all_appointments = Appointment.query.order_by(Appointment.date_time.desc()).all()

    return render_template('dash/includes/admin/admin_dash_manage_appointment.html', all_appointments=all_appointments)


@blueprint.route('/toggle_user', methods=['POST'])
@login_required
def toggle_user():
    user_id = request.form.get('userid')
    user_to_toggle = Users.query.filter_by(id=user_id).first()
    if (user_to_toggle.active):
        user_to_toggle.active = False
        db.session.commit()
    else:
        user_to_toggle.active = True
        db.session.commit()

    return jsonify({'approve': user_to_toggle.active})


@blueprint.route('/toggle_appointment', methods=['POST'])
@login_required
def toggle_appointment():
    appointment_id = request.form.get('userid')
    appointment_to_toggle = Appointment.query.filter_by(
        id=appointment_id).first()
    if (appointment_to_toggle.is_approved):
        appointment_to_toggle.is_approved = False
        db.session.commit()
    else:
        appointment_to_toggle.is_approved = True
        db.session.commit()

    return jsonify({'approve': appointment_to_toggle.is_approved})


@blueprint.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    try:
        user_id = request.form.get('userid')
        Users.query.filter_by(id=user_id).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'exception': str(e)})

@blueprint.route('/delete_appointment', methods=['POST'])
@login_required
def delete_appointment():
    try:
        appointment = request.form.get('appointmentid')
        Appointment.query.filter_by(id=appointment).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False})

@blueprint.route('/update_doctor', methods=['GET', 'POST'])
@login_required
def update_doctor():
    user_id = request.args.get('userid')

    if user_id is not None and str(user_id).isdigit():
        user_id = int(user_id)
        form = UpdateDoctor(id=user_id)
        user = Users.query.filter_by(id=user_id).first()
        for field in form:
            if hasattr(user, field.name):
                field.data = getattr(user, field.name)
        form.specialization.specialization.data = user.get_specialization
        return render_template('dash/includes/admin/admin_dash_edit_doctor.html', doctor_form=form)
    else:
        form = UpdateDoctor(request.form)
        if form.validate_on_submit():
            user = Users.query.filter_by(id=int(form.id.data)).first()
            for field in form:
                if field.name == 'id':
                    continue
                if field.name == 'password':
                    if field.data == '':
                        continue
                    hashed_password = hash_pass(field.data)
                    if hasattr(user, field.name):
                        setattr(user, field.name, hashed_password)
                        db.session.commit()
                        continue
                if hasattr(user, field.name):
                    setattr(user, field.name, field.data)
                    db.session.commit()
            pic = request.files.get('profile_pic')
            if pic:
                # Check if the file has a name and is allowed
                if pic.filename != '' and '.' in pic.filename and pic.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                    # Securely generate a new name for the file
                    new_name = str(uuid4()) + secure_filename(pic.filename)
                    pic.save('apps/static/profile_pics/'+new_name)
                    user.profile_pic = new_name
            return redirect(url_for('home_blueprint.manage_doctor'))
        else:
            return redirect(url_for('home_blueprint.manage_doctor'))


@blueprint.route('/update_patient', methods=['GET', 'POST'])
@login_required
def update_patient():
    user_id = request.args.get('userid')

    if user_id is not None and str(user_id).isdigit():
        user_id = int(user_id)
        form = UpdatePatient(id=user_id)
        user = Users.query.filter_by(id=user_id).first()
        for field in form:
            if hasattr(user, field.name):
                field.data = getattr(user, field.name)
        return render_template('dash/includes/admin/admin_dash_edit_patient.html', patient_form=form)
    else:
        form = UpdatePatient(request.form)
        if form.validate_on_submit():
            user = Users.query.filter_by(id=int(form.id.data)).first()
            for field in form:
                if field.name == 'id':
                    continue
                if field.name == 'password':
                    if field.data == '':
                        continue
                    hashed_password = hash_pass(field.data)
                    if hasattr(user, field.name):
                        setattr(user, field.name, hashed_password)
                        db.session.commit()
                        continue
                if hasattr(user, field.name):
                    setattr(user, field.name, field.data)
                    db.session.commit()
            pic = request.files.get('profile_pic')
            if pic:
                # Check if the file has a name and is allowed
                if pic.filename != '' and '.' in pic.filename and pic.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                    # Securely generate a new name for the file
                    new_name = str(uuid4()) + secure_filename(pic.filename)
                    pic.save('apps/static/profile_pics/'+new_name)
                    user.profile_pic = new_name
            form_specialization_data = form.specialization.specialization.data
            user.set_specialization(form_specialization_data)
            return redirect(url_for('home_blueprint.manage_patient'))
        else:
            return redirect(url_for('home_blueprint.manage_patient'))


@blueprint.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():

    form = AddDoctor(request.form)
    if form.validate_on_submit():
        user = Users()
        for field in form:
            if field.name == 'password':
                if not str(field.data).strip():
                    return render_template('dash/includes/admin/admin_dash_add_doctor.html', doctor_form=form)
                hashed_password = hash_pass(field.data)
                if hasattr(user, field.name):
                    setattr(user, field.name, hashed_password)
                    continue
            if hasattr(user, field.name):
                setattr(user, field.name, field.data)
        pic = request.files.get('profile_pic')
        if pic:
            # Check if the file has a name and is allowed
            if pic.filename != '' and '.' in pic.filename and pic.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                # Securely generate a new name for the file
                new_name = str(uuid4()) + secure_filename(pic.filename)
                pic.save('apps/static/profile_pics/'+new_name)
                user.profile_pic = new_name
        user.role = 2
        form_specialization_data = form.specialization.specialization.data
        db.session.add(user)
        db.session.commit()
        new_doctor = Doctor(
            user_id=user.id, specialization=form_specialization_data)
        db.session.add(new_doctor)
        db.session.commit()
        return redirect(url_for('home_blueprint.manage_doctor'))

    return render_template('dash/includes/admin/admin_dash_add_doctor.html', doctor_form=form)


@blueprint.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():

    form = AddPatient(request.form)
    if form.validate_on_submit():
        user = Users()
        for field in form:
            if field.name == 'password':
                if not str(field.data).strip():
                    return render_template('dash/includes/admin/admin_dash_add_patient.html', patient_form=form)
                hashed_password = hash_pass(field.data)
                if hasattr(user, field.name):
                    setattr(user, field.name, hashed_password)
                    continue
            if hasattr(user, field.name):
                setattr(user, field.name, field.data)
        pic = request.files.get('profile_pic')
        if pic:
            # Check if the file has a name and is allowed
            if pic.filename != '' and '.' in pic.filename and pic.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
                # Securely generate a new name for the file
                new_name = str(uuid4()) + secure_filename(pic.filename)
                pic.save('apps/static/profile_pics/'+new_name)
                user.profile_pic = new_name
        user.role = 1
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('home_blueprint.manage_patient'))

    return render_template('dash/includes/admin/admin_dash_add_patient.html', patient_form=form)


@blueprint.route('/update_appointment', methods=['GET', 'POST'])
@login_required
def update_appointment():
    appointment_id = request.args.get('apt_id')
    appoint_form = ManageAppoinmentsForm(request.form)
    appoint_form.patient_id.choices = [(patient.id, patient.first_name + ' ' + patient.last_name)
                                        for patient in Users.query.filter_by(role='1').all()]
    appoint_form.doctor_id.choices = [(doctor.id, doctor.first_name + ' ' + doctor.last_name)
                                          for doctor in Users.query.filter_by(role='2').all()]
    if appointment_id is not None:
       
        appointment_id = int(appointment_id)
        appointment_to_edit = Appointment.query.get_or_404(appointment_id)
        appoint_form.form_id.data=appointment_id
        appoint_form.patient_id.default = str(appointment_to_edit.patient.id)
        appoint_form.doctor_id.default = appointment_to_edit.doctor.id
        appoint_form.date_time.default=appointment_to_edit.date_time
        appoint_form.is_approved.default= int(appointment_to_edit.is_approved)
        appoint_form.process(form_id=appointment_id)
    if appoint_form.validate_on_submit():
        appointment_to_edit = Appointment.query.get_or_404(int(appoint_form.data.get('form_id')))
        appointment_to_edit.patient_id=int(appoint_form.patient_id.data)
        appointment_to_edit.doctor_id=int(appoint_form.doctor_id.data)
        appointment_to_edit.is_approved=bool(appoint_form.is_approved.data)
        format_str = r'%Y-%m-%d %H:%M:%S'
        date_time_obj = datetime.strptime(appoint_form.date_time.data, format_str)
        appointment_to_edit.date_time=date_time_obj

        db.session.commit()
        return redirect(url_for('home_blueprint.manage_appointments'))
    return render_template('dash/includes/admin/admin_dash_edit_appointment.html', appoint_form=appoint_form)



@blueprint.route('/add_appointment', methods=['GET', 'POST'])
@login_required
def add_appointment():
    form=AddAppoinmentsForm(request.form)
    form.patient_id.choices = [(patient.id, patient.first_name + ' ' + patient.last_name)
                                        for patient in Users.query.filter_by(role='1').all()]
    form.doctor_id.choices = [(doctor.id, doctor.first_name + ' ' + doctor.last_name)
                                          for doctor in Users.query.filter_by(role='2').all()]
    
    if form.validate_on_submit():
        new_appointment=Appointment()
        form.populate_obj(new_appointment)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('home_blueprint.manage_appointments'))

    return render_template('dash/includes/admin/admin_dash_add_appointment.html',appoint_form=form)


@blueprint.route('/dr_view_appointments', methods=['GET', 'POST'])
@login_required
def dr_view_appointments():
    current_datetime= datetime.now()
    current_datetime_str = current_datetime.strftime(r'%Y-%m-%d %H:%M:%S')
    new_appointments=Appointment.query.filter_by(doctor_id=current_user.id).filter(Appointment.date_time>=current_datetime_str).order_by(Appointment.date_time.desc()).all()
    old_appointments=Appointment.query.filter_by(doctor_id=current_user.id).filter(Appointment.date_time<current_datetime_str).order_by(Appointment.date_time.desc()).all()
    print(new_appointments)
    
    return render_template('/dash/includes/doctor/doctor_dash_view_appointment.html',new_appointments=new_appointments,old_appointments=old_appointments)

@blueprint.route('/pt_view_appointments', methods=['GET', 'POST'])
@login_required
def pt_view_appointments():
    current_datetime= datetime.now()
    current_datetime_str = current_datetime.strftime(r'%Y-%m-%d %H:%M:%S')
    new_appointments=Appointment.query.filter_by(patient_id=current_user.id).filter(Appointment.date_time>=current_datetime_str).order_by(Appointment.date_time.desc()).all()
    old_appointments=Appointment.query.filter_by(patient_id=current_user.id).filter(Appointment.date_time<current_datetime_str).order_by(Appointment.date_time.desc()).all()
    print(new_appointments)
    
    return render_template('/dash/includes/doctor/doctor_dash_view_appointment.html',new_appointments=new_appointments,old_appointments=old_appointments)


@blueprint.route('/appointments', methods=['GET', 'POST'])
@login_required
def make_apt():
    form=SymptomsFillForm(request.form)
    choosespecialization=DoctorForm(request.form)
    appointform=AddAppoinmentFromPatient(request.form)
    doctors=Doctor.query.filter_by(specialization='Dermatologist').all()
    choices=[(doctor.user.id,doctor.user.first_name+' '+doctor.user.last_name) for doctor in doctors ]
    appointform.doctor_id.choices=choices
    if appointform.validate_on_submit():
        print('sucess')
        new_apt=Appointment(patient_id=current_user.id,doctor_id=int(appointform.doctor_id.data),date_time=appointform.date_time.data)
        db.session.add(new_apt)
        db.session.commit()
        flash(f'Appointment Created at {appointform.date_time.data} successfully!')
        return redirect(url_for('home_blueprint.index'))
    return render_template('patient/makeappointment.html',form=form,choosespecialization=choosespecialization,appointform=appointform)

@blueprint.route('/get_doctors_by_spec')
def get_doctors_by_spec():
    spec=request.args.get('spec')
    print(request.args)
    doctors=Doctor.query.filter_by(specialization=spec).all()
    choices=[{'value':doctor.user.id,'text':doctor.user.first_name+' '+doctor.user.last_name} for doctor in doctors ]
    import json
    print(json.dumps(choices))
    print(jsonify(choices))
    return json.dumps(choices),200

@blueprint.route('/predict_patient', methods=['POST'])
def predict_patient():
    df=pd.read_csv('predict.csv')
    data=np.zeros(131)
    for col in request.form.getlist('selectedValues[]'):
        data[int(col)]=1
    # data=data.reshape(1,-1)
    # data=[0,0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    model_filepath = 'ModelCreation/Specalist.pkl'
    df.loc[len(df)]=data
    with open(model_filepath, 'rb') as file:
        loaded_model = pickle.load(file)
    result = loaded_model.predict(df)
    result_prob=loaded_model.predict_proba(df)
    print(result_prob)
    print(np.max(result_prob))
    print(np.max(result_prob[0]))
    if np.max(result_prob)>0.5:
        return jsonify({'result':str(result[0])})
    else:
        return jsonify({})