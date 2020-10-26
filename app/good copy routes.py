# coding: utf-8
from os.path import splitext, expanduser
from random import randint
from tkinter import *
from tkinter import filedialog

import flask_excel as excel
from flask import render_template, redirect, url_for, session, send_from_directory
from flask.json import jsonify
from flask_login import current_user, login_user, logout_user, login_required
from pandas.errors import ParserError
from sqlalchemy import create_engine
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
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if process_exists('run.exe'):
    #     raise SystemExit

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.reset_password.data:
        return redirect(url_for('pass_challenge'))

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
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
        user = User(username=form.username.data,
                    email=form.email.data,
                    admin=form.admin.data,
                    su=form.su.data,
                    lastname=form.lastname.data,
                    firstname=form.firstname.data
                    # challenge_1=form.challenge_1.data.replace(" ", ""),
                    # challenge_2=form.challenge_2.data.replace(" ", ""),
                    # challenge_3=form.challenge_3.data.replace(" ", "")
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
                mod = ModeOfDonation(mode_description=form.description.data.upper(), mode_code=form.code.data.upper())
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
            is_user_in_db = Members.query.filter_by(member_id=form.id.data).first()
            if is_user_in_db:
                flash('Member ID Exist')
                return render_template('member.html', title='Add New Member', ctr=ctr, form=form)

            sqlstmt_1 = "INSERT INTO Members(member_id, member_type_ID, member_lastname, member_firstname," \
                        " member_middlename,  member_address,   member_address1,  member_email, " \
                        "member_phone_no ) VALUES(  '" + form.id.data + "' ,'" + form.type_id.data \
                        + "' ,'" + form.lastname.data + "' ,'" + form.firstname.data + "' ,'" + form.middlename.data + \
                        "' ,'" + form.address.data + "' ,'" + form.address1.data + "' ,'" + form.email.data + "' ,'" \
                        + form.phone_no.data + "');"
            # return sqlstmt_1
            # cursor.execute(sqlstmt_1)

            try:
                multiselect = request.form.getlist('group_id')
                for item in multiselect:
                    sqlstmt = "SELECT * FROM MemberGroupLink WHERE  member_id ='" \
                              + form.id.data + "' AND  type_code ='" + item + "'"
                    if cursor.execute(sqlstmt).fetchone() is None:
                        sql_insert_stmt = "INSERT INTO MemberGroupLink(member_id, type_code) VALUES ('" + \
                                          form.id.data + "', '" + item + "');".upper()
                        cursor.execute(sql_insert_stmt)
                ##db.session.add(detail)
                # db.session.commit()
                cursor.execute(sqlstmt_1)
                conn.commit()
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
    searchform = SearchForm()
    if ctr.cancel.data:
        return redirect(url_for('search', module='Member'))
    if ctr.close.data:
        return redirect(url_for('index'))
    if request.method == "POST":
        # return request.form['sid']
        # dbmember = Members.query.get_or_404(id)
        dbmember = Members.query.filter_by(member_id=id).first()
        if ctr.delete.data:
            db.session.delete(dbmember)
            db.session.commit()
            # return request.form['type_id']
        form.type_id.choices = [(row.type_code, row.type_description) for row in MemberType.query.all()]
        form.type_id.choices.insert(0, ('', 'Select Member Type'))
        form.group_id.choices = [(row.type_code, row.type_description) for row in GroupType.query.all()]

        if form.validate_on_submit():
            if ctr.update.data:
                dbmember.member_id = form.id.data
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
                    sql_delete = "DELETE FROM MemberGroupLink  WHERE  member_id = '" + form.id.data + "'"
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
            return redirect(url_for('search', module='Member'))
        else:
            flash('Some Field{s} are empty')
            return render_template('edit_member.html', title='Edit Member Details', action="edit", ctr=ctr, form=form)
    # return redirect(url_for('search'))

    if request.method == 'GET' and id:
        # return id
        dbmember = Members.query.filter_by(member_id=id).first()
        form.type_id.choices = [(row.type_code, row.type_description) for row in MemberType.query.all()]
        form.type_id.choices.insert(0, ('Select Member Type', '----'))

        group_qry = "select GroupType.type_code, GroupType.type_description from GroupType, MemberGroupLink where " \
                    "GroupType.type_code = MemberGroupLink.type_code and  MemberGroupLink.member_id='" \
                    + dbmember.member_id + "'"
        choice_from_db = conn.execute(group_qry).fetchall()
        form.group_id.choices = [(row[0], row[1]) for row in choice_from_db]

        if dbmember:
            form.sid = dbmember.sid
            form.id.data = dbmember.member_id
            form.type_id.data = dbmember.member_type_ID
            # form.group_id.data = dbmember.member_group_id
            form.lastname.data = dbmember.member_lastname
            form.firstname.data = dbmember.member_firstname
            form.middlename.data = dbmember.member_middlename
            form.address.data = dbmember.member_address
            form.address1.data = dbmember.member_address1
            form.email.data = dbmember.member_email
            form.phone_no.data = dbmember.member_phone_no
            return render_template('edit_member.html', title='Edit Member Details', action="edit", ctr=ctr, form=form)
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
                donation_mode_id=form.mode_id.data
                # payment_type_id = form.payment_type_id.data
            )
            if ctr.submit.data:
                db.session.add(detail)
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
                    sql_update_stmt = "UPDATE Donations SET donation_id = '" + form.donation_id.data \
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
                    sql_update_child = "UPDATE Donationtrail SET donation_id = '" + form.donation_id.data + \
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


@app.route('/edit_donation/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_donation(id):
    form = DonationForm()
    ctr = FormControl()
    conn = db_conn_only()
    cursor = conn.cursor()
    searchform = SearchForm()
    if ctr.cancel.data:
        return redirect(url_for('search', module='Member'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if request.method == 'GET' and id:
        # return id
        dbmember = Donations.query.filter_by(donation_id=id).first()
        mid = dbmember.donor.member_id
        form.donation_type_id.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
        form.mode_id.choices = [(row.mode_code, row.mode_description) for row in ModeOfDonation.query.all()]

        user_in_db = Members.query.filter_by(member_id=mid).first()
        if user_in_db:
            form.member_name.data = user_in_db.member_lastname + " ," + user_in_db.member_firstname

        if dbmember:
            form.donation_id.data = dbmember.donation_id
            session['old_donation_id'] = dbmember.donation_id
            return session['old_donation_id']
            form.donation_type_id.data = dbmember.donation_type_id
            form.member_id.data = dbmember.member_id
            form.date.data = dbmember.donation_date
            form.amount.data = float(dbmember.amount)
            # return 'Hello' + str(form.amount.data)
            form.mode_id.data = dbmember.donation_mode_id
            form.comment.data = dbmember.comment
        return render_template('donation.html', title='Edit Donation Details', action="edit", ctr=ctr, form=form)

    return redirect(url_for('search', module='Donation'))


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
                mod = TypeOfDonation(type_description=form.description.data.upper(), type_code=form.code.data.upper())
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
            mode.type_code = form.code.data.upper()
            # db.session.add(mod)
            db.session.commit()
            flash('Record Update Sucessful!')

        return redirect('typeofdonation')

    if request.method == 'GET' and id:
        mode = TypeOfDonation.query.filter_by(type_id=id).first()
        form.code.data = mode.type_code
        form.description.data = mode.type_description
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
                mod = PaymentType(type_description=form.description.data.upper(), type_code=form.code.data.upper())
                db.session.add(mod)
                db.session.commit()
                flash('Record Added!')
                return redirect(url_for('moderedemption'))
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
                mod = MemberType(type_description=form.description.data.upper(), type_code=form.code.data.upper())
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
                mod = GroupType(type_description=form.description.data.upper(), type_code=form.code.data.upper())
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
    print(list_mod)
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
        form.get_module.data = module
        flash(form.get_module.data)
    if request.method == "POST" and form.validate_on_submit():
        look_for = '%{0}%'.format(form.src_string.data)
        session['searchstr'] = form.src_string.data
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
            flash(str(total_paid))
            update = UpdatePayment(form.donation_id.data, form.amount.data).payment_complete()
            # flash(update)
            if update:
                # return 'OK'
                status_ok = Donations.query.filter_by(donation_id=form.donation_id.data).first()
                # return 'OK'
                status_ok.payment_status = 1
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
            flash('Record Updated!')

            if session.get('searchstr_name'):
                return redirect(url_for('search', module='Donation'))
                # return render_template('donation_search_by_name_result.html',
                #                        result=qryresult, typename=typename, title="Search Result", module='Donation')
            else:
                if session['searchstr_option'] == 'name_option':
                    return render_template('donation_search_by_name_result.html', typename=typename, module='Donation',
                                           result=qryresult, title="Search Result")
                if session['searchstr_option'] == 'name_option':
                    return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                           result=qryresult, title="Search Result")
        else:
            return render_template('donation_payment.html', title='New Donation', ctr=ctr, form=form)

    if request.method == 'GET' and request.args.get('id'):
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
        return render_template('donation_search_by_id_result.html', typename=typename, module='Donation', result=qryresult,
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
    if session.get('paydetail'):
        look_for = '%{0}%'.format(session['searchstr'])
        if session.get('searchstr_option') and session['searchstr_option'] == 'name_option':
            look_for = '%{0}%'.format(session['searchstr'])
            isdata, qryresult, typename = Search(look_for).donation_name_option()
            # print(isdata, qryresult, typename)
            if isdata:
                session['paydetail'] = None
                return render_template('donation_search_by_name_result.html',
                                       result=qryresult, typename=typename, title="Search Result",
                                       module='Donation')
        elif session.get('searchstr_option') and session['searchstr_option'] == 'id_option':
            isdata, qryresult, typename = Search(look_for).donation_id_option()
            # print(isdata, qryresult, typename)
            if isdata:
                session['paydetail'] = None
                return render_template('donation_search_by_id_result.html', typename=typename, module='Donation',
                                       result=qryresult, title="Search Result")
            return redirect(url_for('search', module='Donation'))

    donationid = Donations.query.filter_by(donation_id=id).first()
    qryresult = donationid.trail.all()

    if len(qryresult) > 0:
        typename = {}
        for x in qryresult:
            decription = TypeOfDonation.query.filter_by(type_code=x.donation_type_id).first()
            typename[x.donation_type_id] = decription.type_description
            donation = Donations.query.filter_by(donation_id=x.donation_id).first()
            member = Members.query.filter_by(member_id=donation.member_id).first()
            typename[x.donation_id] = member.member_firstname + ' ' + member.member_lastname
        session['paydetail'] = True
        return render_template('donation_details.html', typename=typename, result=qryresult,
                               title="Details of Payments")
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
                    print(records)

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
                db_path = app.config['SQLALCHEMY_DATABASE_URI']
                engine = create_engine(db_path, echo=False)
                error = []
                error_rec = []
                num_rows = len(records)
                no_rec_loaded = 0
                # Iterate one row at a time
                for i in range(num_rows):
                    try:
                        # Try inserting the row

                        records.iloc[i:i + 1].to_sql('Members', con=engine, if_exists='append', index=False)
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

                    record_message = 'Records in File:' + str(num_rows-1) +\
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
                db_path = app.config['SQLALCHEMY_DATABASE_URI']
                engine = create_engine(db_path, echo=False)
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
                        member_id = donation_record[0][2]
                        id_exist = Members.query.filter_by(member_id=member_id).first()
                        if id_exist is not None:
                            # print(member_id)
                            records.iloc[i:i + 1].to_sql('Donations', con=engine, if_exists='append', index=False)
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

                if len(error_rec) > 1 or no_member_id:
                    error_msg = error
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

                    if no_member_id:
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
    df = df.apply(lambda x: x.astype(str).str.title())
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
    form = ReportGenaratorForm()
    ctr = FormControl()

    if request.method == 'GET':
        return render_template('report_menu.html', form=form, ctr=ctr)

    if ctr.close.data:
        return redirect(url_for('index'))

    if ctr.submit.data:
        filter_action = ReportFilter.query.filter_by(filter_id=form.filter.data).first()
        operator = filter_action.action + " '" + form.start_field.data + "' "

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

        if form.filter.data == 'btw' and form.filter_field.data.__contains__('amt'):
            if form.start_field.data and form.end_field.data:
                operator = "BETWEEN " + form.start_field.data + "  AND  " + form.end_field.data
                title = 'Donation Amount ' + operator

            else:
                flash('BETWEEN operator requires two(2) value')
                return redirect(url_for('generate_report'))

        # flash(operator)
        report = ReportName.query.filter_by(report_id=form.report_name.data).first()
        query_stmt = (report.query_stmt.replace('"""', '').replace('\n', "")).strip()
        sqlstmt = query_stmt.format(operator.upper(), operator.upper())
        # return sqlstmt
        # return operator.upper()
        session['sqlstmt'] = sqlstmt
        session['title'] = report.report_header
        # return sqlstmt
        df = pd.read_sql_query(sqlstmt, db.session.bind)
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
            conn.commit()

        except sqlite3.OperationalError as err:
            # print(err)
            flash(err)
            return render_template('report_backend.html', ctr=ctr, form=form)
        redirect(url_for('report_backend'))
    return render_template('report_backend.html', ctr=ctr, form=form)


@app.route('/add_group_member', methods=['GET', 'POST'])
@login_required
def add_group_member():
    conn = db_conn_only()
    cursor = conn.cursor()
    ctr = FormControl()
    form = GroupMemberForm()
    group_choice = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    form.group.choices = group_choice
    if ctr.cancel.data:
        return redirect(url_for('add_group_member'))
    if ctr.close.data:
        return redirect(url_for('index'))

    if form.get_group.data:
        form.group.data.clear()
        member_detail = Members.query.filter_by(member_id=form.member_id.data).first()
        if member_detail is None:
            flash('Invalid Member ID')
            return redirect(url_for('add_group_member'))

        form.member_name.data = member_detail.member_lastname + "  " + member_detail.member_firstname
        # groups = member_detail.groups.all()
        group_qry = "select GroupType.type_code, GroupType.type_description from GroupType, MemberGroupLink where " \
                    "GroupType.type_code = MemberGroupLink.type_code and  MemberGroupLink.member_id='" \
                    + form.member_id.data + "'"
        choice_from_db = conn.execute(group_qry).fetchall()
        if choice_from_db is not None:
            [form.group.data.append(row[0]) for row in choice_from_db]

    if ctr.submit.data:

        del_stmt = "DELETE FROM MemberGroupLink where member_id = '" + form.member_id.data + "'"
        cursor.execute(del_stmt)
        conn.commit()
        # return sqlstmt
        try:

            for checked in form.group.data:
                conn.commit()
                ins_stmt = "INSERT INTO MemberGroupLink(member_id, type_code) VALUES ('" + \
                           form.member_id.data + "', '" + checked + "');".upper()
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
        user_detail = User.query.filter_by(username=form.username.data).first()
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
        user = User.query.filter_by(username=form.username.data).first()
        if form.admin_option.data == "2":
            user.su = True
            user.admin = True
        else:
            user.su = False
            user.admin = bool(int(form.admin_option.data))
        db.session.commit()
        return redirect('edit_user')

    if form.validate_on_submit() and ctr.delete.data:
        if form.username.data == current_user.username:
            flash('Cannot delete self')
            return redirect(url_for('edit_user'))
            return "Cannot delete self"
        user = User.query.filter_by(username=form.username.data).first()
        db.session.delete(user)
        db.session.commit()
        return redirect('edit_user')
    if request.method == 'GET' and request.args.get('username'):
        form.username.data = request.args.get('username')
    return render_template('edit_user.html', ctr=ctr, form=form)


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
        user = User.query.filter_by(username=session['userdata']).first()
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
                sttus = 'Activated'
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
                del_member_stmt = "DELETE FROM Members  WHERE member_id = '" + member_id + "'"
                cursor.execute(del_donations_stmt)
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

    if request.method == 'GET' and request.args.get("donation_sid"):
        donation_sid = request.args.get("donation_sid")
        donation_id = request.args.get("donation_id")
        try:
            del_trail_stmt = "DELETE FROM Donationtrail WHERE id = '" + donation_sid + "'"
            cursor.execute(del_trail_stmt)
            # conn.commit()
            donation_status = UpdatePayment(donation_id, 0.0)
            if donation_status.payment_complete():
                sql_update_stmt = "UPDATE Donations SET payment_status = 0 WHERE donation_id = '" + donation_id + "'"
                cursor.execute(sql_update_stmt)
            conn.commit()

        except sqlite3.OperationalError as err:
            # print(err)
            flash(err)
        return render_template('get_payment_details.html', form=form)
    return render_template('get_payment_details.html', form=form)


@app.route('/template/<path:filename>')
# @login_required
def template(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
                               filename, as_attachment=False)


@app.route('/backup')
# @login_required
def backup():
    sqlite3_backup(app.config['SQLITE_PATH'], app.config['BACKUP_FOLDER'])
    # clean_data(args.backup_dir)
    clean_data(app.config['BACKUP_FOLDER'])
    flash("Backup update has been successful.")
    return redirect(url_for('index'))


@app.route('/restore')
# @login_required
def restore():
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
def export_backup():
    conn = db_conn_only()
    db_backup = 'donatrack_db_dump' + time.strftime("-%Y%m%d-%H%M%S") + '.sql'
    root = Tk()
    directory = filedialog.askdirectory()
    root.destroy()
    filename = os.path.join(directory, db_backup)
    # return filename
    dump_to_file(conn, filename)
    return redirect(url_for('index'))


@app.route('/import_backup', methods=['GET', 'POST'])
def import_backup():
    root = Tk()
    filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                          filetypes=(("Databse Backup file", "*.sql"), ("all files", "*.*")))
    root.destroy()
    # restore_path = app.config['BACKUP_FOLDER'] + 'donatrack' + time.strftime("-%Y%m%d-%H%M%S") + '.db'
    db_name = 'donatrack' + time.strftime("-%Y%m%d-%H%M%S") + '.db'
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


@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    session.clear()
    logout_user()
    shutdown_server()
    return '<h1 align="center">Application Closed <br> Thank you for using Donatrack Application</h1>'


@app.route("/last_number")
def last_number():
    flash('Last Member ID: ' + last_member_id())
    return redirect(url_for('index'))
