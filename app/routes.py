# coding: utf-8
import math
from os.path import splitext, expanduser
from random import randint
#from tkinter import *
#from tkinter import filedialog
import flask_excel as excel
import pdfkit

import psycopg2
from psycopg2 import sql


from flask import render_template, redirect, url_for, session, send_from_directory, make_response
from flask.json import jsonify
from flask_login import current_user, login_user, logout_user, login_required
from pandas.errors import ParserError
from sqlalchemy import create_engine
from sqlalchemy.sql import exists
from sqlalchemy.exc import IntegrityError
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

# Import `load_workbook` module from `openpyxl`
from app.forms import *  # LoginForm, AddUserForm, ModeOfDonation
from app.models import *  # User, DonationMode
from app.reports import *


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)
    session.modified = True
    # g.user = current_user


@app.route('/')
@app.route('/index')
@login_required
def index():
    #    file_path = app.config['LICENSE_COUNT']
    # license_details = ValidApp.query.first()
    # today_time = time.time()
    # trial_period = 90
    # form = LicenseForm()
    # ctr = FormControl()
    # day_remaining = 90
    # if_run_once = False
    #
    # license_details = ValidApp.query.first()
    # today_time = time.time()
    # trial_period = 90
    # form = LicenseForm()
    # ctr = FormControl()
    # day_remaining = 90
    # if_run_once = False
    # # license_status = validateLicense()
    # license_status = 1
    #
    # # with open(file_path, 'r') as lrf:
    # #     elapsed = lrf.readline().split(",")
    #
    # if license_status == 0:  # 0 - Invalid License
    #     flash("Invalid License")
    #     return render_template('license.html', form=form, ctr=ctr)
    #
    # if license_status == 10:  # 0 - License files has been tampered
    #     flash("Some files missing")
    #     print("Could not find one or more critical files ")
    #     return render_template('license.html', form=form, ctr=ctr)
    # else:
    #     if license_status != 1: # if license has not been activated, read the license counter file
    #         file_path = app.config['LICENSE_COUNT']
    #         with open(file_path, 'r') as lrf:
    #             elapsed = lrf.readline().split(",")
    #
    # if license_status == 3 or license_status == 4:  # the license count file has been tampered
    #
    #     with open(file_path, 'r') as lrf:
    #         elapsed = lrf.readline().split(",")
    #
    #         if elapsed[0] == '': # the license count file has been tampered
    #             with open(app.config['LICENSE_BACKUP_FILE'], 'r') as rf:
    #                 backup = rf.readline().split("-")
    #                 file_time = backup[1]
    #                 today_time = time.time()
    #                 seconds_elapsed = today_time - float(file_time)
    #                 days, rest = divmod(seconds_elapsed, 86400)
    #                 encoded_time = base64.b64encode(bytes(backup[1], 'utf-8'))
    #                 hashed_app_license = backup[0]
    #
    #             with open(app.config['LICENSE_COUNT'], 'w') as wf: # restored from the backup file(bkclds.data)
    #                 count_and_time = str(int(days)) + "," + str(file_time)
    #                 wf.write(count_and_time)
    #
    #                 lic = ValidApp.query.first()
    #
    #                 ## -- We need only one license, if there one update it else create one
    #                 if lic is not None:
    #                     row = ValidApp.query.get(lic.id)
    #                     row.duration = base64.b64encode(bytes(backup[1], 'utf-8'))
    #                     row.app_license = hashed_app_license
    #                     db.session.commit()
    #                 else:
    #                     save_license = ValidApp(duration=encoded_time, app_license=hashed_app_license)
    #                     db.session.add(save_license)
    #                     db.session.commit()
    #
    #             return redirect(url_for('logout'))
    #
    # if license_status != 1: # license has not been activated
    #
    #     if float(elapsed[0].strip()) >= 1:
    #         #License has not been activated but the the application has been installed and ran at least once
    #         # and activation code has been created therefore we don't need to create another one
    #         if_run_once = True
    #
    #     if float(elapsed[0].strip()) - trial_period >= 0:
    #         flash("Your Trial License has expired ")
    #         return render_template('license.html', form=form, ctr=ctr)
    #
    #     if time.time() - float(elapsed[1].strip()) < 0:
    #         flash("Your Trial License has expired \n date has being adjusted backwards")
    #         return render_template('license.html', form=form, ctr=ctr)
    #
    #     if license_details is not None:
    #
    #         if license_details.duration != "":
    #             seconds_elapsed = today_time - float(base64.b64decode(license_details.duration))
    #             days, rest = divmod(seconds_elapsed, 86400)
    #             days_used = int(days)
    #         else:
    #             days_used = trial_period
    #
    #         day_remaining = trial_period - days_used
    #
    #         count = 0
    #         count_time = ""
    #
    #         if license_details.activation_code is None or license_details.activation_code == "":
    #
    #             if days_used < trial_period:
    #                 over_24hrs, remain = divmod((time.time() - float(elapsed[1].strip())), 3600)
    #                 # print(over_24hrs)
    #                 if over_24hrs >= 24:
    #                     count = int(float(elapsed[0].strip())) + 1
    #                     count_time = str(time.time())
    #                     count_and_time = str(count) + ", " + count_time
    #
    #                     with open(file_path, 'w') as wf:
    #                         wf.write(count_and_time)
    #
    #                 flash("Your Trial License expires in " + str(day_remaining) + " days")
    #
    #             else:
    #                 flash("Your Trial License has expired ")
    #                 return render_template('license.html', form=form, ctr=ctr)
    #
    #     if license_status == 3:
    #         if if_run_once == True: # licence record on table has been tampered with restore from License backup file
    #             with open(app.config['LICENSE_BACKUP_FILE'], 'r') as rf:
    #                 backup = rf.readline().split("-")
    #                 encoded_time = base64.b64encode(bytes(backup[1], 'utf-8'))
    #                 hashed_app_license = backup[0]
    #                 ValidApp(duration=encoded_time, app_license=hashed_app_license)
    #                 save_license = ValidApp(duration=encoded_time, app_license=hashed_app_license)
    #                 db.session.add(save_license)
    #                 db.session.commit()
    #             # return redirect(url_for('logout'))
    #         else:
    #             license_key(1) # Created new license activation code and populated the table and file(clds and bkclds)
    #             msg = "Your Trial License expires in " + str(day_remaining) + " days"
    #             flash(msg)

    # -------------------------------------end------------------------

    setup_details = {}
    org_detail = org_name = OwnerDetails.query.first()
    group_detail = GroupType.query.first()
    membertype_detail = MemberType.query.first()
    donation_type_detail = TypeOfDonation.query.first()
    ModeOfDonation_detail = ModeOfDonation.query.first()
    PaymentType_detail = PaymentType.query.first()

    if donation_type_detail is None:
        setup_details['donation_type_detail'] = "Donation Type/Category"
    if org_detail is None:
        setup_details['org_detail'] = "Organization"
    if group_detail is None:
        setup_details['group_detail'] = "Group"
    if membertype_detail is None:
        setup_details['membertype_detail'] = "Membership Type"
    if ModeOfDonation_detail is None:
        setup_details['ModeOfDonation_detail'] = "Mode of Donation"
    if PaymentType_detail is None:
        setup_details['PaymentType_detail'] = "Mode of Payment"

    if len(setup_details) > 0:
        flash("The following need to be setup")
        flash("----------------------------------------")
        for nosetup in setup_details:
            flash(setup_details[nosetup])
    if session["user_type"] == "admin_type":
        return render_template('index.html', title='Home')
    else:
        return render_template('index_2.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.reset_password.data:
        return redirect(url_for('pass_challenge'))

    if form.validate_on_submit():
        if form.login_type.data=="admin_option":
            session["user_type"] = "admin_type"
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            session['userdata'] = form.username.data
            login_user(user, remember=form.remember_me.data)
        else:
            session["user_type"] = "member_type"
            user = Members.query.filter_by(member_id=form.username.data).first()
            if user is not None:
                session['userdata'] = form.username.data
                if user.password_hash is None:
                    return  redirect(url_for("change_member_password"))
                else:
                    if user is None or not user.check_password(form.password.data):
                        flash('Invalid username or password')
                        return redirect(url_for('login'))

                    session['userdata'] = form.username.data

                    login_user(user, remember=form.remember_me.data)
            # else:
            #     flash('Invalid username or password')
            #     return redirect(url_for('login'))


        # if user is None or not user.check_password(form.password.data):
        #     flash('Invalid username or password')
        #     return redirect(url_for('login'))
        #login_user(user, remember=form.remember_me.data)
        SESSION_INACTIVITY_TIMEOUT_IN_SECONDS = 60
        # flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('index'))

    return render_template('login.html', title='Log in', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('index'))


@app.route('/adduser', methods=['GET', 'POST'])
@login_required
def adduser():
    if not current_user.su:
        flash('Admin right required')
        return redirect(url_for('index'))
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = AddUserForm()
    ctr = FormControl()
    if ctr.cancel.data:
        return redirect(url_for('adduser'))

    if ctr.close.data:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        user = User(username=form.username.data.strip(),
                    email=form.email.data,
                    admin=form.admin.data,
                    su=form.su.data,
                    lastname=form.lastname.data,
                    firstname=form.firstname.data

                    )
        user.set_password(form.password.data)
        user.set_challenge_1(form.challenge_1.data.replace(" ", "").lower())
        user.set_challenge_2(form.challenge_2.data.replace(" ", "").lower())
        user.set_challenge_3(form.challenge_3.data.replace(" ", "").lower())
        db.session.add(user)
        db.session.commit()
        flash('The user is now registered !')
        return redirect(url_for('adduser'))
    return render_template('adduser.html', title='Register', ctr=ctr, form=form)


@app.route('/modeofdonation', methods=['GET', 'POST'])
@login_required
def modeofdonation():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = DonationSettingForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('listmodedonation'))
        if form.validate_on_submit():
            if form.submit.data:
                mod = ModeOfDonation(mode_description=form.description.data.upper(),
                                     mode_code=form.code.data.upper().strip())
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('modeofdonation'))
        # return redirect(url_for('login'))

    return render_template('new_mode_donation.html', title='Mode of Donation', form=form)


@app.route('/listmodedonation', methods=['GET', 'POST'])
@login_required
def listmodedonation():
    """
    List all departments    """
    list_mod = ModeOfDonation.query.all()

    return render_template('mode_donation.html',
                           list_mod=list_mod, title="Modes of Donations")


@app.route('/editmodedonation/<int:id>', methods=['GET', 'POST'])
@login_required
def get_mode_details(id):
    form = DonationSettingForm()

    if form.cancel.data:
        return redirect(url_for('listmodedonation'))

    if request.method == 'POST' and form.validate_on_submit():

        mode = ModeOfDonation.query.get_or_404(id)

        if form.delete.data:
            db.session.delete(mode)
            db.session.commit()
            return redirect(url_for('listmodedonation'))

        if form.update.data:
            mode.mode_description = form.description.data.upper()
            mode.mode_code = form.code.data.upper()
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('modeofdonation')

    if request.method == 'GET' and id:
        mode = ModeOfDonation.query.filter_by(mode_id=id).first()
        form.code.data = mode.mode_code
        form.description.data = mode.mode_description
        # # form.submit.label.text = "Update"
        return render_template('new_mode_donation.html', action="edit", form=form)

    return render_template('new_mode_donation.html', action="edit", form=form)


@app.route('/member', methods=['GET', 'POST'])
@login_required
def member():
    form = MemberForm()
    ctr = FormControl()
    conn = db_conn_only()
    cursor = conn.cursor()

    form.type_id.choices = [(row.type_code, row.type_description) for row in MemberType.query.all()]
    form.type_id.choices.insert(0, ('', 'Select Member Type'))
    form.group_id.choices = ''
    # [(row.type_code, row.type_description) for row in GroupType.query.all()]

    if ctr.cancel.data:
        return redirect(url_for('member'))
    if ctr.close.data:
        return redirect(url_for('index'))
    if request.method == "POST":
        if form.validate_on_submit():
            is_user_in_db = Members.query.filter_by(member_id=form.member_id.data.strip()).first()
            if is_user_in_db:
                flash('Member ID Exist')
                return render_template('member.html', title='Add New Member', ctr=ctr, form=form)

            sqlstmt_1 = 'INSERT INTO public."Members"'
            sqlstmt_1 = sqlstmt_1 + "(member_id, member_type_ID, member_lastname, member_firstname," \
                        " member_middlename,  member_address,   member_address1,  member_email, " \
                        "member_phone_no ) VALUES(  '" + form.member_id.data.upper().strip() + "' ,'" + form.type_id.data \
                        + "' ,'" + form.lastname.data.capitalize().strip() + "' ,'" + form.firstname.data.capitalize().strip() + "' ,'" \
                        + form.middlename.data.capitalize().strip() + \
                        "' ,'" + form.address.data.capitalize().strip() + "' ,'" + form.address1.data.capitalize().strip() + "' ,'" + \
                        form.email.data + "' ,'" \
                        + form.phone_no.data + "');"
            # return sqlstmt_1
            # cursor.execute(sqlstmt_1)

            try:
                multiselect = request.form.getlist('group_id')
                for item in multiselect:
                    sqlstmt = 'SELECT * FROM public."MemberGroupLink"'
                    sqlstmt = sqlstmt +" WHERE  member_id ='" \
                              + form.id.data + "' AND  type_code ='" + item + "'"
                    if cursor.execute(sqlstmt).fetchone() is None:
                        sql_insert_stmt = 'INSERT INTO public."MemberGroupLink"'
                        sql_insert_stmt = sql_insert_stmt + "(member_id, type_code) VALUES ('" + \
                                          form.id.data + "', '" + item + "');".upper()
                        cursor.execute(sql_insert_stmt)
                ##db.session.add(detail)
                # db.session.commit()
                cursor.execute(sqlstmt_1)
                conn.commit()
                generate_member_password(form.member_id.data.upper().strip())
                ## Generate and send email.
                flash('Congratulations, you are now a registered user!')
            except sqlite3.OperationalError as err:
                # print(err)
                flash(err)
                return render_template('member.html', title='Add New Member', ctr=ctr, form=form)

            return redirect(url_for('member'))
        else:
            flash('Some Field{s} are empty')
            # return render_template('edit_member.html', title='Edit Member Details', action="edit", ctr=ctr, form=form)
    flash('Last Member ID: ' + last_member_id())
    return render_template('member.html', title='Add New Member', ctr=ctr, form=form)


@app.route('/edit_member/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    form = MemberForm()
    ctr = FormControl()
    conn = db_conn_only()
    cursor = conn.cursor()
    # searchform = SearchForm()
    family_id = []
    if ctr.cancel.data:
        if session["user_type"] == "admin_type":
            return redirect(url_for('search', module='Member'))
        elif session["user_type"] == "member_type":
            return redirect(url_for('index'))

    if ctr.close.data:
        return redirect(url_for('index'))
    if request.method == "POST":
        # return request.form['id']
        # dbmember = Members.query.get_or_404(id)
        dbmember = Members.query.filter_by(member_id=id).first()

        family_group = FamilyTrail.query.filter_by(member_id=id).first()

        if family_group is not None:
            family_id.append(family_group.family_id)
            family_id.append(family_group.member_id)

        if ctr.delete.data:
            db.session.delete(dbmember)
            db.session.commit()
            # return request.form['type_id']
        form.type_id.choices = [(row.type_code, row.type_description) for row in MemberType.query.all()]
        form.type_id.choices.insert(0, ('', 'Select Member Type'))
        form.group_id.choices = [(row.type_code, row.type_description) for row in GroupType.query.all()]
        form.type_id.data = form.member_self_type.data
        print(form.type_id.data)

        if form.validate_on_submit():
            if ctr.update.data:
                dbmember.member_id = form.member_id.data
                ##dbmember.member_type_ID = request.form['type_id']
                if session["user_type"] == "member_type":
                    dbmember.member_type_ID = form.member_self_type.data
                else:
                    dbmember.member_type_ID = request.form['type_id']

                # dbmember.member_group_id = request.form['group_id']
                # return dbmember.member_group_id + request.form['group_id']
                dbmember.member_lastname = form.lastname.data
                dbmember.member_firstname = form.firstname.data
                dbmember.member_middlename = form.middlename.data
                dbmember.member_address = form.address.data
                dbmember.member_address1 = form.address1.data
                dbmember.member_email = form.email.data
                dbmember.member_phone_no = form.phone_no.data
                try:
                    delete_text = 'DELETE FROM public."MemberGroupLink"'
                    sql_delete =  delete_text + " WHERE  member_id = '" + form.member_id.data + "'"
                    # return sql_delete
                    cursor.execute(sql_delete)
                    conn.commit()
                    multiselect = request.form.getlist('group_id')
                    for item in multiselect:
                        if item != '':
                            sql_insert_stmt = "INSERT INTO MemberGroupLink(member_id, type_code) VALUES ('" + \
                                              form.id.data + "', '" + item + "');".upper()
                            cursor.execute(sql_insert_stmt)
                    conn.commit()
                except sqlite3.OperationalError as err:
                    # print(err)
                    flash(err)
                    return render_template('member.html', title='Add New Member', ctr=ctr, form=form)
                db.session.commit()
                flash('Record Updated!')

            if session["user_type"] == "admin_type":
                return redirect(url_for('search', module='Member'))
            elif session["user_type"] == "member_type":
                return redirect(url_for('index'))



        else:
            flash('Some Field{s} are empty')
            return render_template('edit_member.html', title='Edit Member Details', family_id=family_id, action="edit",
                                   ctr=ctr, form=form)
    # return redirect(url_for('search'))

    if request.method == 'GET' and id:
        # return id
        dbmember = Members.query.filter_by(member_id=id).first()
        form.type_id.choices = [(row.type_code, row.type_description) for row in MemberType.query.all()]
        form.type_id.choices.insert(0, ('Select Member Type', '----'))

        group_qry_stmt = """select
                   g1.type_code,
                   g1.type_description
               from
                   public."GroupType" g1,
                   public."MemberGroupLink" gl1
               where
                   g1.type_code = gl1.type_code
                   and gl1.member_id = '{}' """

        group_qry = group_qry_stmt.format(dbmember.member_id)
        #return group_qry
        cursor.execute(group_qry)
        choice_from_db = cursor.fetchall()
        form.group_id.choices = [(row[0], row[1]) for row in choice_from_db]

        family_group = FamilyTrail.query.filter_by(member_id=id).first()

        if family_group is not None:
            family_id.append(family_group.family_id)
            family_id.append(family_group.member_id)

        if dbmember:
            #form.id = dbmember.id
            form.member_id.data = dbmember.member_id
            form.type_id.data = dbmember.member_type_id
            form.member_self_type.data = dbmember.member_type_id ##enable get member type when a member is logged in
            # form.group_id.data = dbmember.member_group_id
            form.lastname.data = dbmember.member_lastname
            form.firstname.data = dbmember.member_firstname
            form.middlename.data = dbmember.member_middlename
            form.address.data = dbmember.member_address
            form.address1.data = dbmember.member_address1
            form.email.data = dbmember.member_email
            form.phone_no.data = dbmember.member_phone_no
            return render_template('edit_member.html', title='Edit Member Details', family_id=family_id, action="edit",
                                   ctr=ctr, form=form)
        else:
            flash('No Record Found')

        return redirect(url_for('search', module='Member'))


@app.route('/donations', methods=['GET', 'POST'])
@login_required
def donations():
    form = DonationForm()
    ctr = FormControl()
    conn = db_conn_only()
    cursor = conn.cursor()
    form.mode_id.choices = [(row.mode_code, row.mode_description) for row in ModeOfDonation.query.all()]
    form.donation_type_id.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    # form.payment_type_id.choices = [(row.type_code, row.type_description) for row in PaymentType.query.all()]
    if ctr.cancel.data:
        session['donation_update'] = None
        return redirect(url_for('donations'))
    if ctr.close.data:
        return redirect(url_for('index'))
    if ctr.delete.data:
        if current_user.admin:
            del_trail_stmt = "DELETE FROM Donationtrail  WHERE donation_id = '" + form.donation_id.data + "'"
            del_donation_stmt = "DELETE FROM Donations  WHERE donation_id = '" + form.donation_id.data + "'"
            try:
                cursor.execute(del_trail_stmt)
                cursor.execute(del_donation_stmt)
                conn.commit()
                flash('Record Updated!')
            except sqlite3.OperationalError as err:
                # print(err)
                flash(err)
        return redirect(url_for('donations'))

    if form.generate_id.data:
        # print(form.generate_id.label.text)
        id = form.member_id.data
        user_in_db = Members.query.filter_by(member_id=id).first()
        if user_in_db:
            form.member_name.data = user_in_db.member_lastname + " ," + user_in_db.member_firstname
            form.donation_id.data = form.donation_type_id.data + '-' + form.member_id.data
            if session.get('donation_update') and session['donation_update'] == "admin":
                form.generate_id.label.text = "Change Donation ID"
                # session['donation_update'] = None
                return render_template('donation.html', action='update', title='Update Donation Detail', ctr=ctr,
                                       form=form)
            else:
                # flash('Donation ID:' + form.donation_id.data)
                return render_template('donation.html', title='New Donation', ctr=ctr, form=form)
        else:
            form.donation_id.data = None
            flash('Member ID does not exist')
            return render_template('donation.html', title='New Donation', ctr=ctr, form=form)
    if ctr.update.data and not current_user.admin:
        form.donation_type_id.data = session['donation_type_id_choice']
        return form.donation_type_id.data

    if request.method == "POST":
        if form.validate_on_submit():
            # return 'happy'
            form.donation_id.data = form.donation_type_id.data + "-" + form.member_id.data
            flash('Donation ID:' + form.donation_id.data)
            user_in_db = Donations.query.filter_by(donation_id=form.donation_id.data).first()
            if user_in_db is not None and not ctr.update.data:
                flash('Record of member for this donation exists')
                return render_template('donation.html', title='Add New Member', ctr=ctr, form=form)
            detail = Donations(
                donation_id=form.donation_id.data,
                donation_type_id=form.donation_type_id.data,
                member_id=form.member_id.data,
                donation_date=form.date.data,
                amount=form.amount.data,
                donation_mode_id=form.mode_id.data,
                # payment_type_id = form.payment_type_id.data
            )
            if ctr.submit.data:
                db.session.add(detail)
                #return "here"
                db.session.commit()
                flash('Record Added!')

            if ctr.update.data:
                if current_user.admin:
                    check_status = []

                    check_status = UpdatePayment(form.donation_id.data, form.amount.data) \
                        .update_donation()
                    payment_status = check_status[1]
                    ok_to_update = check_status[0]
                    if not ok_to_update:
                        flash('Record not update: Already paid amount greater than adjusted amount')
                        return redirect(url_for('donations'))
                    sql_update_stmt = 'UPDATE public."Donations" SET donation_id ='
                    sql_update_stmt=  sql_update_stmt  + "'" + form.donation_id.data \
                                      + "', donation_type_id ='" + form.donation_type_id.data \
                                      + "', member_id = '" + form.member_id.data \
                                      + "', donation_date = '" + \
                                      str(datetime.strptime(datetime.strftime(form.date.data, '%Y-%m-%d'), '%Y-%m-%d')) \
                                      + "', amount ='" + str(form.amount.data) \
                                      + "', donation_mode_id ='" + form.mode_id.data \
                                      + "', payment_status ='" + str(payment_status) \
                                      + "', comment = '" + form.comment.data + "' WHERE donation_id = '" + \
                                      session['old_donation_id'] + "'"
                    # return sql_update_stmt
                    sql_update_child = 'UPDATE public."Donationtrail" SET donation_id ='
                    sql_update_child =  sql_update_child + "'" + form.donation_id.data + \
                                       "' WHERE donation_id = '" + session['old_donation_id'] + "'"
                    # return sql_update_stmt
                    try:
                        cursor.execute(sql_update_stmt)
                        cursor.execute(sql_update_child)
                        conn.commit()
                        flash('Record Updated!')
                    except sqlite3.OperationalError as err:
                        # print(err)
                        flash(err)
                return redirect(url_for('donations'))

                user_in_db.donation_id = form.donation_id.data
                user_in_db.donation_type_id = form.donation_type_id.data
                user_in_db.member_id = form.member_id.data
                user_in_db.donation_date = form.date.data
                user_in_db.amount = form.amount.data
                user_in_db.donation_mode_id = form.mode_id.data
                user_in_db.comment = form.comment.data
                db.session.commit()
                flash('Record Updated!')
            return redirect(url_for('donations'))

    if request.method == 'GET' and request.args.get("id"):
        if current_user.admin:
            action = "update"
            session['donation_update'] = "admin"
        else:
            action = "edit"
        id = request.args.get("id")
        form.generate_id.label.text = "Change Donation ID"
        # return id
        dbmember = Donations.query.filter_by(donation_id=id).first()
        mid = dbmember.donor.member_id
        form.donation_type_id.choices = [(row.type_code, row.type_description) for row in
                                         TypeOfDonation.query.all()]
        form.mode_id.choices = [(row.mode_code, row.mode_description) for row in ModeOfDonation.query.all()]

        user_in_db = Members.query.filter_by(member_id=mid).first()
        if user_in_db:
            form.member_name.data = user_in_db.member_lastname + " ," + user_in_db.member_firstname
            # form.donation_id.data = form.donation_type_id.data + '-' + form.member_id.data

        if dbmember:
            form.donation_id.data = dbmember.donation_id
            session['old_donation_id'] = dbmember.donation_id
            form.donation_type_id.data = dbmember.donation_type_id
            session['donation_type_id_choice'] = dbmember.donation_type_id
            form.member_id.data = dbmember.member_id
            form.date.data = dbmember.donation_date
            form.amount.data = float(dbmember.amount)
            # return 'Hello' + str(form.amount.data)
            form.mode_id.data = dbmember.donation_mode_id
            form.comment.data = dbmember.comment
            return render_template('donation.html', action=action, title='Edit Donation Details', ctr=ctr, form=form)
    if request.method == 'GET' and request.args.get('mid'):
        form.member_id.data = request.args.get('mid')
        # print(form.member_id.data)
        # return form.member_id.data
        return render_template('donation.html', title='New Donation', ctr=ctr, form=form)
    return render_template('donation.html', title='New Donation', ctr=ctr, form=form)


"""
Edit Donations
"""


# @app.route('/edit_donation/<string:id>', methods=['GET', 'POST'])
# @login_required
# def edit_donation(id):
#     form = DonationForm()
#     ctr = FormControl()
#     conn = db_conn_only()
#     cursor = conn.cursor()
#     searchform = SearchForm()
#     if ctr.cancel.data:
#         return redirect(url_for('search', module='Member'))
#     if ctr.close.data:
#         return redirect(url_for('index'))
#
#     if request.method == 'GET' and id:
#         # return id
#         dbmember = Donations.query.filter_by(donation_id=id).first()
#         mid = dbmember.donor.member_id
#         form.donation_type_id.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
#         form.mode_id.choices = [(row.mode_code, row.mode_description) for row in ModeOfDonation.query.all()]
#
#         user_in_db = Members.query.filter_by(member_id=mid).first()
#         if user_in_db:
#             form.member_name.data = user_in_db.member_lastname + " ," + user_in_db.member_firstname
#
#         if dbmember:
#             form.donation_id.data = dbmember.donation_id
#             session['old_donation_id'] = dbmember.donation_id
#             return session['old_donation_id']
#             form.donation_type_id.data = dbmember.donation_type_id
#             form.member_id.data = dbmember.member_id
#             form.date.data = dbmember.donation_date
#             form.amount.data = float(dbmember.amount)
#             # return 'Hello' + str(form.amount.data)
#             form.mode_id.data = dbmember.donation_mode_id
#             form.comment.data = dbmember.comment
#         return render_template('donation.html', title='Edit Donation Details', action="edit", ctr=ctr, form=form)
#
#     return redirect(url_for('search', module='Donation'))
#

"""
Routes for type pf Donations

"""


@app.route('/typeofdonation', methods=['GET', 'POST'])
@login_required
def typeofdonation():
    form = DonationSettingForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('listtypedonation'))
        if form.validate_on_submit():
            if form.submit.data:
                mod = TypeOfDonation(type_description=form.description.data.upper(),
                                     type_code=form.code.data.upper().strip(),
                                     date=form.date.data)
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('typeofdonation'))
        # return redirect(url_for('login'))

    return render_template('new_type_donation.html', title='New Donation Type', form=form)


@app.route('/listtypedonation', methods=['GET', 'POST'])
@login_required
def listtypedonation():
    """
    List all departments    """
    list_mod = TypeOfDonation.query.all()

    return render_template('type_donation.html',
                           list_mod=list_mod, title="Types of Donation")


@app.route('/edittypedonation/<int:id>', methods=['GET', 'POST'])
@login_required
def get_type_donation_details(id):
    form = DonationSettingForm()

    if form.cancel.data:
        return redirect(url_for('listtypedonation'))

    if request.method == 'POST' and form.validate_on_submit():

        mode = TypeOfDonation.query.get_or_404(id)
        if form.delete.data:
            db.session.delete(mode)
            db.session.commit()
            return redirect(url_for('listtypedonation'))

        if form.update.data:
            mode.type_description = form.description.data.upper()
            mode.date = form.date.data
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('typeofdonation')

    if request.method == 'GET' and id:
        mode = TypeOfDonation.query.filter_by(type_id=id).first()
        form.code.data = mode.type_code
        form.description.data = mode.type_description
        form.date.data = mode.date
        # # form.submit.label.text = "Update"
        return render_template('new_type_donation.html', action="edit", form=form)

    return render_template('new_type_donation.html', title='Edit Donation Type', action="edit", form=form)


"""
Routes for Redemption Mode

"""


@app.route('/modeofredemption', methods=['GET', 'POST'])
@login_required
def modeofredemption():
    form = DonationSettingForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('listmoderedemption'))
        if form.validate_on_submit():
            if form.submit.data:
                mod = PaymentType(type_description=form.description.data.upper(),
                                  type_code=form.code.data.upper().strip())
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('modeofredemption'))
        # return redirect(url_for('login'))

    return render_template('new_mode_redemption.html', title='Mode of Redemption', form=form)


@app.route('/listmoderedemption', methods=['GET', 'POST'])
@login_required
def listmoderedemption():
    """
    List all departments    """
    list_mod = PaymentType.query.all()

    return render_template('mode_redemption.html',
                           list_mod=list_mod, title="Mode of Redemption")


@app.route('/editlistmoderedemption/<int:id>', methods=['GET', 'POST'])
@login_required
def get_type_redemption_details(id):
    form = DonationSettingForm()

    if form.cancel.data:
        return redirect(url_for('listmoderedemption'))

    if request.method == 'POST' and form.validate_on_submit():
        mode = PaymentType.query.get_or_404(id)

        if form.delete.data:
            db.session.delete(mode)
            db.session.commit()
            return redirect(url_for('listmoderedemption'))

        if form.update.data:
            mode.type_description = form.description.data.upper()
            mode.type_code = form.code.data.upper()
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('modeofredemption')

    if request.method == 'GET' and id:
        mode = PaymentType.query.filter_by(type_id=id).first()
        form.code.data = mode.type_code
        form.description.data = mode.type_description
        # # form.submit.label.text = "Update"
        return render_template('new_mode_redemption.html', action="edit", form=form)

    return render_template('new_mode_redemption.html', action="edit", form=form)


"""
Routes for Relation Type

"""


@app.route('/relationtype', methods=['GET', 'POST'])
@login_required
def relationtype():
    form = DonationSettingForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('listrelationtype'))
        if form.validate_on_submit():
            if form.submit.data:
                mod = FamilyRelation(relation_description=form.description.data.upper(),
                                     relation_id=form.code.data.upper().strip())
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('listrelationtype'))
        # return redirect(url_for('login'))

    return render_template('new_relation_type.html', title='Family Relation Type', form=form)


@app.route('/listrelationtype', methods=['GET', 'POST'])
@login_required
def listrelationtype():
    """
    List all departments    """
    list_mod = FamilyRelation.query.all()

    return render_template('relation_type.html',
                           list_mod=list_mod, title="Family Relation Type")


@app.route('/editlistrelationtype/<int:id>', methods=['GET', 'POST'])
@login_required
def get_relation_type_details(id):
    form = DonationSettingForm()

    if form.cancel.data:
        return redirect(url_for('listrelationtype'))

    if request.method == 'POST' and form.validate_on_submit():
        mode = FamilyRelation.query.get_or_404(id)

        if form.delete.data:
            db.session.delete(mode)
            db.session.commit()
            return redirect(url_for('listrelationtype'))

        if form.update.data:
            mode.relation_description = form.description.data.upper()
            mode.relation_id = form.code.data.upper()
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('relationtype')

    if request.method == 'GET' and id:
        mode = FamilyRelation.query.filter_by(id=id).first()
        form.code.data = mode.relation_id
        form.description.data = mode.relation_description
        # # form.submit.label.text = "Update"
        return render_template('new_relation_type.html', action="edit", form=form)

    return render_template('new_relation_type.html', action="edit", form=form)


# ------------------------------------------------


"""
Routes for Member Type

"""


@app.route('/membertype', methods=['GET', 'POST'])
@login_required
def membertype():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = DonationSettingForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('listmembertype'))
        if form.validate_on_submit():
            if form.submit.data:
                mod = MemberType(type_description=form.description.data.upper(),
                                 type_code=form.code.data.upper().strip())
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('membertype'))
        # return redirect(url_for('login'))

    return render_template('new_membertype.html', title='Member Type', form=form)


@app.route('/listmembertype', methods=['GET', 'POST'])
@login_required
def listmembertype():
    """
    List all departments    """
    list_mod = MemberType.query.all()

    return render_template('membertype.html',
                           list_mod=list_mod, title="Member Type")


@app.route('/editlistmembertype/<int:id>', methods=['GET', 'POST'])
@login_required
def get_membertype_details(id):
    form = DonationSettingForm()

    if form.cancel.data:
        return redirect(url_for('listmembertype'))

    if request.method == 'POST' and form.validate_on_submit():
        formdetail = request.form
        # for key in formdetail:
        # print('form key ' + formdetail[key])
        # if form.validate_on_submit():
        #     return 'Validated'

        mode = MemberType.query.get_or_404(id)
        if form.delete.data:
            db.session.delete(mode)
            db.session.commit()
            return redirect(url_for('listmembertype'))

        if form.update.data:
            mode.type_description = form.description.data.upper()
            mode.type_code = form.code.data.upper()
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('membertype')

    if request.method == 'GET' and id:
        mode = MemberType.query.filter_by(type_id=id).first()
        form.code.data = mode.type_code
        form.description.data = mode.type_description
        # # form.submit.label.text = "Update"
        return render_template('new_membertype.html', action="edit", form=form)

    return render_template('new_membertype.html', action="edit", form=form)


"""
Routes for Group Type
"""


@app.route('/grouptype', methods=['GET', 'POST'])
@login_required
def grouptype():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = DonationSettingForm()
    if request.method == "POST":
        if form.cancel.data:
            return redirect(url_for('listgrouptype'))
        if form.validate_on_submit():
            if form.submit.data:
                mod = GroupType(type_description=form.description.data.upper(),
                                type_code=form.code.data.upper().strip())
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('grouptype'))
        # return redirect(url_for('login'))

    return render_template('new_grouptype.html', title='Groups', form=form)


@app.route('/listgrouptype', methods=['GET', 'POST'])
@login_required
def listgrouptype():
    """
    List all departments    """
    list_mod = GroupType.query.all()

    return render_template('grouptype.html',
                           list_mod=list_mod, title="Groups")


@app.route('/editlistgrouptype/<int:id>', methods=['GET', 'POST'])
@login_required
def get_grouptype_details(id):
    form = DonationSettingForm()

    if form.cancel.data:
        return redirect(url_for('listgrouptype'))

    if request.method == 'POST' and form.validate_on_submit():
        formdetail = request.form

        mode = GroupType.query.get_or_404(id)
        if form.delete.data:
            db.session.delete(mode)
            db.session.commit()
            return redirect(url_for('listgrouptype'))

        if form.update.data:
            mode.type_description = form.description.data.upper()
            mode.type_code = form.code.data.upper()
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')
        return redirect('grouptype')

    if request.method == 'GET' and id:
        mode = GroupType.query.filter_by(type_id=id).first()
        form.code.data = mode.type_code
        form.description.data = mode.type_description
        # # form.submit.label.text = "Update"
        return render_template('new_grouptype.html', action="edit", form=form)
    return render_template('new_grouptype.html', action="edit", form=form)


@app.route('/list_users', methods=['GET', 'POST'])
@login_required
def list_users():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    """
    List all system Users    """
    list_mod = User.query.all()
    # print(list_mod)
    return render_template('system_users.html', list_mod=list_mod, title="System Users")


# ----------------------------Search Route---------------------------
@app.route('/search/<string:module>', methods=['GET', 'POST'])
@login_required
def search(module):
    form = SearchForm()
    ctr = FormControl()

    if ctr.cancel.data:
        return redirect(url_for('search', module=form.get_module.data))
    if ctr.close.data:
        return redirect(url_for('index'))
    if ctr.delete.data:
        pass

    if request.method == "GET":
        if module =='member_self': ## if it is comming from a logged in user 
            return redirect(url_for('index'))

        form.get_module.data = module
        flash(form.get_module.data)
    if request.method == "POST" and form.validate_on_submit():
        look_for = '%{0}%'.format(form.src_string.data)
        session['searchstr'] = form.src_string.data
        session['updated'] = False
        if form.get_module.data == 'Add Donation':
            search_module_id = 1
        if form.get_module.data == 'Donation':
            search_module_id = 2
        if form.get_module.data == 'Member':
            search_module_id = 3

        if search_module_id == 1:
            if form.search_option.data == 'id_option':
                flash('Use the "Name" option')
                return redirect(url_for('search', module='Add Donation'))

            if form.search_option.data == 'name_option':

                # look_for = '%{0}%'.format(form.src_string.data)
                typename = []
                isdata, qryresult, typename = Search(look_for).add_donation_name_option()
                # print(isdata, qryresult, typename)
                if isdata:
                    return render_template('new_donation_search_result.html', \
                                           result=qryresult, typename=typename, title="Search Result",
                                           module='Add Donation')

        elif search_module_id == 2:

            if form.search_option.data == 'name_option':
                session['searchstr_option'] = 'name_option'
                isdata, qryresult, typename = Search(look_for).donation_name_option()
                # print(isdata, qryresult, typename)
                if isdata:
                    return render_template('donation_search_by_name_result.html',
                                           result=qryresult, typename=typename, title="Search Result",
                                           module='Donation')
                else:
                    flash('No Result Found')

            if form.search_option.data == 'id_option':
                # session['searchstr_name'] = 'id_option'
                session['searchstr_option'] = 'id_option'
                # look_for = '%{0}%'.format(form.src_string.data)
                isdata, qryresult, typename = Search(look_for).donation_id_option()
                # print(isdata, qryresult, typename)
                if isdata:
                    return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                           result=qryresult, title="Search Result")
                return redirect(url_for('search', module='Donation'))

        elif search_module_id == 3:
            if form.search_option.data == 'id_option':
                look_for = format(form.src_string.data)
                dbmember = db.session.query(Members).filter(or_(Members.member_id == look_for.lower(),
                                                                Members.member_id == look_for.upper())).first()
                if dbmember:
                    return redirect(url_for('edit_member', id=dbmember.member_id))
                else:
                    flash('No Record Found')
                return render_template('search.html', title=module, ctr=ctr, form=form)

            if form.search_option.data == 'name_option':
                # look_for = '%{0}%'.format(form.src_string.data)
                qryresultcount = db.session.query(Members).filter(or_(Members.member_firstname.ilike(look_for),
                                                                      Members.member_lastname.ilike(look_for),
                                                                      Members.member_middlename.ilike(
                                                                          look_for))).order_by(
                    Members.member_lastname.desc()).count()
                qryresult = db.session.query(Members).filter(or_(Members.member_firstname.ilike(look_for),
                                                                 Members.member_lastname.ilike(look_for),
                                                                 Members.member_middlename.ilike(look_for))).order_by(
                    Members.member_lastname.desc())
                if qryresultcount > 0:
                    return render_template('member_search_result.html',
                                           result=qryresult, title="Search Result", module='Member')
                    flash('No Record Found')

    return render_template('search.html', title=module, calledby=module, ctr=ctr, form=form)


# ----------------------------------------------------------------------------------

@app.route('/donationstrail', methods=['GET', 'POST'])
@login_required
def donationstrail():
    # --------------Create a class for this---------------
    look_for = '%{0}%'.format(session['searchstr'])

    if session.get('searchstr_option') and session['searchstr_option'] == 'name_option':
        isdata, qryresult, typename = Search(look_for).donation_name_option()

    elif session.get('searchstr_option') and session['searchstr_option'] == 'id_option':
        # return 'We are in ID'
        isdata, qryresult, typename = Search(look_for).donation_id_option()

    # ----------------end create class-----------------
    form = DonationTrailForm()
    ctr = FormControl()
    form.payment_type_id.choices = [(row.type_code, row.type_description) for row in PaymentType.query.all()]
    if ctr.cancel.data:

        if session.get('searchstr_option') and session['searchstr_option'] == 'name_option':
            look_for = '%{0}%'.format(session['searchstr'])
            isdata, qryresult, typename = Search(look_for).donation_name_option()
            # print(isdata, qryresult, typename)
            if isdata:
                return render_template('donation_search_by_name_result.html',
                                       result=qryresult, typename=typename, title="Search Result",
                                       module='Donation')
        elif session.get('searchstr_option') and session['searchstr_option'] == 'id_option':
            isdata, qryresult, typename = Search(look_for).donation_id_option()
            # print(isdata, qryresult, typename)
            if isdata:
                return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                       result=qryresult, title="Search Result")
            return redirect(url_for('search', module='Donation'))

    if ctr.close.data:
        return redirect(url_for('index'))  # change to take you back list of donation for member

    if request.method == "POST":
        if form.validate_on_submit():
            total_paid = UpdatePayment(form.donation_id.data, form.amount.data).total_paid
            # flash(str(total_paid))
            update = UpdatePayment(form.donation_id.data, form.amount.data).payment_complete()
            # flash(update)
            if not session['updated']:
                if update:
                    status_ok = Donations.query.filter_by(donation_id=form.donation_id.data).first()
                    status_ok.payment_status = True
                # db.session.commit()

                detail = Donationstrail(
                    donation_id=form.donation_id.data,
                    donation_type_id=form.donation_type_id.data,
                    payment_date=form.payment_date.data,
                    amount=form.amount.data,
                    payment_type_id=form.payment_type_id.data,
                    payment_details=form.payment_details.data
                )
                db.session.add(detail)
                db.session.commit()
                session['updated'] = True
                flash('Record Updated!')



            if session.get('searchstr_name'):
                return redirect(url_for('search', module='Donation'))
                # return render_template('donation_search_by_name_result.html',
                #                        result=qryresult, typename=typename, title="Search Result", module='Donation')
            else:

                if session["user_type"] == "member_type":
                    isdata, qryresult, typename = Search(look_for).donation_id_option()
                    return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                           result=qryresult, title="Search Result")

                if session['searchstr_option'] == 'name_option':
                    isdata, qryresult, typename = Search(look_for).donation_name_option()
                    return render_template('donation_search_by_name_result.html', typename=typename, module='Donation',
                                           result=qryresult, title="Search Result")
                if session['searchstr_option'] == 'id_option':
                    isdata, qryresult, typename = Search(look_for).donation_id_option()
                    return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                           result=qryresult, title="Search Result")
        else:
            return render_template('donation_payment.html', title='New Donation', ctr=ctr, form=form)
    else:
        if request.method == 'GET' and request.args.get('id'):
            session['updated'] = False
            id = request.args.get('id')
            ##return request.args.get('id')
            donation = Donations.query.filter_by(donation_id=id).first()
            form.donation_type_id.data = donation.donation_type_id
            form.member_id.data = donation.member_id

            try:
                donation_member = Members.query.filter_by(member_id=donation.member_id).first()
                donation_type = TypeOfDonation.query.filter_by(type_code=donation.donation_type_id).first()
                form.donation_id.data = donation.donation_id
                form.member_name.data = donation_member.member_lastname + " , " + donation_member.member_firstname
                form.donation_type_name.data = donation_type.type_description
                flash(form.donation_type_id)
            except:
                flash("Oops!  Invalid Donation ID .  Try again...")
            return render_template('donation_payment.html', ctr=ctr, form=form)

        if session.get('searchstr_name'):
            return render_template('donation_search_by_name_result.html',
                                   result=qryresult, typename=typename, title="Search Result", module='Donation')

        return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                               result=qryresult,
                               title="Search Result")


@app.route('/testmodule/<string:id>')
@login_required
def testmodule(id):
    # --------------Create a class for this---------------
    look_for = '%{0}%'.format(session['searchstr'])
    qryresult = db.session.query(Donations).filter(or_(Donations.donation_id.ilike(look_for),
                                                       Donations.member_id.ilike(look_for))).order_by(
        Donations.donation_type_id.desc())

    typename = {}
    for x in qryresult:
        decription = TypeOfDonation.query.filter_by(type_code=x.donation_type_id).first()
        typename[x.donation_type_id] = decription.type_description
    # session['searchstr'] = None
    # ----------------end create class-----------------
    form = DonationTrailForm()
    ctr = FormControl()
    form.payment_type_id.choices = [(row.type_code, row.type_description) for row in PaymentType.query.all()]
    if ctr.cancel.data:
        return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                               result=qryresult,
                               title="Search Result")
    if ctr.close.data:
        return redirect(url_for('index'))  # change to take you back list of donation for member

    if request.method == "POST":
        if form.validate_on_submit():
            update = UpdatePayment(form.donation_id.data, form.amount.data).payment_complete()
            if update:
                status_ok = Donations.query.filter_by(donation_id=form.donation_id.data).first()
                status_ok.payment_status = True
                db.session.commit()
            detail = Donationstrail(
                donation_id=form.donation_id.data,
                donation_type_id=form.donation_type_id.data,
                payment_date=form.payment_date.data,
                amount=form.amount.data,
                payment_type_id=form.payment_type_id.data,
                payment_details=form.payment_details.data
            )
            db.session.add(detail)
            db.session.commit()
            flash('Record Added!')

            return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                   result=qryresult,
                                   title="Search Result")
        else:
            return render_template('donation_payment.html', title='New Donation', ctr=ctr, form=form)

    if request.method == 'GET' and id:
        donation = Donations.query.filter_by(donation_id=id).first()
        form.donation_type_id.data = donation.donation_type_id
        form.member_id.data = donation.member_id

        try:
            donation_member = SearchData(table_name=Members, field_id='member_id',
                                         src_string=donation.member_id).get_member()
            donation_type = SearchData(table_name=TypeOfDonation, field_id='type_code',
                                       src_string=donation.donation_type_id).get_member()
            # donation_type = TypeOfDonation.query.filter_by(type_code=donation.donation_type_id).first()
            form.donation_id.data = donation.donation_id
            form.member_name.data = donation_member.member_lastname + " , " + donation_member.member_firstname
            form.donation_type_name.data = donation_type.type_description
            flash(form.donation_type_id)
        except:
            flash("Oops!  Invalid Donation ID .  Try again...")
        return render_template('donation_payment.html', ctr=ctr, form=form)
    return render_template('donation_payment.html', ctr=ctr, form=form)


@app.route('/donationdetails/<string:id>')
@login_required
def donationdetails(id):
    # return id
    """
        List all departments    """
    if session.get('paydetail') and session['paydetail']:
        if session["user_type"] == "member_type":
            look_for = '%{0}%'.format(session['userdata'])
        elif session["user_type"] == "admin_type":
            look_for = '%{0}%'.format(session['searchstr'])



        if session.get('searchstr_option') and session['searchstr_option'] == 'name_option':
            look_for = '%{0}%'.format(session['searchstr'])
            isdata, qryresult, typename = Search(look_for).donation_name_option()
            # print(isdata, qryresult, typename)
            if isdata:
                session['paydetail'] = None
                session['paydetail'] = False
                return render_template('donation_search_by_name_result.html',
                                       result=qryresult, typename=typename, title="Search Result",
                                       module='Donation')
        elif session.get('searchstr_option') and session['searchstr_option'] == 'id_option':
            isdata, qryresult, typename = Search(look_for).donation_id_option()
            # print(isdata, qryresult, typename)
            if isdata:
                session['paydetail'] = None
                session['paydetail'] = False
                return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                       result=qryresult, title="Search Result")
            return redirect(url_for('search', module='Donation'))

        elif session["user_type"] == "member_type":
            isdata, qryresult, typename = Search(look_for).donation_id_option()
            # print(isdata, qryresult, typename)
            if isdata:
                session['paydetail'] = None
                session['paydetail'] = False
                return render_template('donation_search_by_id_result.html', typename=typename, module='member_self',
                                       result=qryresult, title="Search Result")
            return redirect(url_for('search', module='member_self')) #replaced donation with member_self

    donationid = Donations.query.filter_by(donation_id=id).first()
    qryresult = donationid.trail.all()
    donation_amt = donationid.amount
    summary = {}
    if len(qryresult) > 0:
        sum_amt_paid = 0
        typename = {}
        for x in qryresult:
            sum_amt_paid = sum_amt_paid + x.amount
            decription = TypeOfDonation.query.filter_by(type_code=x.donation_type_id).first()
            typename[x.donation_type_id] = decription.type_description
            donation = Donations.query.filter_by(donation_id=x.donation_id).first()
            member = Members.query.filter_by(member_id=donation.member_id).first()
            typename[x.donation_id] = member.member_firstname + ' ' + member.member_lastname
            balance = donation_amt - sum_amt_paid
        session['paydetail'] = True
        summary['donation_amt'] = donation_amt
        summary['sum_amt_paid'] = sum_amt_paid
        summary['balance'] = balance
        summary['timestamp'] = time.strftime("%d-%B-%Y:%H:%M")

        # return render_template('donation_details.html', typename=typename, result=qryresult,
        #                        title="Details of Payments")
        # return render_template('donation_details.html',  typename=typename, result=qryresult,
        #                        title="Details of Payments", balance=balance, donation=donation_amt,
        #                        sum_amt_paid=sum_amt_paid)
        return render_template('donation_details.html', typename=typename, result=qryresult,
                               title="Details of Payments", summary=summary)

    flash('Pay status error')
    return redirect(url_for('index'))


# -*- coding: utf-8 -*-

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    form = UploadForm()
    clean_data(app.config['UPLOAD_FOLDER'], "uploaded files")  ## Clean up the upload folder
    if request.method == 'POST':
        form = UploadForm()
        uploaddir = app.config['UPLOAD_FOLDER']
        errorfolder = app.config['ERROR_FOLDER']

        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            form.file.data.save(os.path.join(uploaddir, filename))
            # f = open(os.path.join(uploaddir, filename))
            # #print(os.path.join(uploaddir, filename))
            file_path = os.path.join(uploaddir, filename)
            name, ext = splitext(file_path)
            records = ''
            if ext in ['.xls', '.xlsx', '.csv']:
                if ext in ['.xls', '.xlsx']:
                    records = pd.read_excel(file_path, index_col=None)
                    # print(records)

                if ext == '.csv':
                    with open(file_path, 'rb') as f:
                        result = chardet.detect(f.read())
                    try:
                        records = pd.read_csv(file_path, encoding=result['encoding'])
                    except ParserError:
                        flash('Error Loading File: Check File data format')
                        return render_template('uploadfile.html', form=form)

                records.reset_index(drop=True)
                records.head(5)
                verifyheader = UploadsManager(file_path, ext, 'Members')
                if not verifyheader.verify_header():
                    missing_field = verifyheader.missing_field
                    missing_field = pd.DataFrame(verifyheader.missing_field, columns=['Missing Fields'])
                    view_missing_file = missing_field['Missing Fields'].tolist()
                    # view_missing_file = view_missing_file_1
                    flash('File Uploaded is missing some fields')
                    return render_template('uploadfile.html', missing_fields=view_missing_file, missing=True, form=form)
                #db_path = app.config['SQLALCHEMY_DATABASE_URI']
                #engine = create_engine(db_path, echo=False)

                ##Updated for postgres SQL.

                #conn = db_conn_only()
                #engine = create_engine('postgresql+psycopg2://db_donatrack:123456@localhost:5432/donatrack_web')
                database_url = app.config['SQLALCHEMY_DATABASE_URI']
                url = database_url.split('postgres://')[1]
                engine = create_engine('postgresql+psycopg2://{}'.format(url), convert_unicode=True, encoding='utf8')
                #engine = create_engine(database_url)
                msg_type = ''
                error = []
                error_rec = []
                num_rows = len(records)
                no_rec_loaded = 0
                # Iterate one row at a time
                for i in range(num_rows):
                    try:
                        # Try inserting the row

                        #records.iloc[i:i + 1].to_sql('Members', con=engine, if_exists='append', index=False)

                        records.iloc[i:i + 1].to_sql('Members', con=engine, schema='public',
                                                     if_exists='append', index=False)

                        no_rec_loaded = no_rec_loaded + 1

                    except IntegrityError as err:
                        error = str(err.args)
                        error_rec.append(records.iloc[i:i + 1].values)
                        remove_str = ["('(sqlite3.IntegrityError)", "'", ",)"]
                        for r in remove_str:
                            if r in error:
                                error = error.replace(r, '')

                        if "NOT NULL" in error:
                            msg_type = error + "Some Field are empty"

                        if "UNIQUE" in error:
                            msg_type = error

                if len(error_rec) > 1:
                    error_msg = error
                    error_file_name = "Members_data_upload_error_" + datetime.now().strftime(
                        "%Y_%m_%d_%H-%S") + ".log"
                    error_file = os.path.join(errorfolder, error_file_name.strip(' '))
                    # return error_file

                    f = open(error_file, 'w')
                    f.write("Error: " + error + "\r\n")
                    f.close()

                    with open(error_file, 'a') as errortxt:
                        for error in error_rec:
                            errortxt.write("%s\n" % error)

                    record_message = 'Records in File:' + str(num_rows - 1) + \
                                     '  Records Uploaded: ' + str(no_rec_loaded)
                    flash(record_message)
                    flash('Membership upload Completed with error')
                    flash(msg_type + "; ckeck error log:")
                    flash(error_file)
                else:
                    record_message = 'Records in File: ' + str(num_rows - 1) + \
                                     ' Records Uploaded: ' + str(no_rec_loaded)
                    flash(record_message)
                    flash('Record upload Successful')
                return redirect(url_for('upload'))
        return redirect(url_for('upload'))
        # return render_template('uploadfile.html', form=form)

    return render_template('uploadfile.html', title="Members Upload", form=form)


@app.route("/upload_donation", methods=['GET', 'POST'])
@login_required
def upload_donation():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    form = UploadForm()
    clean_data(app.config['UPLOAD_FOLDER'], "uploaded files")  ## Clean up the upload folder
    if request.method == 'POST':
        form = UploadForm()
        uploaddir = app.config['UPLOAD_FOLDER']
        errorfolder = app.config['ERROR_FOLDER']
        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            form.file.data.save(os.path.join(uploaddir, filename))

            file_path = os.path.join(uploaddir, filename)
            name, ext = splitext(file_path)
            records = ''
            if ext in ['.xls', '.xlsx', '.csv']:
                if ext in ['.xls', '.xlsx']:
                    records = pd.read_excel(file_path, index_col=None)
                    # #print(records)
                # return 'Hellp'
                if ext == '.csv':
                    with open(file_path, 'rb') as f:
                        result = chardet.detect(f.read())
                    try:
                        records = pd.read_csv(file_path, encoding=result['encoding'])
                    except ParserError:
                        flash('Error Loading File: Check File data format')
                        return render_template('uploadfile.html', form=form)

                records.reset_index(drop=True)
                records.head(5)
                verifyheader = UploadsManager(file_path, ext, 'Donations')
                if not verifyheader.verify_header():
                    missing_field = verifyheader.missing_field
                    missing_field = pd.DataFrame(verifyheader.missing_field, columns=['Missing Fields'])
                    view_missing_file = missing_field['Missing Fields'].tolist()
                    # view_missing_file = view_missing_file_1
                    flash('File Uploaded is missing some fields')
                    return render_template('uploadfile.html', missing_fields=view_missing_file, missing=True, form=form)
                #db_path = app.config['SQLALCHEMY_DATABASE_URI']
                #engine = create_engine(db_path, echo=False)
                conn = db_conn_only()

                #engine = create_engine('postgresql+psycopg2://db_donatrack:123456@localhost:5432/donatrack_web')
                #df.to_sql('dbtable', engine, schema='dbschema', if_exists='replace')
                database_url = app.config['SQLALCHEMY_DATABASE_URI']
                url = database_url.split('postgres://')[1]
                engine = create_engine('postgresql+psycopg2://{}'.format(url), convert_unicode=True, encoding='utf8')

                msg_type = ''
                error = []
                error_rec = []
                no_member_id = []
                num_rows = len(records)
                no_rec_loaded = 0

                # Iterate one row at a time
                for i in range(num_rows):
                    try:
                        # Try inserting the row
                        donation_record = records.iloc[i:i + 1].values
                        if isfloat(donation_record[0][2]) and math.isnan(donation_record[0][2]):
                            member_id = ''
                        else:
                            member_id = donation_record[0][2].strip()

                        id_exist = Members.query.filter_by(member_id=member_id).first()
                        if id_exist is not None:
                            # print(member_id)
                            #records.iloc[i:i + 1].to_sql('Donations', con=engine, if_exists='append', index=False)
                            ## updated for Postgres SQL
                            records.iloc[i:i + 1].to_sql('Donations', con=engine, schema='public', if_exists='append',
                                                         index=False)

                            no_rec_loaded = no_rec_loaded + 1
                        else:
                            no_member_id_msg = "{} \t {}" \
                                .format(donation_record[0][0], donation_record[0][2])
                            no_member_id.append(no_member_id_msg)

                    except IntegrityError as err:
                        error = str(err.args)
                        error_rec.append(records.iloc[i:i + 1].values)
                        remove_str = ["('(sqlite3.IntegrityError)", "'", ",)"]
                        for r in remove_str:
                            if r in error:
                                error = error.replace(r, '')

                        if "NOT NULL" in error:
                            msg_type = error + "Some Field are empty"

                        if "UNIQUE" in error:
                            msg_type = error

                if len(no_member_id) > 1:
                    no_id_error = True
                    error_file_name = "donation_upload_no_member_id_error-" + datetime.now().strftime("%Y_%m_%d_%H-%S") \
                                      + ".log"
                    no_id_error_file = os.path.join(errorfolder, error_file_name)
                    f = open(no_id_error_file, 'w')
                    f.write("Error: MEMBER ID NOT IN DATABASE \r\n Donation_id\t\t  Member_ID\r\n")
                    f.close()

                    with open(no_id_error_file, 'a') as errorfile:
                        for error in no_member_id:
                            errorfile.write("%s\n" % error)
                    # flash('Data with no Member ID in database not uploaded; ckeck error log:')
                    # flash(error_file)

                if len(error_rec) > 1 or len(no_member_id) > 1:
                    error_msg = str(error)
                    error_file_name = "Donation_upload_error_" + datetime.now().strftime(
                        "%Y_%m_%d_%H-%S") + ".log"
                    error_file = os.path.join(errorfolder, error_file_name.strip(' '))
                    # return error_file

                    f = open(error_file, 'w')
                    f.write("Error: " + error + "\r\n")
                    f.close()

                    with open(error_file, 'a') as errortxt:
                        for error in error_rec:
                            errortxt.write("%s\n" % error)

                    record_message = 'Records in File: ' + str(num_rows - 1) + \
                                     ' Records Uploaded: ' + str(no_rec_loaded)
                    flash(record_message)
                    flash('Record Upload Completed with error')

                    if len(no_member_id) > 1:
                        flash('Data with no Member ID in database not uploaded; ckeck error log:')
                        flash(no_id_error_file)

                    if len(error_rec) > 1:
                        flash(msg_type + "; ckeck error log:")
                        flash(error_file)
                else:
                    record_message = 'Records in File: ' + str(num_rows - 1) + \
                                     ' Records Uploaded: ' + str(no_rec_loaded)
                    flash(record_message)
                    flash('Donations Data Upload Successful')
                return redirect(url_for('upload_donation'))

        return redirect(url_for('upload_donation'))
    return render_template('uploadfile.html', title="Donations Upload", form=form)


@app.route("/upload_group_membership", methods=['GET', 'POST'])
@login_required
def upload_group_membership():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    form = UploadForm()
    clean_data(app.config['UPLOAD_FOLDER'], "uploaded files")  ## Clean up the upload folder
    if request.method == 'POST':
        form = UploadForm()
        uploaddir = app.config['UPLOAD_FOLDER']
        errorfolder = app.config['ERROR_FOLDER']
        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            form.file.data.save(os.path.join(uploaddir, filename))

            file_path = os.path.join(uploaddir, filename)
            name, ext = splitext(file_path)
            records = ''
            if ext in ['.xls', '.xlsx', '.csv']:
                if ext in ['.xls', '.xlsx']:
                    records = pd.read_excel(file_path, index_col=None)
                    # #print(records)
                # return 'Hellp'
                if ext == '.csv':
                    with open(file_path, 'rb') as f:
                        result = chardet.detect(f.read())
                    try:
                        records = pd.read_csv(file_path, encoding=result['encoding'])
                    except ParserError:
                        flash('Error Loading File: Check File data format')
                        return render_template('uploadfile.html', form=form)

                records.reset_index(drop=True)
                # records.head(5)
                verifyheader = UploadsManager(file_path, ext, 'Groups')
                if not verifyheader.verify_header():
                    # missing_field = verifyheader.missing_field
                    missing_field = pd.DataFrame(verifyheader.missing_field, columns=['Missing Fields'])
                    view_missing_file = missing_field['Missing Fields'].tolist()
                    # view_missing_file = view_missing_file_1
                    flash('File Uploaded is missing some fields')
                    return render_template('uploadfile.html', missing_fields=view_missing_file, missing=True, form=form)

                # db_path = app.config['SQLALCHEMY_DATABASE_URI']
                # engine = create_engine(db_path, echo=False)
                ## Updated for postgres SQL
                #conn = db_conn_only()
                #engine = create_engine(conn)
                #engine = create_engine('postgresql+psycopg2://db_donatrack:123456@localhost:5432/donatrack_web')
                database_url = app.config['SQLALCHEMY_DATABASE_URI']
                url = database_url.split('postgres://')[1]
                engine = create_engine('postgresql+psycopg2://{}'.format(url), convert_unicode=True, encoding='utf8')

                msg_type = ''
                error = []
                error_rec = []
                no_member_id = []
                num_rows = len(records)
                no_rec_loaded = 0

                # Iterate one row at a time
                for i in range(num_rows):
                    try:

                        # Try inserting the row
                        print(i)
                        group_record = records.iloc[i:i + 1].values

                        if isfloat(group_record[0][1]) and math.isnan(group_record[0][1]):
                           # return 'Hello'
                            member_id = ''
                        else:
                            member_id = group_record[0][1].strip()

                        type_code = group_record[0][0].strip()
                        id_exist = Members.query.filter_by(member_id=member_id).first()
                        code_exist = id_exist = GroupType.query.filter_by(type_code=type_code).first()
                        if id_exist is not None:
                            if code_exist is not None:
                                # records.iloc[i:i + 1].to_sql('MemberGroupLink', con=engine, if_exists='append',
                                #                              index=False)
                                ## Updated for postgres SQL

                                records.iloc[i:i + 1].to_sql('MemberGroupLink', con=engine, schema='public',
                                                             if_exists='append',
                                                             index=False)
                                no_rec_loaded = no_rec_loaded + 1
                            else:
                                no_group_id_msg = "Group Code does not exist: {} \t {}" \
                                    .format(group_record[0][0], group_record[0][1])
                                no_member_id.append(no_group_id_msg)

                        else:
                            no_member_id_msg = "{} \t {}" \
                                .format(group_record[0][0], group_record[0][1])
                            no_member_id.append(no_member_id_msg)

                    except IntegrityError as err:
                        error = str(err.args)
                        error_rec.append(records.iloc[i:i + 1].values)
                        remove_str = ["('(sqlite3.IntegrityError)", "'", ",)"]
                        for r in remove_str:
                            if r in error:
                                error = error.replace(r, '')

                        if "NOT NULL" in error:
                            msg_type = error + "Some Field are empty"

                        if "UNIQUE" in error:
                            msg_type = error

                if len(no_member_id) > 1:
                    no_id_error = True
                    error_file_name = "group_upload_no_member_id_error-" + datetime.now().strftime("%Y_%m_%d_%H-%S") \
                                      + ".log"
                    no_id_error_file = os.path.join(errorfolder, error_file_name)
                    f = open(no_id_error_file, 'w')
                    f.write("Error: MEMBER ID NOT IN DATABASE \r\n type_code\t\t  Member_ID\r\n")
                    f.close()

                    with open(no_id_error_file, 'a') as errorfile:
                        for error in no_member_id:
                            errorfile.write("%s\n" % error)
                    # flash('Data with no Member ID in database not uploaded; ckeck error log:')
                    # flash(error_file)

                if len(error_rec) > 1 or len(no_member_id) > 1:
                    error_msg = str(error)
                    error_file_name = "Group_upload_error_" + datetime.now().strftime(
                        "%Y_%m_%d_%H-%S") + ".log"
                    error_file = os.path.join(errorfolder, error_file_name.strip(' '))
                    # return error_file

                    f = open(error_file, 'w')
                    f.write("Error: " + error + "\r\n")
                    f.close()

                    with open(error_file, 'a') as errortxt:
                        for error in error_rec:
                            errortxt.write("%s\n" % error)

                    record_message = 'Records in File: ' + str(num_rows - 1) + \
                                     ' Records Uploaded: ' + str(no_rec_loaded)
                    flash(record_message)
                    flash('Record Upload Completed with error')

                    if len(no_member_id) > 1:
                        flash('Data with no Member ID in database not uploaded; ckeck error log:')
                        flash(no_id_error_file)

                    if len(error_rec) > 1:
                        flash(msg_type + "; ckeck error log:")
                        flash(error_file)
                else:
                    record_message = 'Records in File: ' + str(num_rows - 1) + \
                                     ' Records Uploaded: ' + str(no_rec_loaded)
                    flash(record_message)
                    flash('Group Memersip Data Upload Successful')
                return redirect(url_for('upload_group_membership'))

        return redirect(url_for('upload_group_membership'))
    return render_template('uploadfile.html', title="Group Membership Upload", form=form)


@app.route("/export", methods=['GET'])
# @login_required
def export():
    # return excel.make_response_from_array([[1, 2], [3, 4]], "csv",
    #                                       file_name="export_data")
    download_dir = expanduser("~")
    file_path = os.path.join(download_dir, 'Downloads', 'Output_2.xlsx')
    sqlsmst = "select  Donations.donation_id, Donationtrail.donation_type_id, TypeOfDonation.type_description, " \
              " Donationtrail.payment_date, Donationtrail.amount from Donationtrail, donations,TypeOfDonation where" \
              "  Donationtrail.donation_id=Donations.Donation_id  and TypeOfDonation.type_code=" \
              "Donations.donation_type_id and Donations.member_id ='10'"
    df = pd.read_sql_query(sqlsmst, db.session.bind)
    df['payment_date'] = df.payment_date.apply(lambda x: pd.to_datetime(x).strftime('%m/%d/%Y'))
    df.rename(columns={'type_description': 'Activity Description',
                       'payment_date': 'Date of Payment',
                       'amount': 'Amount Paid'}, inplace=True)
    prn_df = df[['Activity Description', 'Amount Paid', 'Date of Payment']]
    writer = pd.ExcelWriter(file_path)
    df.to_excel(writer, 'Sheet1')
    writer.save()
    writer = pd.ExcelWriter(file_path)
    prn_df.to_excel(writer, 'Sheet1')
    writer.save()
    flash('File download complete  ' + file_path)
    return redirect(url_for('index'))


@app.route("/download_file_named_in_unicode", methods=['GET'])
@login_required
def download_file_named_in_unicode():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv",
                                          file_name=u"中文文件名")


@app.route('/download', methods=['GET'])
@login_required
def download():
    form = ReportGenaratorForm()
    # return excel.make_response_from_array([[1, 2], [3, 4]], "csv",
    #                                       file_name="export_data")
    download_dir = expanduser("~")

    if session.get('sqlstmt'):
        sqlstmt = session['sqlstmt']
        title = session['title']
    else:
        return redirect(url_for('generate_report'))

    file_name = "".join(title.split()) + "_" + "".join((datetime.now().strftime('%Y_%m_%d_%H_%S')).split("_")) + ".xlsx"
    file_path = os.path.join(download_dir, 'Downloads', file_name)

    df = pd.read_sql_query(sqlstmt, db.session.bind)
    # df = df.apply(lambda x: x.astype(str).str.title())
    # df = df.apply(lambda x: x.astype(str).str.title())
    df_no_row = df.shape[0]
    df_dict = df.to_dict()
    writer = pd.ExcelWriter(file_path)
    df.to_excel(writer, 'Sheet1')
    writer.save()
    writer = pd.ExcelWriter(file_path)
    flash('File download complete  ' + file_path)
    return redirect(url_for('generate_report'))


@app.route('/generate_report/', methods=['GET', 'POST'])
@login_required
def generate_report():
    if session["user_type"] == "admin_type":
        print(session["user_type"])
        form = ReportGenaratorForm()
        form.donation_name.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
        form.group_name.choices = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    elif session["user_type"] == "member_type":
        form =  MemberReportGenaratorForm()
        form.donation_name.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
        form.group_name.choices = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    print(session['userdata'])

    ctr = FormControl()

    if request.method == 'GET':
        return render_template('report_menu.html', form=form, ctr=ctr)

    if ctr.close.data:
        return redirect(url_for('index'))

    if ctr.submit.data:
        filter_action = ReportFilter.query.filter_by(filter_id=form.filter.data).first()
        operator = filter_action.action + " '" + form.start_field.data + "' "

        if form.report_name.data == 'RFR001':
            return redirect(url_for('redflag_report'))

        if form.report_name.data == 'PAR001':
            return redirect(url_for('payment_analysis'))

        if form.start_date.data:
            date_1 = datetime.strftime(form.start_date.data, '%Y-%m-%d')
            operator = filter_action.action + " '" + date_1 + "' "
            title = 'Donation for  Date ' + operator

        if "group_name" in request.form:
            if form.report_name.data == "MQ005":
                operator = filter_action.action + " '" + request.form['group_name'] + "' "

        if "donation_name" in request.form:
            if form.report_name.data == 'CQ001' or form.report_name.data == 'CQ005':
                operator = filter_action.action + " '" + request.form['donation_name'] + "' "

        if form.start_field.data:
            operator = filter_action.action + " '" + form.start_field.data + "' "
            title = 'Donation Amount ' + operator.replace("'", "")

        if form.start_field.data and form.filter_field.data.__contains__('amt'):
            operator = filter_action.action + form.start_field.data
            title = 'Donation Amount ' + operator.replace("'", "")

        if form.filter.data == 'btw' and form.filter_field.data.__contains__('dd'):
            if form.start_date.data and form.end_date.data:
                date_1 = datetime.strftime(form.start_date.data, '%Y-%m-%d')
                date_2 = datetime.strftime(form.end_date.data, '%Y-%m-%d')
                # return date_1 + "  " + date_2
                operator = "BETWEEN '" + date_1 + "' AND '" + date_2 + "'"
                title = 'Donations Made  ' + operator.strip("'")

            else:
                flash('BETWEEN operator requires two(2) date value')
                return redirect(url_for('generate_report'))

        elif form.filter.data == 'btw' and form.filter_field.data.__contains__('amt'):
            if form.start_field.data and form.end_field.data:
                operator = "BETWEEN " + form.start_field.data + "  AND  " + form.end_field.data
                title = 'Donation Amount ' + operator

            else:
                flash('BETWEEN operator requires two(2) value')
                return redirect(url_for('generate_report'))

        elif form.filter.data == 'btw':
            if form.start_field.data and form.end_field.data:
                operator = "BETWEEN '" + form.start_field.data + "'  AND  '" + form.end_field.data + "'"
                # title = 'Donation Amount ' + operator

            else:
                flash('BETWEEN operator requires two(2) value')
                return redirect(url_for('generate_report'))

        # flash(operator)
        report = ReportName.query.filter_by(report_id=form.report_name.data).first()
       # return report.query_stmt
        # query_stmt = (report.query_stmt.replace('"""', '').replace('\n', "")).strip()
        query_stmt = report.query_stmt.replace('"""', '')
        sqlstmt = query_stmt.format(operator.upper(), operator.upper())
        #return sqlstmt
        # return operator.upper()
        session['sqlstmt'] = sqlstmt
        session['title'] = report.report_header
        # return sqlstmt
        conn = db_conn_only()
        conn.cursor()
        print(sqlstmt)
        df = pd.read_sql_query(sqlstmt, conn)
        df = df.apply(lambda x: x.astype(str).str.title())
        ##print(df.describe())
        df_no_row = df.shape[0]
        if df_no_row == 0:
            flash('No result generated for the requested report')
            return redirect(url_for('generate_report'))

        df_dict = df.to_dict()
        return render_template('report_genarator.html', sqlstmt=sqlstmt, qry_result=df_dict, row_len=df_no_row,
                               title=report.report_header, form=form)

    return redirect(url_for('generate_report'))


@app.route('/_get_filterfield/')
@login_required
def get_filterfield():
    report_id = request.args.get('report_id', '01', type=str)
    rpt = ReportName.query.filter_by(report_id=report_id).first()
    rptFieldfilter = rpt.filterfield  # --- ReportFilterField---
    filterfields = [(row.field_id, row.filter_header) for row in rptFieldfilter]
    return jsonify(filterfields)


@app.route('/get_filterlogic/')
@login_required
def get_filterlogic():
    field_id = request.args.get('field_id', '01', type=str)
    rptfilterfields = ReportFilterField.query.filter_by(field_id=field_id).first()
    rptfilter = rptfilterfields.filterlogic  # --- ReportFilter ----
    filters = [(row.filter_id, row.description) for row in rptfilter]
    return jsonify(filters)


@app.route('/report_backend', methods=['GET', 'POST'])
@login_required
def report_backend():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    conn = db_conn_only()

    cursor = conn.cursor()
    ctr = FormControl()
    form = ReportBackendForm()
    if ctr.close.data:
        return redirect(url_for('index'))
    if ctr.cancel.data:
        return redirect(url_for('report_backend'))
    if ctr.submit.data:
        try:

            sqlstmt_1 = "INSERT INTO ReportName(report_id, report_name, report_header, query_stmt) VALUES ('" + \
                        form.report_id.data + "', '" + form.report_name.data + "', '" + form.report_header.data + \
                        "', '" + form.query_stmt.data + "');".upper()

            sqlstmt_2 = "INSERT INTO ReportFilterField(field_id, filter_field, filter_header) VALUES ('" \
                        + form.field_id.data + "', '" + form.filter_field.data + "', '" + form.filter_header.data + "');"

            sqlstmt_3 = "INSERT INTO ReportNameFilterLink(report_id, field_id) VALUES ('" + \
                        form.report_id.data + "', '" + form.field_id.data + "');".upper()

            for checked in form.action.data:
                sqlstmt_4 = "INSERT INTO ReportFieldFilterLink (field_id, filter_id) VALUES('" \
                            + form.field_id.data + "', '" + checked + "')"
                cursor.execute(sqlstmt_4)
            cursor.execute(sqlstmt_1)
            exist_in_db = ReportFilterField.query.filter_by(field_id=form.field_id.data).first()
            if not exist_in_db:
                cursor.execute(sqlstmt_2)
            cursor.execute(sqlstmt_3)
            ##conn.commit()

        except sqlite3.OperationalError as err:
            # print(err)
            flash(err)

            return render_template('report_backend.html', ctr=ctr, form=form)
        else:
            conn.commit()
        redirect(url_for('report_backend'))
    return render_template('report_backend.html', ctr=ctr, form=form)


@app.route('/add_group_member', methods=['GET', 'POST'])
@login_required
def add_group_member():
    conn = db_conn_only()
    cursor = conn.cursor()
    ctr = FormControl()
    form = GroupMemberForm()
    if session["user_type"] == "member_type":
        form.member_id.data = session['userdata']

    group_choice = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    form.group.choices = group_choice
    if ctr.cancel.data:
        return redirect(url_for('add_group_member'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if form.get_group.data:
        form.group.data.clear()
        member_detail = Members.query.filter_by(member_id=form.member_id.data.strip()).first()
        if member_detail is None:
            flash('Invalid Member ID')
            return redirect(url_for('add_group_member'))

        form.member_name.data = member_detail.member_lastname + "  " + member_detail.member_firstname
        # groups = member_detail.groups.all()
        # group_qry = "select GroupType.type_code, GroupType.type_description from GroupType, MemberGroupLink where " \
        #             "GroupType.type_code = MemberGroupLink.type_code and  MemberGroupLink.member_id='" \
        #             + form.member_id.data + "'"
        #choice_from_db = conn.execute(group_qry).fetchall()

        group_qry_stmt = """select
                           g1.type_code,
                           g1.type_description
                       from
                           public."GroupType" g1,
                           public."MemberGroupLink" gl1
                       where
                           g1.type_code = gl1.type_code
                           and gl1.member_id = '{}' """

        group_qry = group_qry_stmt.format(form.member_id.data )


        cursor.execute(group_qry)
        choice_from_db = cursor.fetchall()

        if choice_from_db is not None:
            [form.group.data.append(row[0]) for row in choice_from_db]

    if ctr.submit.data:
        del_stmt = 'DELETE FROM public."MemberGroupLink"'
        del_stmt = del_stmt + " where member_id = '" + form.member_id.data + "'"
        cursor.execute(del_stmt)
        conn.commit()
        # return sqlstmt
        try:

            for checked in form.group.data:
                conn.commit()
                ins_stmt = 'INSERT INTO public."MemberGroupLink"'
                ins_stmt = ins_stmt + "(member_id, type_code) VALUES ('" + \
                           form.member_id.data.strip() + "', '" + checked + "');".upper()
                cursor.execute(ins_stmt)
                conn.commit()
            return redirect(url_for('add_group_member'))
        except sqlite3.OperationalError as err:
            # print(err)
            flash(err)
        return render_template('group_membership.html', ctr=ctr, form=form)
    return render_template('group_membership.html', ctr=ctr, form=form)


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    if not current_user.su:
        flash('Admin right required')
        return redirect(url_for('index'))
    conn = db_conn_only()
    cursor = conn.cursor()
    ctr = FormControl()
    form = EditUserForm()
    if ctr.cancel.data:
        return redirect(url_for('edit_user'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if form.get_user.data:
        user_detail = User.query.filter_by(username=form.username.data.strip()).first()
        if user_detail is None:
            flash('User not in Database')
            return render_template('edit_user.html', ctr=ctr, form=form)

        form.fullname.data = user_detail.lastname + "  " + user_detail.firstname
        form.email.data = user_detail.email
        if int(user_detail.su) == 1:
            form.admin_option.data = "2"
        else:
            form.admin_option.data = str(int(user_detail.admin))

    if form.validate_on_submit() and ctr.submit.data:
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if form.admin_option.data == "2":
            user.su = True
            user.admin = True
        else:
            user.su = False
            user.admin = bool(int(form.admin_option.data))
        db.session.commit()
        return redirect('edit_user')

    if form.validate_on_submit() and ctr.delete.data:
        if form.username.data.strip() == current_user.username:
            flash('Cannot delete self')
            return redirect(url_for('edit_user'))
            return "Cannot delete self"
        user = User.query.filter_by(username=form.username.data.strip()).first()
        db.session.delete(user)
        db.session.commit()
        return redirect('edit_user')
    if request.method == 'GET' and request.args.get('username'):
        form.username.data = request.args.get('username')
    return render_template('edit_user.html', ctr=ctr, form=form)


@app.route('/change_member_password', methods=['GET', 'POST'])
def change_member_password():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = ChangePasswordForm()
    ctr = FormControl()

    # if current_user.is_authenticated:
    # 	form.username.data = current_user.username
    # 	user_form = False
    # else:
    # 	user_form = True
    # # if form.validate_on_submit():

    # if not session.get('userdata'):
    #     return redirect(url_for('pass_challenge'))

    if ctr.cancel.data:
        return redirect(url_for('change_member_password'))

    if ctr.close.data:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        user = Members.query.filter_by(member_id= session['userdata']).first()
        user.set_password(form.password.data)
        # print('Helooo')
        db.session.commit()
        session['userdata'] = None
        return redirect(url_for('logout'))
    else:
        return render_template('reset_password.html', ctr=ctr, form=form)
    return render_template('reset_password.html', ctr=ctr, form=form)















@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    form = ChangePasswordForm()
    ctr = FormControl()

    # if current_user.is_authenticated:
    # 	form.username.data = current_user.username
    # 	user_form = False
    # else:
    # 	user_form = True
    # # if form.validate_on_submit():

    if not session.get('userdata'):
        return redirect(url_for('pass_challenge'))

    if ctr.cancel.data:
        return redirect(url_for('change_password'))

    if ctr.close.data:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        if session["user_type"] == "Admin_type":
            user = User.query.filter_by(username=session['userdata']).first()
            user.set_password(form.password.data)
        elif session["user_type"] == "member_type":
            user = Members.query.filter_by(member_id=session['userdata']).first()
            user.set_password(form.password.data)
            # print('Helooo')
        db.session.commit()
        session['userdata'] = None
        return redirect(url_for('logout'))
    else:
        if not session.get('userdata'):
            return redirect(url_for('pass_challenge'))
        else:
            fnd = session.get('userdata')
            # return str(fnd)
            return render_template('reset_password.html', ctr=ctr, form=form)
    return render_template('reset_password.html', ctr=ctr, form=form)


@app.route('/pass_challenge', methods=['GET', 'POST'])
def pass_challenge():
    form = ChallengeForm()
    ctr = FormControl()

    if current_user.is_authenticated:
        form.username.data = current_user.username

    if ctr.cancel.data:
        if session.get('reponse1', 'found'):
            session['userdata'] = None
        return redirect(url_for('pass_challenge'))

    if ctr.close.data:
        if session.get('reponse1', 'found'):
            session['userdata'] = None
        return redirect(url_for('index'))

    if request.method == 'POST':
        # return  'ok'
        if form.validate_on_submit():
            if form.get_quest.data:
                user = User.query.filter_by(username=form.username.data).first()
                if user is not None:
                    rand_1 = randint(1, 3)
                    rand_2 = rand_1

                    while rand_1 == rand_2:
                        rand_2 = randint(1, 3)
                        if rand_2 != rand_1:
                            break

                    question = {}
                    question[1] = 'My best place in the world'
                    question[2] = 'Favorite Clothe'
                    question[3] = 'Favorite film'

                    reponse = {}
                    reponse[1] = user.challenge_1
                    reponse[2] = user.challenge_2
                    reponse[3] = user.challenge_3
                    session['reponse1'] = reponse[rand_1]
                    session['reponse2'] = reponse[rand_2]
                    # #print(session['question'][1])
                    # print(str(rand_1) + session['reponse1'])

                    # return  question[rand_1] + reponse[rand_1]
                    form.challenge_1.label.text = question[rand_1]
                    form.challenge_2.label.text = question[rand_2]
                    show = 'pass_btn'
                    return render_template('challenge.html', show=show, ctr=ctr, form=form)
                flash('Invalid Username')
                return render_template('challenge.html', ctr=ctr, form=form)
            if session.get('reponse1', 'found'):
                answer_1 = form.challenge_1.data.replace(" ", "").lower()
                answer_2 = form.challenge_2.data.replace(" ", "").lower()
                # return answer_1 + reponse[rand_1] + question[rand_1] +
                # print("ans_quest" + session['reponse1'], answer_1 + form.challenge_1.label.text)
                response_ok_1 = check_password_hash(session['reponse1'], answer_1)
                response_ok_2 = check_password_hash(session['reponse2'], answer_2)
                if response_ok_1 and response_ok_2:
                    show = 'ok'
                    session['reponse1'] = None
                    session['reponse2'] = None
                    session['userdata'] = form.username.data
                    return redirect(url_for('change_password'))
                else:
                    flash('Provide Correct answers to all the questions')
                    return redirect(url_for('pass_challenge'))
    # else:
    #     flash('Provide answers to all the questions')
    #     return render_template('reset_password.html', ctr=ctr, form=form)
    return render_template('challenge.html', ctr=ctr, form=form)


@app.route('/member_settings', methods=['GET', 'POST'])
@login_required
def member_settings():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    conn = db_conn_only()
    cursor = conn.cursor()
    ctr = FormControl()
    form = EditUserForm()
    conn = db_conn_only()
    cursor = conn.cursor()
    form.get_user.label.text = 'Get Member Detail'
    form.username.label.text = 'Member ID'
    form.admin_option.choices = [('0', 'Not Active'), ('1', 'Active')]

    if ctr.cancel.data:
        return redirect(url_for('member_settings'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if form.get_user.data:
        user_detail = Members.query.filter_by(member_id=form.username.data).first()
        if user_detail is None:
            flash('Members ID not in Database')
            return render_template('member_settings.html', ctr=ctr, form=form)

        form.fullname.data = user_detail.member_lastname + "  " + user_detail.member_firstname
        # form.email.data = user_detail.email
        form.admin_option.data = str(int(user_detail.active))

    if form.validate_on_submit() and ctr.submit.data:
        user = Members.query.filter_by(member_id=form.username.data).first()
        if user is not None:
            user.active = bool(int(form.admin_option.data))
            if bool(int(form.admin_option.data)):
                status = 'Activated'
            else:
                status = 'Deactivated'
            db.session.commit()
            flash('Member status has been {}'.format(status))
            return redirect('member_settings')

    if form.validate_on_submit and ctr.delete.data:
        user = Members.query.filter_by(member_id=form.username.data).first()
        if user is None:
            flash('Invalid User')
            return redirect('member_settings')
        member_id = user.member_id
        Msg = "All details of : {} with Membership ID: {}".format(form.fullname.data, member_id)
        user_donations = user.donation.all()
        if user_donations is not None:
            try:
                for donation in user_donations:
                    del_trail_stmt = "DELETE FROM Donationtrail  WHERE donation_id = '" + donation.donation_id + "'"
                    cursor.execute(del_trail_stmt)

                del_donations_stmt = "DELETE FROM Donations  WHERE member_id = '" + member_id + "'"
                del_from_family_member_stmt = "DELETE FROM FamilyTrail  WHERE member_id = '" + member_id + "'"
                del_member_stmt = "DELETE FROM Members  WHERE member_id = '" + member_id + "'"
                cursor.execute(del_donations_stmt)
                cursor.execute(del_from_family_member_stmt)
                cursor.execute(del_member_stmt)
                conn.commit()
                flash(Msg)
                redirect(url_for('member_settings'))
            except sqlite3.OperationalError as err:
                # print(err)
                flash(err)
                return redirect('member_settings')
    return render_template('member_settings.html', ctr=ctr, form=form)


@app.route('/edit_payment_details', methods=['GET', 'POST'])
@login_required
def edit_payment_details():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))

    # return id
    """
        List all departments    """
    form = FormControl()
    form.requiredbx.label.text = "Donation ID"
    conn = db_conn_only()
    cursor = conn.cursor()

    if form.cancel.data:
        return redirect(url_for('edit_payment_details'))
    if form.close.data:
        return redirect(url_for('index'))

    if request.method == 'POST':
        id = form.requiredbx.data
        donationid = Donations.query.filter_by(donation_id=id).first()
        if donationid is None:
            flash('No Record Found')
            return redirect(url_for('edit_payment_details'))
        qryresult = donationid.trail.all()
        if len(qryresult) > 0:
            typename = {}
            for x in qryresult:
                decription = TypeOfDonation.query.filter_by(type_code=x.donation_type_id).first()
                typename[x.donation_type_id] = decription.type_description
            donation = Donations.query.filter_by(donation_id=x.donation_id).first()
            member = Members.query.filter_by(member_id=donation.member_id).first()
            typename[x.donation_id] = member.member_firstname + ' ' + member.member_lastname

            return render_template('edit_payment_details.html', typename=typename, result=qryresult,
                                   title="Details of Payments")
        return render_template('get_payment_details.html', form=form)

    if request.method == 'GET' and request.args.get("donation_id"):
        donation_id = request.args.get("donation_id")
        try:
            del_trail_stmt = 'DELETE FROM public."Donationtrail" WHERE  donation_id= '
            del_trail_stmt = del_trail_stmt + "'" + donation_id + "'"
            cursor.execute(del_trail_stmt)
            # conn.commit()
            donation_status = UpdatePayment(donation_id, 0.0)
            if donation_status.payment_complete():
                sql_update_stmt = """UPDATE public."Donations" SET payment_status = 
                        False WHERE public."Donations".donation_id = '{}' """
                sql_update_stmt = sql_update_stmt.format(donation_id)
                return sql_update_stmt
                cursor.execute(sql_update_stmt)
            conn.commit()

        except sqlite3.OperationalError as err:
            # print(err)
            flash(err)
        return render_template('get_payment_details.html', form=form)
    return render_template('get_payment_details.html', form=form)


@app.route('/template/<path:filename>')
@login_required
def template(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=False)


# @app.route('/backup')
# @login_required
# def backup():
#     #sqlite3_backup(app.config['SQLITE_PATH'], app.config['BACKUP_FOLDER'])
#     # clean_data(args.backup_dir)
#     flash("Backup update has been successful.")
#     clean_data(app.config['BACKUP_FOLDER'], "backup files")
#     return redirect(url_for('index'))



@app.route('/backup')
@login_required
def backup():
    #sqlite3_backup(app.config['SQLITE_PATH'], app.config['BACKUP_FOLDER'])
    # clean_data(args.backup_dir)
    flash("Backup update has been successful.")
    backup_postgres_db()
    clean_data(app.config['BACKUP_FOLDER'], "backup files")
    return redirect(url_for('index'))







@app.route('/restore')
@login_required
def restore():
    if not current_user.admin:
        flash('Admin right required')
        return redirect(url_for('index'))
    root = Tk()
    root.wm_title('Donatrack')

    filename = filedialog.askopenfilename(initialdir=app.config['BACKUP_FOLDER'], title="Select file",
                                          filetypes=(("Databse Backup file", "*.db"), ("all files", "*.*")))
    root.destroy()
    ##print('file', str(filename) )
    if filename:
        # return filename
        sqlite3_restore_backup(filename, app.config['BASE_DIR'])
        flash("Backup update has been successful.")
    else:
        flash('Please choose a database file')
        return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/export_backup', methods=['GET', 'POST'])
@login_required
def export_backup():
    conn = db_conn_only()
    db_backup = 'donatrack_db_dump' + time.strftime("-%Y%m%d-%H%M%S") + '.sql'
    root = Tk()
    directory = filedialog.askdirectory()
    root.destroy()
    filename = os.path.join(directory, db_backup)
    # return filename
    export_db(conn, filename)
    return redirect(url_for('index'))


@app.route('/import_backup', methods=['GET', 'POST'])
@login_required
def import_backup():
    root = Tk()
    filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                          filetypes=(("Databse Backup file", "*.sql"), ("all files", "*.*")))
    root.destroy()
    db_name = 'donatrack.db' + time.strftime("-%Y%m%d-%H%M%S")
    restore_db_name = os.path.join(app.config['BACKUP_FOLDER'], db_name)
    if filename:
        conn = sqlite3.connect(restore_db_name)
        restore_db(conn, db_file=restore_db_name, filename=filename)
        conn.close()
        flash("database successfully imported as " + restore_db_name)
    else:
        flash('Please choose an SQL file')
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/load_data', methods=['GET', 'POST'])
@login_required
def load_data():
    if not current_user.su:
        flash('Super Admin right required')
        return redirect(url_for('index'))

    root = Tk()
    old_db_sqlite_file = app.config['OLD_DB_SQLITE_PATH']
    tables = ["Members", "MemberType", "MemberGroupLink", "GroupType", "TypeOfDonation", "Donations",
              "Donationtrail", "OwnerDetails", "PaymentType", "user"]  # Ensure the payment and user

    filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                          filetypes=(("Load SQL file", "*.sql"), ("all files", "*.*")))
    root.destroy()
    sourceDB_db_name = 'donatrack-old.db'
    restore_sourceDB = os.path.join(app.config['BACKUP_FOLDER'], sourceDB_db_name)
    if filename:
        conn = sqlite3.connect(restore_sourceDB)
        restore_db(conn, db_file=restore_sourceDB, filename=filename)
        conn.close()
        status = data_loader(old_db_sqlite_file, tables)
        if status:
            flash("database successfully imported")
        else:
            flash("Error encountered during import")
            flash("**********")
        os.remove(restore_sourceDB)
    else:
        flash('Please choose an SQL file')
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    session.clear()
    logout_user()
    shutdown_server()
    return '<h1 align="center">Application Closed <br> Thank you for using Donatrack Application</h1>'


@app.route('/support', methods=['POST', 'GET'])
def support():
    return render_template('support.html')


@app.route("/last_number")
def last_number():
    flash('Last Member ID: ' + last_member_id())
    return redirect(url_for('index'))


@app.route('/donation_receipt_pdf/<string:id>')
@login_required
def donation_receipt_pdf(id):
    path_wkhtmltopdf = app.config['WKHTMLTOPDF_FOLDER'] + '/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    # return path_wkthmltopdf
    donationid = Donations.query.filter_by(donation_id=id).first()
    donation_amt = donationid.amount
    qryresult = donationid.trail.all()
    owner_detail = OwnerDetails.query.first()
    summary = {}
    if len(qryresult) > 0:
        sum_amt_paid = 0
        typename = {}
        for x in qryresult:
            sum_amt_paid = sum_amt_paid + x.amount
            decription = TypeOfDonation.query.filter_by(type_code=x.donation_type_id).first()
            typename[x.donation_type_id] = decription.type_description
            donation = Donations.query.filter_by(donation_id=x.donation_id).first()
            member = Members.query.filter_by(member_id=donation.member_id).first()
            typename[x.donation_id] = member.member_firstname + ' ' + member.member_lastname
        balance = donation_amt - sum_amt_paid
        summary['donation_amt'] = donation_amt
        summary['sum_amt_paid'] = sum_amt_paid
        summary['balance'] = balance
        summary['timestamp'] = time.strftime("%d-%B-%Y:%H:%M")

        render = render_template('donation_details_print.html', typename=typename, result=qryresult,
                                 title="Details of Payments", summary=summary, owner_detail=owner_detail)

        filename = typename[x.donation_type_id] + "_payment_details(" + typename[x.donation_id] + ").pdf"

        pdf = pdfkit.from_string(render, False, configuration=config)
        #pdf = pdfkit.from_string(render)
        response = make_response(pdf)
        response.headers['content-type'] = 'application/pdf'
        response.headers['content-disposition'] = 'attachment; filename=' + filename
        return response


@app.route('/statement_of_account/<string:mid>')
@login_required
def statement_of_account(mid):
    path_wkhtmltopdf = app.config['WKHTMLTOPDF_FOLDER'] + '/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    connection = db_conn_only()
    conn = connection.cursor()
    sql_stmt ="""select
	t1.type_description as "Donation Name",
	d2.donation_type_ID as "Donation Code",
	to_char(d2.donation_date, 'dd-mm-yyyy') as "Donation Date",
	d2.amount as Pledged,
	coalesce(sum(d3.amount), 0) as Paid,
	d2.amount - coalesce(sum(d3.amount), 0) as Outstanding,
	m1.member_id as id,
	m1.member_Firstname || ' ' || m1.member_lastname as name,
	m1.member_phone_no as "Mobile No."
from
	public."Donations" d2
left outer join public."Donationtrail" d3 on
	d3.donation_id = d2.donation_id
left outer join public."TypeOfDonation" t1 on
	t1.type_code = d2.donation_type_id
left outer join public."Members" m1 on
	m1.member_id = d2.member_id
where
	m1.member_id = '{}'
group by
	d2.donation_date,
	d2.donation_type_id,
	t1.type_description,
	d2.amount,
	m1.member_id,
	m1.member_firstname,
	m1.member_lastname,
	m1.member_phone_no
order by
	m1.member_id"""

    query_stmt = sql_stmt.format(mid)
    #print(query_stmt)
    #return query_stmt
    #qry_result = conn.execute(query_stmt).fetchall()
    conn.execute(query_stmt)
    qry_result = conn.fetchall()
    if len(qry_result) > 0:
        summary = {}
        donation_sum = 0
        paid_sum = 0
        # print(query_result)

        for x in qry_result:
            donation_sum = donation_sum + x[3]
           # donation_sum = x[3]
            paid_sum = paid_sum + x[4]
            member_id = x[6]
            name = x[7]
        balance = donation_sum - paid_sum
        summary['donation_sum'] = donation_sum
        summary['paid_sum'] = paid_sum
        summary['balance'] = balance
        summary['member_id'] = member_id
        summary['name'] = name
        # print_date = .strftime()
        session['paydetail'] = True
    # return render_template('donation_soa_print.html', summary=summary, result=qry_result)
    return render_template('donation_member_soa.html', summary=summary, result=qry_result)


@app.route('/statement_of_account_pdf/<string:mid>')
@login_required
def statement_of_account_pdf(mid):
    path_wkhtmltopdf = app.config['WKHTMLTOPDF_FOLDER'] + '/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    conn = db_conn_only()
    cursor = conn.cursor()
    sql_stmt = """SELECT typeofdonation.type_description AS [Donation Name], Donations.donation_type_ID AS [Donation Code], 
    strftime('%d-%m-%Y',Donations.donation_date) AS [Donation Date], 
    Donations.amount AS Pledged,  IFNULL(sum(donationtrail.amount), 0) AS Paid,   
     donations.amount - IFNULL(sum(donationtrail.amount), 0)  AS Outstanding, 
     members.member_id AS id, members.member_Firstname || ' ' ||  members.member_lastname AS Name, 
    members.member_phone_no AS [Mobile No.] 
    FROM  Donations 
    OUTER LEFT JOIN donationtrail ON  donationtrail.donation_id = donations.donation_id 
    OUTER LEFT JOIN typeofdonation On typeofdonation.type_code = donations.donation_type_id 
    OUTER LEFT JOIN  members ON members.member_id = donations.member_id 
    WHERE  Members.member_id ='{}'
    group by donations.donation_type_id  
    order by members.member_id"""
    query_stmt = sql_stmt.format(mid)
    # return query_stmt
    qry_result = conn.execute(query_stmt).fetchall()
    if len(qry_result) > 0:
        # owner_detail = OwnerDetails.query.first_or_404()
        owner_detail = OwnerDetails.query.first()
        summary = {}
        donation_sum = 0
        paid_sum = 0

        # print(query_result)

        for x in qry_result:
            donation_sum = donation_sum + x[3]
            paid_sum = paid_sum + x[4]
            member_id = x[6]
            name = x[7]
        balance = donation_sum - paid_sum
        summary['donation_sum'] = donation_sum
        summary['paid_sum'] = paid_sum
        summary['balance'] = balance
        summary['member_id'] = member_id
        summary['name'] = name
        summary['timestamp'] = time.strftime("%d-%B-%Y:%H:%M")
    # return render_template('donation_soa_print.html', summary=summary, result=qry_result)
    render = render_template('donation_soa_print.html', summary=summary, result=qry_result, owner_detail=owner_detail)
    filename = "Statment of Account (" + summary['name'] + ").pdf"
    pdf = pdfkit.from_string(render, False, configuration=config)
    #pdf = pdfkit.from_string(render)
    response = make_response(pdf)
    response.headers['content-type'] = 'application/pdf'
    response.headers['content-disposition'] = 'attachment; filename=' + filename
    return response


@app.route('/ownerdetails', methods=['GET', 'POST'])
@login_required
def ownerdetails():
    if not current_user.su:
        flash('Super Admin right required')
        return redirect(url_for('index'))
    form = OwnerDetailsForm()
    ctr = FormControl()

    if ctr.cancel.data:
        return redirect(url_for('ownerdetails'))
    if ctr.close.data:
        return redirect(url_for('index'))
    if session.get('update') and session['update']:
        update_btn = True
    else:
        update_btn = False
    if request.method == 'POST' and form.validate_on_submit():
        # if OwnerDetailsForm.validate_on_submit() and ctr.submit.data:

        owner = OwnerDetails(name=form.name.data,
                             email=form.email.data,
                             address=form.address.data,
                             address1=form.address1.data,
                             lga=form.lga.data,
                             state=form.state.data,
                             phone_no=form.phone_no.data,
                             phone_no_2=form.phone_no_2.data
                             )

        # if form.delete.data:
        #     db.session.delete(owner)
        #     db.session.commit()
        #     return redirect(url_for('index.html'))
        #
        if ctr.submit.data:
            db.session.add(owner)
            db.session.commit()
            flash('Record Saved!')

        if ctr.update.data:
            dbmember = OwnerDetails.query.filter_by(id=form.id.data).first()
            dbmember.id = form.id.data
            dbmember.name = form.name.data
            dbmember.email = form.email.data
            dbmember.address = form.address.data
            dbmember.address1 = form.address1.data
            dbmember.lga = form.lga.data
            dbmember.state = form.state.data
            dbmember.phone_no = form.phone_no.data
            dbmember.phone_no_2 = form.phone_no_2.data
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('index')

    if request.method == 'GET':
        org_name = OwnerDetails.query.first()

        if org_name is not None:
            form.id.data = str(org_name.id)
            form.name.data = org_name.name
            form.email.data = org_name.email
            form.address.data = org_name.address
            form.address1.data = org_name.address1
            form.lga.data = org_name.lga
            form.state.data = org_name.state
            form.phone_no.data = org_name.phone_no
            form.phone_no_2.data = org_name.phone_no_2
            update_btn = True
            session['update'] = True
        return render_template('ownerdetails.html', form=form, ctr=ctr, update=update_btn)

    return render_template('ownerdetails.html', form=form, ctr=ctr, update=update_btn)


## -----------------   Family --------------

@app.route('/add_family_member', methods=['GET', 'POST'])
@login_required
def add_family_member():
    conn = db_conn_only()
    cursor = conn.cursor()
    ctr = FormControl()
    form = FamilyMemberForm()

    if session["user_type"] == "member_type":
        # form.member_id.data = session['userdata']
        member_family_id_result = FamilyTrail.query.filter_by(member_id=session['userdata']).first()
        if member_family_id_result is not None:
            form.family_id.data = member_family_id_result.family_id
        else:
            flash("You don't Family ID Number")
            return redirect(url_for('index'))


    def get_famliy_detail():

        """
        Ensures that only record members not in the family table(FamilyTrail) is returned for display
        :return:
        qryresultcount: the number of record returned by the query
        qryresult: result of the query,
        choices : retrieves all the type of relation available from the relation description table(FamilyRelation)
        """

        qryresult = db.session.query(Members).filter(or_(Members.member_lastname.ilike(form.family_name.data.strip()))) \
            .filter(~exists().where(FamilyTrail.member_id == Members.member_id)).order_by(
            Members.member_lastname.desc())

        qryresultcount = qryresult.count()

        choices = FamilyRelation.query.all()

        return qryresultcount, qryresult, choices

    if ctr.cancel.data:
        return redirect(url_for('add_family_member'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if request.method == "POST":
        family_id = form.family_id.data.strip().upper()
        if form.get_family.data == "" or form.family_id.data == "":
            flash('Family Name or ID Empty')
            return redirect(url_for('add_family_member'))

        if form.get_family.data and form.family_id.data.strip() != "":

            """
            Start here: get member with similiar Family name
             """
            family_id_exist = FamilyTrail.query.filter_by(family_id=family_id).first()

            qryresultcount, db_qryresult, choices = get_famliy_detail()
            #print(qryresult)

            if family_id_exist is not None and qryresultcount <= 0:
                flash("Family ID Already Exist!, \n All members with Family Name has been to assigned it.")
                return redirect(url_for('add_family_member'))

            if family_id_exist is not None:
                form.family_alert.label.text = "Family ID Already Exist!, You can only add to it."
            else:
                form.family_alert.label.text = ""

            if qryresultcount <= 0:
                flash('Family Name does not exist or it has been fully assigned to another family id ')
                return redirect(url_for('add_family_member'))

            if qryresultcount > 0:
                count = qryresultcount
               # print(count)
                record_no = 0
                record_detail = {}
                for record in db_qryresult: ## for some  weird reason the extracting index value directly did not work fine
                    #print(record)       ## so I had to read and its value on new dict object.
                    record_detail[record_no] =  record
                    record_no = record_no + 1
                #print(record_detail)
                qryresult = record_detail
                return render_template('family_membership.html', ctr=ctr, form=form, count=count, result=qryresult,
                                       choices=choices)

        if ctr.submit.data:
            count, qryresult, choices = get_famliy_detail()

            if form.family_id.data == "":
                flash('Please enter Family ID')
                # return redirect(url_for('add_family_member'))
                return render_template('family_membership.html', ctr=ctr, form=form, count=count, result=qryresult,
                                       choices=choices)

            # del_stmt = "DELETE FROM FamilyTrail where family_id = '" + form.family_id.data + "'"
            # cursor.execute(del_stmt)
            # conn.commit()

            family_member = request.form.getlist('family')
            if len(family_member) <= 0:
                flash('No Member selected')
                return render_template('family_membership.html', ctr=ctr, form=form, count=count, result=qryresult,
                                       choices=choices)

            ins_stmt = ""
            try:
                conn.commit()
                for member_id in family_member:
                    relationship = request.form.getlist(member_id)
                    member = Members.query.filter_by(member_id=member_id).first()
                    if len(relationship) <= 0:
                        flash(
                            'Record for ' + member.member_firstname + " (" + member_id + ")" + ' not saved; Reason: No Relationship selected')

                    if len(relationship) > 0:

                        for relation_id in relationship:
                            ins_stmt_1 ='INSERT INTO public."FamilyTrail" '
                            ins_stmt = ins_stmt_1 + "(family_id, member_id, family_name, relation_id) VALUES ('" + \
                                       family_id + "','" + member_id + \
                                       "','" + form.family_name.data.strip().upper() + "','" + relation_id + "');".upper()
                            #return ins_stmt

                            family_member_exist = FamilyTrail.query.filter_by(member_id=member_id).first()
                            father_exist = FamilyTrail.query.filter_by(family_id=family_id, relation_id="FA").first()
                            mother_exist = FamilyTrail.query.filter_by(family_id=family_id, relation_id="MO").first()

                            if family_member_exist is not None:
                                flash('Record Exist')
                                return redirect(url_for('add_family_member'))
                            if relation_id == "FA" and father_exist is not None:
                                flash('Record Exist for Husband(Father) for Family ID: ' + form.family_id.data.strip())
                                return redirect(url_for('add_family_member'))

                            else:
                                if relation_id == "MO" and mother_exist is not None:
                                    flash('Record Exist for Wife(Mother) for Family ID: ' + form.family_id.data.strip())
                                    return redirect(url_for('add_family_member'))

                            cursor.execute(ins_stmt)
                    conn.commit()
                    #        flash("Record Saved")
                # if check != "":
                #     flash("However Member ID: " + check + " Not saved: No Relationship Option chosen")

                return redirect(url_for('add_family_member'))
            except IntegrityError as err:
                flash(err)
            return redirect(url_for('add_family_member'))
    return render_template('family_membership.html', ctr=ctr, count=0, form=form)


## -----------------   Get Family  ID--------------

@app.route('/get_family_id', methods=['GET', 'POST'])
@login_required
def get_family_id():
    conn = db_conn_only()
    cursor = conn.cursor()
    ctr = FormControl()
    form = FamilyMemberForm()

    if session["user_type"] == "member_type":
        # form.member_id.data = session['userdata']
        member_family_id_result = FamilyTrail.query.filter_by(member_id=session['userdata']).first()
        if member_family_id_result is not None:
            form.family_id.data =  member_family_id_result.family_id
        else:
            return redirect(url_for('index'))



    def get_famliy_detail():

        """
        Returns record matching the searched family name.
        :return:
        qryresultcount: the number of record returned by the query
        qryresult: result of the query,
        choices : retrieves all the type of relation available from the relation description table(FamilyRelation)
        """

        family_array = {}

        # qryresult = db.session.query(FamilyTrail) \
        #     .filter(or_(FamilyTrail.family_name.ilike(form.family_name.data.strip()))) \
        #     .order_by(FamilyTrail.family_id.asc())




        qryresult = db.session.query(FamilyTrail) \
            .filter(or_(FamilyTrail.family_id.ilike(form.family_id.data.strip()))) \
            .order_by(FamilyTrail.family_id.asc())


        for record in qryresult:
            middlename = ""
            member = Members.query.filter_by(member_id=record.member_id).first()
            relation = FamilyRelation.query.filter_by(relation_id=record.relation_id).first()
            if (member.member_middlename is not None):
                middlename = ", " + member.member_middlename

            name = member.member_firstname + middlename
            family_array[record.member_id] = name
            family_array[record.relation_id] = relation.relation_description

        qryresultcount = qryresult.count()
        # for i in range(qryresultcount):
        #      print(qryresult[i].family_id)

        return qryresultcount, qryresult, family_array

    # --------------------end of get_famliy_detail function----------------------------

    if ctr.cancel.data:
        return redirect(url_for('get_family_id'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if request.method == "POST":

        if form.get_family.data:

            """
            Start here: get member with similiar Family name
             """

            qryresultcount, qryresult, family_array = get_famliy_detail()
            form.family_name.data = ""

            if qryresultcount <= 0:
                flash('Family Name not found family table')
                return redirect(url_for('get_family_id'))

            if qryresultcount > 0:
                # count = qryresultcount
                return render_template('get_family_id.html', ctr=ctr, form=form, result=qryresult,
                                       count=qryresultcount, family_array=family_array)

            return redirect(url_for('get_family_id'))
    return render_template('get_family_id.html', ctr=ctr, count=0, form=form)


## -----------------   Get Family  ID--------------

@app.route('/edit_family_member/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_family_member(id):
    form = FamilyMemberForm()
    ctr = FormControl()
    form.relation_id.choices = [(row.relation_id, row.relation_description) for row in FamilyRelation.query.all()]
    form.relation_id.choices.insert(0, ('', 'Select Member Type'))
    # conn = db_conn_only()
    family_id = []
    middlename = ""

    if ctr.cancel.data:
        return redirect(url_for('get_family_id'))
    if ctr.close.data:
        return redirect(url_for('index'))
    if request.method == "POST":
        dbmember = FamilyTrail.query.filter_by(member_id=id).first()

        if dbmember is not None:
            family_id.append(dbmember.family_id)
            family_id.append(dbmember.member_id)

        if ctr.delete.data:
            db.session.delete(dbmember)
            db.session.commit()
            flash('Record Deleted!')

        if form.validate_on_submit():
            if ctr.update.data:
                dbmember.family_id = form.family_id.data
                dbmember.family_name = form.family_name.data
                dbmember.relation_id = request.form['relation_id']
                db.session.commit()
                flash('Record Updated!')
            return redirect(url_for('get_family_id'))
        else:
            flash('Some Field{s} are empty')
            return render_template('edit_family_membership.html', ctr=ctr, form=form)

    if request.method == 'GET' and id:
        member_record = Members.query.filter_by(member_id=id).first()
        dbmember = FamilyTrail.query.filter_by(member_id=id).first()
        form.relation_id.choices = [(row.relation_id, row.relation_description) for row in FamilyRelation.query.all()]
        form.relation_id.choices.insert(0, ('Select Relationship', '----'))

        if (member_record.member_middlename is not None):
            middlename = ", " + member_record.member_middlename

        if dbmember:
            form.family_id.data = dbmember.family_id
            form.family_member_name.data = member_record.member_firstname + middlename
            form.family_name.data = dbmember.family_name
            form.relation_id.data = dbmember.relation_id
            return render_template('edit_family_membership.html', ctr=ctr, form=form)
        else:
            flash('No Record Found')

        # return redirect(url_for('search', module='Member'))
        return redirect(url_for('get_family_id'))


@app.route('/donatrack_validate', methods=['GET', 'POST'])
def donatrack_validate():
    form = LicenseForm()
    ctr = FormControl()
    license_path = app.config['LICENSE_FOLDER']
    if ctr.cancel.data:
        return render_template('license.html', form=form, ctr=ctr)
    if ctr.close.data:
        return redirect(url_for('index'))

    if request.method == "POST":
        if form.validate_on_submit():
            if ctr.submit.data:
                lic = ValidApp.query.first()
                if lic is not None:
                    row = ValidApp.query.get(lic.id)
                    code = form.activation_code.data.strip() + "-" + str(hex(uuid.getnode()))
                    if lic.check_license(code):
                        row.activation_code = form.activation_code.data.strip()
                        db.session.commit()
                        return redirect(url_for('index'))
                    else:
                        flash("Invalid Activation Code")
                        return render_template('license.html', form=form, ctr=ctr, license_path=license_path)

    return render_template('license.html', form=form, ctr=ctr, license_path=license_path)


@app.route('/redflag_report', methods=['GET', 'POST'])
@login_required
def redflag_report():
    form = RedFlagForm()
    ctr = FormControl()
    conn = db_conn_only()
    cursor = conn.cursor()
    path_wkhtmltopdf = app.config['WKHTMLTOPDF_FOLDER'] + '/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    donation_name = ""
    donation_year = ""
    # form.relation_id.choices = [(row.relation_id, row.relation_description) for row in FamilyRelation.query.all()]
    # form.relation_id.choices.insert(0, ('', 'Select Member Type'))
    # #conn = db_conn_only()
    # family_id = []
    middlename = ""

    form.donation_code.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    form.donation_code.choices.insert(0, ('', 'Select Donation Name'))
    ##form.group_id.choices = '

    if ctr.cancel.data:
        return redirect(url_for('redflag_report'))
    if ctr.close.data:
        return redirect(url_for('generate_report'))
    if request.method == "POST":
        stmt = """select
                    vr.name,
                    count(vr."Donation Code") as "No. of Donations Made",
                    FORMAT('%s', sum(vr.pledged)) as "Total Pledge",
                    FORMAT('%s', sum(vr.paid)) as "Total Paid",
                    FORMAT('%s', round( CAST(float8 (sum(vr.paid)* 100)/ sum(vr.pledged) as numeric), 2)) as "% Redeemed",
                    case
                        when ((sum(vr.paid)* 100)/ sum(vr.pledged) < {}) then FORMAT('RED FLAG')
                end as "RED FLAG"
                from
                    public."v_RedFlagSource" vr
                    {}
                group by
                    vr.member_id, vr.name
                order by
                    "% Redeemed" desc"""

        if form.validate_on_submit():
            if not form.redflag_mark.data.isdigit():
                flash("Redflag Marker must be a number")
                # return render_template('redflag_report.html', ctr=ctr, form=form)
                return redirect(url_for('redflag_report'))

            if form.analyze_option.data == 'one' and form.donation_code.data == "":
                flash(" This option requires you choose a donation name")
                # return render_template('redflag_report.html', ctr=ctr, form=form)
                return redirect(url_for('redflag_report'))

            if form.analyze_option.data == 'one':
                where = 'Where vr."Donation Code" ='
                where = where + "'" + form.donation_code.data + "'"
                donation_rec = TypeOfDonation.query.filter_by(type_code=form.donation_code.data).first()
                donation_name = donation_rec.type_description
                stmt = stmt.format(form.redflag_mark.data, where)
                # print(stmt)

            if form.analyze_option.data == 'year' and form.analyze_year.data == "":
                flash("This option requires you enter a year")
                # return render_template('redflag_report.html', ctr=ctr, form=form)
                return redirect(url_for('redflag_report'))

            if form.analyze_option.data == 'year':
                #where = "where strftime('%Y', [Donation Date])='" + form.analyze_year.data + "'"

                where = """where cast(date_part('year', vr."Donation Date") as character(4)) = '{}' """
                where = where.format(form.analyze_year.data)

                # return 'Year'# where strftime("%Y", [Donation Date]) ='2015'
                donation_year = form.analyze_year.data
                stmt = stmt.format(form.redflag_mark.data, where)
                # return stmt
            else:
                stmt = stmt.format(form.redflag_mark.data, "")

            print(stmt)
            cursor.execute(stmt)
            result = cursor.fetchall()
            if len(result) <= 0:
                flash("No Record Found")
                return render_template('redflag_report.html', ctr=ctr, form=form)

            print_time = time.strftime("%d-%B-%Y:%H:%M")

            if form.btnview.data:
                return render_template('redflag_print.html', ctr=ctr, form=form, print_time=print_time,
                                       donation_name=donation_name, donation_year=donation_year, result=result)

            if form.btnprint.data:
                render = render_template('redflag_print.html', ctr=ctr, form=form, print_time=print_time,
                                         donation_name=donation_name, donation_year=donation_year, result=result)

                pdf = pdfkit.from_string(render, False, configuration=config)
                response = make_response(pdf)
                response.headers['content-type'] = 'application/pdf'
                response.headers['content-disposition'] = 'attachment; filename=REDFLAG REPORT.PDF'
                return response
            if form.btndownload.data:
                download_dir = expanduser("~")

                file_name = donation_name + " Red Flag Report " + "_" + "".join(
                    (datetime.now().strftime('%Y_%m_%d_%H_%S')).split("_")) + ".xlsx"
                file_path = os.path.join(download_dir, 'Downloads', file_name)

                df = pd.read_sql_query(stmt, db.session.bind)

                df_no_row = df.shape[0]
                df_dict = df.to_dict()
                writer = pd.ExcelWriter(file_path)
                df.to_excel(writer, 'Sheet1')
                writer.save()
                writer = pd.ExcelWriter(file_path)
                flash('File download complete  ' + file_path)
                return redirect(url_for('redflag_report'))
            # return render_template('redflag_report.html', ctr=ctr, form=form, result=result)

    return render_template('redflag_report.html', ctr=ctr, form=form)


@app.route('/payment_analysis', methods=['GET', 'POST'])
@login_required
def payment_analysis():
    form = PaymentAnalysisForm()
    ctr = FormControl()
    conn = db_conn_only()
    cursor = conn.cursor()
    path_wkhtmltopdf = app.config['WKHTMLTOPDF_FOLDER'] + '/wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    donation_name = ""
    donation_year = ""
    header = []
    result_size = 0

    form.donation_code.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    form.donation_code.choices.insert(0, ('', 'Select Donation Name'))
    ##form.group_id.choices = '

    if ctr.cancel.data:
        return redirect(url_for('payment_analysis'))
    if ctr.close.data:
        return redirect(url_for('generate_report'))

    if request.method == "POST":
        inner_stmt = '( select name,[Donation Name], count([Donation Name]) AS [No. Of Donations Made],' \
                     '  sum(v_RedFlagSource.pledged) AS [Total Pledge] ,' \
                     '  sum(v_RedFlagSource.paid)  AS [Total Paid], ' \
                     ' printf("%.2f",(sum(v_RedFlagSource.paid)*100)/sum(v_RedFlagSource.pledged)) AS [percentRedeemed]  ' \
                     'from v_RedFlagSource {}  ' \
                     'group by v_RedFlagSource.member_id' \
                     ' order by  [percentRedeemed] DESC )'
        inner_stmt ="""(
                        select
                            vr.name,
                            vr."Donation Name",
                            count(vr."Donation Name") as "No. of Donations Made",
                            sum(vr.pledged) as "Total Pledge" ,
                            sum(vr.paid) as "Total Paid",
                            FORMAT('%s',(sum(vr.paid)* 100)/ sum(vr.pledged)) as percentRedeemed
                        from
                            public."v_RedFlagSource" vr
                        {}
                        group by
                            vr.member_id, vr."name",vr."Donation Name"
                        order by
                            percentRedeemed desc ) as pledges"""
        # return inner_stmt

        if form.analyze_interval.data == "10":
            stmt =  """ select
                    count(case when (percentRedeemed between '0' and '0.00001')then 1 else null end) as "zero_payment",
                    count(case when (percentRedeemed between '0' and '10')then 1 else null end) as "1 -10 %",
                    count(case when (percentRedeemed between '11' and '20')then 1 else null end) as "11 - 20 %",
                    count(case when (percentRedeemed between '21' and '30')then 1 else null end) as "21 - 30 %",
                    count(case when (percentRedeemed between '31' and '40')then 1 else null end) as "31 - 40 %",
                    count(case when (percentRedeemed between '41' and '50')then 1 else null end) as "41 - 50 %",
                    count(case when (percentRedeemed between '51' and '60')then 1 else null end) as "51 - 60 %",
                    count(case when (percentRedeemed between '61' and '70')then 1 else null end) as "61 - 70 %",
                    count(case when (percentRedeemed between '71' and '80')then 1 else null end) as "71 - 80 %",
                    count(case when (percentRedeemed between '81' and '90')then 1 else null end) as "81 - 90 %",
                    count(case when (percentRedeemed between '91' and '100')then 1 else null end) as "91 - 100 %",
                    count(case when (percentRedeemed between '100' and '101')then 1 else null end) as "Completed" """

            header = '[ 0 %]', '[ 0 - 10 %]', '[ 11 - 20 %]', '[ 21 - 30 %]', '[ 31 - 40 %]', '[ 41 - 50 %]', \
                     '[ 51 - 60 %]', '[ 61 - 70 %]', '[ 71 - 80 %]', '[ 81 - 90 %]', '[ 91 - 100 %]', '[ 100% ]'
            result_size = 12

        if form.analyze_interval.data == "20":
            stmt = """select
                    count(case when (percentRedeemed between '0' and '0.00001')then 1 else null end) as "zero_payment",
                    count(case when (percentRedeemed between '0' and '20')then 1 else null end) as "0 - 20 %",
                    count(case when (percentRedeemed between '21' and '40')then 1 else null end) as "21 - 40 %",
                    count(case when (percentRedeemed between '41' and '60')then 1 else null end) as "41 - 60 %",
                    count(case when (percentRedeemed between '61' and '80')then 1 else null end) as "61 - 80 %",
                    count(case when (percentRedeemed between '81' and '100')then 1 else null end) as "81 - 100 %",
                    count(case when (percentRedeemed between '100' and '101')then 1 else null end) as "Completed" """

            header = '[ 0 %]', '[ 0 - 20 %]', '[ 21 - 40 %]', '[ 41 - 60 %]', '[ 61 - 80 %]', '[ 81 - 100 %]', '[ 100 %]'

            result_size = 7

        if form.analyze_interval.data == "25":
            stmt ="""select
                    count(case when (percentRedeemed between '0' and '0.00001')then 1 else null end) as "zero_payment",
                    count(case when (percentRedeemed between '0' and '25')then 1 else null end) as "0 - 25 %",
                    count(case when (percentRedeemed between '26' and '50')then 1 else null end) as "26 - 50 %",
                    count(case when (percentRedeemed between '51' and '75')then 1 else null end) as "51 - 75 %",
                    count(case when (percentRedeemed between '76' and '101')then 1 else null end) as "76 - 100 %",
                    count(case when (percentRedeemed between '100' and '101')then 1 else null end) as "Completed" """

            header = '[ 0 %]', '[ 0 - 25 %]', '[ 26 - 50 %]', '[ 51 - 75 %]', '[ 76 - 100 %]', '[ 100 %]'

            result_size = 6

        if form.analyze_option.data == 'one' and form.donation_code.data == "":
            flash(" This option requires you choose a donation name")
            # return render_template('redflag_report.html', ctr=ctr, form=form)
            return redirect(url_for('payment_analysis'))

        if form.analyze_option.data == 'one':
            where = "Where [Donation Code]='" + form.donation_code.data + "'"
            where = """where  vr."Donation Code" = '{}'"""
            where = where.format(form.donation_code.data)
            donation_rec = TypeOfDonation.query.filter_by(type_code=form.donation_code.data).first()
            donation_name = donation_rec.type_description
            inner_stmt = inner_stmt.format(where)
            # print(stmt)

        if form.analyze_option.data == 'year' and form.analyze_year.data == "":
            flash("This option requires you enter a year")
            # return render_template('redflag_report.html', ctr=ctr, form=form)
            return redirect(url_for('payment_analysis'))

        if form.analyze_option.data == 'year':
            where = """where  cast(date_part('year', vr."Donation Date") as character(4)) = '{}'"""
            #where = "where strftime('%Y', [Donation Date])='" + form.analyze_year.data + "'"
            where = where.format(form.analyze_year.data)
            # return 'Year'# where strftime("%Y", [Donation Date]) ='2015'
            donation_year = form.analyze_year.data
            inner_stmt = inner_stmt.format(where)
            # return stmt
        else:
            inner_stmt = inner_stmt.format("")

        final_stmt = stmt + " from " + inner_stmt

        #return final_stmt

        #stmt_qry = cursor.execute(final_stmt)
        cursor.execute(final_stmt)
        result = cursor.fetchall()
        print(result)
        if len(result) <= 0:
            flash("No Record Found")
            return render_template('payment_analysis.html', ctr=ctr, form=form)

        print_time = time.strftime("%d-%B-%Y:%H:%M")

        if form.btnview.data:
            return render_template('payment_analysis_print.html', ctr=ctr, form=form, print_time=print_time,
                                   donation_name=donation_name, donation_year=donation_year, result=result,
                                   header=header, result_size=result_size)

        if form.btnprint.data:
            render = render_template('payment_analysis_print.html', ctr=ctr, form=form, print_time=print_time,
                                     donation_name=donation_name, donation_year=donation_year, result=result,
                                     header=header, result_size=result_size)

            pdf = pdfkit.from_string(render, False, configuration=config)
            response = make_response(pdf)
            response.headers['content-type'] = 'application/pdf'
            response.headers['content-disposition'] = 'attachment; filename=PAYMENT ANALYSIS REPORT.PDF'
            return response
        if form.btndownload.data:
            download_dir = expanduser("~")

            file_name = donation_name + " Red Flag Report " + "_" + "".join(
                (datetime.now().strftime('%Y_%m_%d_%H_%S')).split("_")) + ".xlsx"
            file_path = os.path.join(download_dir, 'Downloads', file_name)

            conn.cursor()

            df = pd.read_sql_query(final_stmt, conn)

            df_no_row = df.shape[0]
            df_dict = df.to_dict()
            writer = pd.ExcelWriter(file_path)
            df.to_excel(writer, 'Sheet1')
            writer.save()
            writer = pd.ExcelWriter(file_path)
            flash('File download complete  ' + file_path)
            return redirect(url_for('payment_analysis'))
    # return render_template('redflag_report.html', ctr=ctr, form=form, result=result)

    return render_template('payment_analysis.html', ctr=ctr, form=form)

@app.route('/member_self_edit', methods=['GET', 'POST'])
@login_required
def member_self_edit():

    look_for = format(session['userdata'])
    dbmember = db.session.query(Members).filter(or_(Members.member_id == look_for.lower(),
                                                    Members.member_id == look_for.upper())).first()
    if dbmember:
        return redirect(url_for('edit_member', id=dbmember.member_id))
    else:
        return redirect(url_for('index'))

@app.route('/member_self_donate', methods=['GET', 'POST'])
@login_required
def member_self_donate():
    look_for = format(session['userdata'])
    session['searchstr'] = look_for

    return redirect(url_for('donations', mid=session['userdata']))

@app.route('/member_self_statement', methods=['GET', 'POST'])
@login_required
def member_self_statement():
    look_for = format(session['userdata'])
    session['searchstr'] = look_for
    isdata, qryresult, typename = Search(look_for).donation_id_option()
    if isdata:
        return render_template('donation_search_by_id_result.html', typename=typename, module='member_self',
                                           result=qryresult, title="Search Result")
    else:
        return redirect(url_for('index'))

