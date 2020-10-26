import base64
import os
import random
import sqlite3
import psycopg2
import subprocess
import time
import uuid
from datetime import datetime

import chardet
import pandas as pd
from flask import request, flash, session
from flask_login import UserMixin
from pip._vendor.distlib._backport import shutil
from sqlalchemy import UniqueConstraint, func
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from app import db, login
from app.reports import db_conn_only


@login.user_loader
def load_user(id):
    if session["user_type"] == "admin_type":
        return User.query.get(int(id))
    else:
        if session["user_type"] == "member_type":
            return Members.query.get(int(id))


class User(UserMixin, db.Model):
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_challenge_1(self, challenge_1):
        self.challenge_1 = generate_password_hash(challenge_1)

    def check_challenge_1(self, challenge_1):
        return check_password_hash(self.challenge_1, challenge_1)

    def set_challenge_2(self, challenge_2):
        self.challenge_2 = generate_password_hash(challenge_2)

    def check_challenge_2(self, challenge_2):
        return check_password_hash(self.challenge_2, challenge_2)

    def set_challenge_3(self, challenge_3):
        self.challenge_3 = generate_password_hash(challenge_3)
        return self.challenge_3

    def check_challenge_3(self, challenge_3):
        return check_password_hash(self.challenge_3, challenge_3)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    lastname = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean(), nullable=False)
    su = db.Column(db.Boolean(), nullable=False)
    challenge_1 = db.Column(db.String(20), unique=True)
    challenge_2 = db.Column(db.String(20), unique=True)
    challenge_3 = db.Column(db.String(20), unique=True)
  ##  posts = db.relationship('Post', backref='author', lazy='dynamic')

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<User {}>'.format(self.username)


class ValidApp(db.Model):
    __tablename__ = 'ValidApp'
    id = db.Column(db.Integer, primary_key=True)
    app_license = db.Column(db.String(100))
    activation_code = db.Column(db.String(100))
    duration = db.Column(db.String(50))

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<id {},License: {} , Activation Code: {}, duration: {}>'. \
            format(self.id, self.app_license, self.activation_code, self.duration)

    def check_license(self, code):
        return check_password_hash(self.app_license, code)


class OwnerDetails(db.Model):
    __tablename__ = 'OwnerDetails'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    address = db.Column(db.Text, nullable=False)
    address1 = db.Column(db.Text)
    lga = db.Column(db.String(20))
    state = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    phone_no = db.Column(db.String(11))
    phone_no_2 = db.Column(db.String(11))

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<ID: {}, Name: {}>'.format(self.id, self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Code: {} , Description {}>'.format(self.type_code, self.type_description)


class ModeOfDonation(db.Model):
    __tablename__ = 'ModeOfDonation'
    mode_id = db.Column(db.Integer, primary_key=True)
    mode_code = db.Column(db.String(10), nullable=False)
    mode_description = db.Column(db.String(20), nullable=False)

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<Code: {} , Description {}>'.format(self.type_code, self.type_description)


class TypeOfDonation(db.Model):
    __tablename__ = 'TypeOfDonation'
    type_id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(10), nullable=False)
    type_description = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<Code: {} , Description {}>'.format(self.type_code, self.type_description)


class PaymentType(db.Model):
    __tablename__ = 'PaymentType'
    type_id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(10), nullable=False)
    type_description = db.Column(db.String(20), nullable=False)

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<Code: {} , Description {}>'.format(self.type_code, self.type_description)


class MemberType(db.Model):
    __tablename__ = 'MemberType'
    type_id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(10), nullable=False)
    type_description = db.Column(db.String(20), nullable=False)

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<Code: {} , Description {}>'.format(self.type_code, self.type_description)


class GroupType(db.Model):
    __tablename__ = 'GroupType'
    type_id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(10), nullable=False)
    type_description = db.Column(db.String(20), nullable=False)

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<Code: {} , Description {}>'.format(self.type_code, self.type_description)


MemberGroupLink = db.Table('MemberGroupLink',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('member_id', db.String(10), db.ForeignKey('public.Members.member_id')),
                           db.Column('type_code', db.String(10), db.ForeignKey('public.GroupType.type_code')),
                           UniqueConstraint('member_id', 'type_code'))


class Members(UserMixin, db.Model):

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return True

    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(10))
    member_type_id = db.Column(db.String(10), nullable=False)
    password_hash = db.Column(db.String(128))
    ## member_group_id = db.Column(db.String(10), nullable=False)
    member_lastname = db.Column(db.String(20), nullable=False)
    member_firstname = db.Column(db.String(20), nullable=False)
    member_middlename = db.Column(db.String(20))
    member_address = db.Column(db.Text, nullable=False)
    member_address1 = db.Column(db.Text)
    member_email = db.Column(db.String(120), unique=True)
    member_phone_no = db.Column(db.String(11))
    active = db.Column(db.Boolean)
    donation = db.relationship('Donations', backref='donor', lazy='dynamic')
    family = db.relationship('FamilyTrail', backref='family', lazy='dynamic')
    groups = db.relationship('GroupType', secondary=MemberGroupLink, lazy='dynamic',
                             backref=db.backref('Members', lazy='dynamic'))
    # trailing = db.relationship('Donationstrail', backref='donor_donation', lazy='dynamic')

    __table_args__ = (
        UniqueConstraint("member_id"),  {'schema': 'public'}
    )

    def __repr__(self):
        return '<ID: {}, Name: {} ,{}>'.format(self.member_id, self.member_firstname, self.member_lastname)


# class MemberGroupLink(db.Model):
#     __tablename__ = 'MemberGroupLink'
#     id = db.Column(db.Integer, primary_key=True)
#     member_id = db.Column(db.String(7), nullabe=False)
#     type_code = db.Column(db.String(10), nullable=False)


class Donations(db.Model):
    __tablename__ = 'Donations'
    donation_id = db.Column(db.String(15), primary_key=True)
    donation_type_id = db.Column(db.String(10), nullable=False)
    member_id = db.Column(db.String(7), db.ForeignKey(Members.member_id), nullable=False)
    donation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    amount = db.Column(db.Float(9, 2), nullable=False)
    donation_mode_id = db.Column(db.String(10), nullable=False)
    payment_status = db.Column(db.Boolean(), nullable=False, default=False)
    #payment_status = db.Column(db.String(2), nullable=False, default=0)
    #payment_type_id = db.Column(db.String(10), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    trail = db.relationship('Donationstrail', backref='donation', lazy='dynamic')

    __table_args__ =  {"schema": "public"}
    

    def __repr__(self):
        return '<Member ID: {}, Donation Type: {}, Donation ID: {}, Amount: {}>'.format(self.member_id,
                                                                                        self.donation_id,
                                                                                        self.donation_type_id,
                                                                                        self.amount)


class Donationstrail(db.Model):
    __tablename__ = 'Donationtrail'
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey(Donations.donation_id))
    # , primary_key=True,  autoincrement=False)
    donation_type_id = db.Column(db.String(2), nullable=False)
    payment_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    payment_type_id = db.Column(db.String(2), nullable=False)
    payment_details = db.Column(db.Text)
    amount = db.Column(db.Float(9, 2), nullable=False)

    __table_args__ =  {"schema": "public"}

    #
    # __table_args__ = (
    #         UniqueConstraint("donation_id", "member_id"),
    #     )

    def __repr__(self):
        return '<Donation ID: {} , Donation Type: {},  Amount: {}>'.format(self.donation_id, self.donation_type_id,
                                                                           self.amount)


ReportFieldFilterLink = db.Table('ReportFieldFilterLink',
                                 db.Column('id', db.Integer, primary_key=True),
                                 db.Column('field_id', db.String(10), db.ForeignKey('public.ReportFilterField.field_id')),
                                 db.Column('filter_id', db.String(3), db.ForeignKey('public.ReportFilter.filter_id')))

ReportNameFilterLink = db.Table('ReportNameFilterLink',
                                db.Column('id ', db.Integer, primary_key=True),
                                db.Column('report_id', db.String(10), db.ForeignKey('public.ReportName.report_id')),
                                db.Column('field_id', db.String(30), db.ForeignKey('public.ReportFilterField.field_id')),
                                UniqueConstraint('report_id', 'field_id')
                                )


class ReportName(db.Model):
    __tablename__ = 'ReportName'
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(10), nullable=False, unique=True)
    report_name = db.Column(db.String(50), nullable=False, unique=True)
    report_header = db.Column(db.String(50), nullable=False, unique=True)
    access_id = db.Column(db.String(50), nullable=False, unique=True)
    query_stmt = db.Column(db.String(1000), nullable=False, unique=True)
    filterfield = db.relationship('ReportFilterField', secondary=ReportNameFilterLink, lazy='dynamic',
                                  backref=db.backref('ReportName', lazy='dynamic'))

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<id : {}, report_id: {},  report_name: {}, report_header: {}, query_stmt: {}  >'. \
            format(self.id, self.report_id, self.report_name, self.report_header, self.query_stmt)


class ReportFilterField(db.Model):
    __tablename__ = 'ReportFilterField'
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.String(30), nullable=False, unique=True)
    filter_field = db.Column(db.String(50), nullable=False, unique=True)
    filter_header = db.Column(db.String(30), nullable=False, unique=True)
    filterlogic = db.relationship('ReportFilter', secondary=ReportFieldFilterLink, lazy='dynamic',
                                  backref=db.backref('ReportFilterField', lazy='dynamic'))

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<field_id: {} , filter_field : {}, filter_header: {} >'.format(self.field_id, self.filter_field,
                                                                               self.filter_header)


class ReportFilter(db.Model):
    __tablename__ = 'ReportFilter'
    id = db.Column(db.Integer, primary_key=True)
    filter_id = db.Column(db.String(3), nullable=False, unique=True)
    action = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(20), nullable=False)

    __table_args__ =  {"schema": "public"}

    def __repr__(self):
        return '<field_id: {} , action:{}, description : {}>'.format(self.filter_id, self.description, self.action)


class FamilyTrail(db.Model):
    __tablename__ = 'FamilyTrail'
    __table_args__ =  {"schema": "public"}
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.String(10), nullable=False)
    member_id = db.Column(db.String(10), db.ForeignKey('public.Members.member_id'), nullable=False, unique=True)
    family_name = db.Column(db.String(100), nullable=False)
    relation_id = db.Column(db.String(3), db.ForeignKey('public.FamilyRelation.relation_id'), nullable=False)



    def __repr__(self):
        return '<family_id: {} , member_id : {}, relation_id : {} >'.format(self.family_id,
                                                                            self.member_id, self.relation_id)


class FamilyRelation(db.Model):
    __tablename__ = 'FamilyRelation'
    __table_args__ = {"schema": "public"}
    id = db.Column(db.Integer, primary_key=True)
    relation_id = db.Column(db.String(3), nullable=False, unique=True)
    relation_description = db.Column(db.String(100), nullable=False)



    ## related = db.relationship('FamilyTrail', backref='relation', lazy='dynamic')

    def __repr__(self):
        return '<relation_id: {} , description : {}>'.format(self.relation_id, self.relation_description)


class UpdatePayment(object):

    def __init__(self, donation_id, amount):
        self.donation_id = donation_id
        self.amount = float(amount)

        """
        total_paid: Sum the amount paid by donor for a particular donation ID
                    >>get total amount paid by member from Donationstrail table<<
        donation_amt: Donation amount from the member particular donation ID
                       >>get donation amount for member from Donations table<<
        expected_amt: Outstanding payment of member for a particular donation ID
                      >> donation_amt -  total_paid <<
        """
        # donor = Donations.query.filter_by(donation_id=self.donation_id).first()
        donor = db.session.query(Donations).filter(Donations.donation_id == self.donation_id).first()

        paid = db.session.query(Donationstrail).filter(Donationstrail.donation_id == self.donation_id). \
            with_entities(func.sum(Donationstrail.amount).label('total_amount')).one()

        paid_row = db.session.query(Donationstrail).filter(Donationstrail.donation_id == self.donation_id). \
            with_entities(func.count(Donationstrail.amount).label('count')).one()

        self.total_paid = 0.0
        if paid_row.count > 0:
            self.total_paid = float(paid.total_amount)

        self.donation_amt = float(donor.amount)
        self.expected_amt = self.donation_amt - self.total_paid

    def check_payment(self):
        if self.amount > self.expected_amt:
            return False
        else:
            return True

    def payment_complete(self):
        if self.donation_amt - (self.total_paid + self.amount) == 0:
            return True
        else:
            return False

    def expected_amount(self):
        return self.expected_amt

    def redeem_amount(self):
        return self.total_paid

    def update_donation(self):
        check = self.amount - self.total_paid

        if check > 0:
            return (True, '0')

        if check == 0:
            return (True, '1')

        if check < 0:
            return (False, '2')


class SearchData(object):

    def __init__(self, **kwargs):
        self.src_string = kwargs.get("src_string")
        self.table_name = kwargs.get("table_name")
        self.field_id = kwargs.get("field_id")
        self.sort_by = kwargs.get("sort_by")
        self.look_for = '%{0}%'.format(self.src_string)
        self.result = {}

    @staticmethod
    def connection():
        sqlite_file = app.config['SQLITE_PATH']
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        return cursor

    def get_description(self):
        cursor = self.connection()
        slqstmt = 'select type_description from  ' + self.table_name + ' where ' + self.field_id + ' = "' \
                  + self.src_string + '"'
        result = cursor.execute(slqstmt).fetchone()
        # self.description = result[0]
        description = result[0]
        return description

    def search_donation(self):
        cursor = self.connection()
        slqstmt = 'select distinct donation_id, member_id from Donations where (donation_id like "%pr%" or' \
                  ' member_id like "%10%")'
        result = cursor.execute(slqstmt).fetchone()
        description = result[0]
        return description

    def search_member(self):
        cursor = self.connection()
        slqstmt = 'select distinct member_id, member_lastname from Members where (member_id like "%ol%" or' \
                  ' member_lastname like "%ol%" or member_firstname like "%10%" or member_middlename like "%ol%")'
        result = cursor.execute(slqstmt).fetchone()
        description = result[0]
        return description

    def get_member(self):
        field_id = {self.field_id: self.src_string}
        result = self.table_name.query.filter_by(**field_id).first()
        return result


class UploadsManager(object):
    def __init__(self, df_file, ext, db_table):
        self.ext = ext
        self.missing_field = []
        self.db_table = db_table
        if self.ext in ['.xls', '.xlsx']:
            self.df = pd.read_excel(df_file, index_col=None)
        if self.ext == '.csv':
            with open(df_file, 'rb') as f:
                result = chardet.detect(f.read())
                self.df = pd.read_csv(df_file, encoding=result['encoding'], sep=None)

    def verify_header(self):
        # self.df.head(5)

        if self.db_table == 'Members':
            header_set = ['member_id', 'member_type_id', 'member_lastname',
                          'member_firstname', 'member_middlename', 'member_address',
                          'member_address1', 'member_email', 'member_phone_no']

        if self.db_table == 'Donations':
            header_set = ['donation_id', 'donation_type_id', 'member_id', 'donation_date',
                          'amount', 'donation_mode_id', 'comment']

        if self.db_table == 'Groups':
            header_set = ['type_code', 'member_id']

        missing_field = []
        for item in header_set:
            if item not in self.df.columns:
                missing_field.append(item)
        if len(missing_field) > 0:
            self.missing_field = missing_field
            return False
        else:
            return True


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class Search(object):
    def __init__(self, search_text):
        self.search_text = search_text

    def add_donation_name_option(self):

        qryresultcount = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                              Members.member_lastname.ilike(self.search_text),
                                                              Members.member_middlename.ilike(
                                                                  self.search_text))).order_by(
            Members.member_lastname.desc()).count()
        qryresult = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                         Members.member_lastname.ilike(self.search_text),
                                                         Members.member_middlename.ilike(self.search_text))).order_by(
            Members.member_lastname.desc())
        if qryresultcount > 0:
            typename = {}
            for m in qryresult:
                for d in m.donation.all():
                    decription = TypeOfDonation.query.filter_by(type_code=d.donation_type_id).first()
                    typename[d.donation_type_id] = decription.type_description

            return True, qryresult, typename
        else:
            return False, None, None

    def donation_name_option(self):
        qryresultcount = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                              Members.member_lastname.ilike(self.search_text),
                                                              Members.member_middlename.ilike(
                                                                  self.search_text))).order_by(
            Members.member_lastname.desc()).count()
        qryresult = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                         Members.member_lastname.ilike(self.search_text),
                                                         Members.member_middlename.ilike(self.search_text))).order_by(
            Members.member_lastname.desc())
        if qryresultcount > 0:
            typename = {}
            for m in qryresult:
                for d in m.donation.all():

                    decription = TypeOfDonation.query.filter_by(type_code=d.donation_type_id).first()
                    typename[d.donation_type_id, 0] = decription.type_description
                    trail_amt = 0
                    for t in d.trail.all():
                        trail_amt = trail_amt + t.amount

                    typename[d.donation_id, 1] = trail_amt
                    typename[d.donation_id, 2] = d.amount - trail_amt

            return True, qryresult, typename
        else:
            return False, None, None

    def donation_id_option(self):

        qryresultcount = db.session.query(Donations).filter(or_(Donations.donation_id.ilike(self.search_text),
                                                                Donations.member_id.ilike(self.search_text))).order_by( \
            Donations.donation_type_id.desc()).count()
        qryresult = db.session.query(Donations).filter(or_(Donations.donation_id.ilike(self.search_text),
                                                           Donations.member_id.ilike(self.search_text))).order_by( \
            Donations.donation_type_id.desc())
        if qryresultcount > 0:
            typename = {}
            for x in qryresult:
                decription = TypeOfDonation.query.filter_by(type_code=x.donation_type_id).first()
                member = Members.query.filter_by(member_id=x.member_id).first()
                typename[x.member_id] = member.member_firstname + ' ' + member.member_lastname
                typename[x.donation_type_id] = decription.type_description
                typename[x.payment_status] = x.payment_status
                total_amt_paid = UpdatePayment(x.donation_id, 0.0)
                donation_amt = x.donation_id
                typename[donation_amt] = total_amt_paid.redeem_amount()
            return True, qryresult, typename
        else:
            return False, None, None

    def Member_id_option(self):
        qryresultcount = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                              Members.member_lastname.ilike(self.search_text),
                                                              Members.member_middlename.ilike(
                                                                  self.search_text))).order_by(
            Members.member_lastname.desc()).count()
        qryresult = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                         Members.member_lastname.ilike(self.search_text),
                                                         Members.member_middlename.ilike(self.search_text))).order_by(
            Members.member_lastname.desc())
        if qryresultcount > 0:
            typename = {}
            for m in qryresult:
                for d in m.donation.all():

                    decription = TypeOfDonation.query.filter_by(type_code=d.donation_type_id).first()
                    typename[d.donation_type_id, 0] = decription.type_description
                    trail_amt = 0
                    for t in d.trail.all():
                        trail_amt = trail_amt + t.amount

                    typename[d.donation_id, 1] = trail_amt
                    typename[d.donation_id, 2] = d.amount - trail_amt

    def member_name_option(self):

        qryresultcount = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                              Members.member_lastname.ilike(self.search_text),
                                                              Members.member_middlename.ilike(
                                                                  self.search_text))).order_by(
            Members.member_lastname.desc()).count()
        qryresult = db.session.query(Members).filter(or_(Members.member_firstname.ilike(self.search_text),
                                                         Members.member_lastname.ilike(self.search_text),
                                                         Members.member_middlename.ilike(self.search_text))).order_by(
            Members.member_lastname.desc())


def process_exists(processname):
    tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % processname
    # shell=True hides the shell window, stdout to PIPE enables
    # communicate() to get the tasklist command result
    tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
    # trimming it to the actual lines with information
    tlout_0 = tlproc.communicate()[0]
    tlout_1 = str(tlout_0).strip().split('\r\n')
    tlout = tlout_1[0]

    if tlout.__contains__(processname):
        return True
    else:
        return False


def restore_db(conn, db_file, filename='dump.sql'):
    """ Using DDL and DML SQL script creates a new database
            """
    with open(filename, 'r') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()


def export_db(conn, filename):
    """ Creates DDL and DML SQL script file
    """
    with open(filename, 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)


def sqlite3_backup(dbfile, backupdir):
    """
        This script creates a timestamped database backup,
        and cleans backups older than a set number of dates

        """

    DESCRIPTION = """
                      Create a timestamped SQLite database backup, and
                      clean backups older than a defined number of days
                      """

    if not os.path.isdir(backupdir):
        raise Exception("Backup directory does not exist: {}".format(backupdir))

    backup_file = os.path.join(backupdir, os.path.basename(dbfile) + time.strftime("-%Y%m%d-%H%M%S"))
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()

    # Lock database before making a backup
    cursor.execute('begin immediate')
    # Make new backup file
    shutil.copyfile(dbfile, backup_file)
    flash("\nCreating {}...".format(backup_file))
    # Unlock database
    connection.rollback()


def clean_data(backup_dir, sender):
    """
    How old a file needs to be in order
    to be conidered for being removed
    """
    NO_OF_DAYS = 21

    #  Delete files older than NO_OF_DAYS days
    flash_msg = "Cleaning up old " + sender
    # flash(flash_msg)
    printed_heading = False
    elapse_time = time.time() - NO_OF_DAYS * 86400
    if len(os.listdir(backup_dir)) > 0:
        for filename in os.listdir(backup_dir):
            backup_file = os.path.join(backup_dir, filename)
            if os.path.isfile(backup_file):
                if os.stat(backup_file).st_ctime < elapse_time:
                    if not printed_heading:
                        flash(flash_msg)
                        printed_heading = True
                    flash("Deleting {}...".format(filename))
                    os.remove(backup_file)


def sqlite3_restore_backup(dbfile, backupdir):
    """Create timestamped database copy"""

    """
        This script creates a timestamped database backup,
        and cleans backups older than a set number of dates

        """

    DESCRIPTION = """
                      Create a timestamped SQLite database backup, and
                      clean backups older than a defined number of days
                      """

    backup_file = os.path.basename(dbfile)
    backup_file_split = backup_file.split("-")
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()
    # restored_db = backup_file_split[0].strip(" ") + ".db"
    restored_db = backup_file_split[0].strip(" ")

    # Lock database before making a backup
    cursor.execute('begin immediate')
    # Make new backup file
    shutil.copyfile(dbfile, os.path.join(backupdir, restored_db))
    flash("\nRestoring {}...".format(backup_file))
    # Unlock database
    connection.rollback()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def last_member_id():
    # last_item = Members.query.order_by(Members.id.desc()).first()
    last_item = Members.query.order_by(Members.member_id.desc()).first()
    if last_item:
        return last_item.member_id
    else:
        return 'No Member record avaialable, Please add member to database'


def license_key(count):
    licensefolder = app.config['LICENSE_FOLDER']
    file_path = os.path.join(licensefolder, 'License.txt')
    start_time = ""

    seq = "0987654321ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz"

    with open(file_path, 'w') as f:
        for i in range(count):
            """
            lic_plus_rnd: This will be encoded and saved in the license file, will be send by the user to use 
                          for decoding  and sent back to activate the licence

            db_lic: This will be hashed as stored in the database as the app_license

            license_encoded:  the encoded form of lic_plus_rnd
            """

            lic = '-'.join(''.join(random.choice(seq) for _ in range(5)) for _ in range(5))
            lic_plus_rnd = str(random.randint(100, 900)) + "-l-" + lic + "-c-" + str(random.randint(100, 900))

            db_lic = lic + "-" + str(hex(uuid.getnode()))

            license_encoded = base64.b64encode(bytes(lic_plus_rnd, 'utf-8'))

            licence_output = "License Activation Code: {} ".format(license_encoded)

            f.write('%s\n' % licence_output)

            hashed_app_license = generate_password_hash(db_lic)
            start_time = str(time.time())
            encoded_time = base64.b64encode(bytes(start_time, 'utf-8'))
            lic = ValidApp.query.first()

            ## -- We need only one license, if there on update it else create one
            if lic is not None:
                row = ValidApp.query.get(lic.id)
                row.duration = encoded_time
                row.app_license = hashed_app_license
                db.session.commit()
            else:
                save_license = ValidApp(duration=encoded_time, app_license=hashed_app_license)
                db.session.add(save_license)
                db.session.commit()

                with open(app.config['LICENSE_BACKUP_FILE'], 'w') as bckf:
                    start_time_and_app_license = hashed_app_license + "-" + start_time
                    bckf.write(start_time_and_app_license)

    with open(app.config['LICENSE_COUNT'], 'w') as wf:
        count_and_time = "0, " + start_time
        wf.write(count_and_time)


def getTableDump(db_file, table_to_dump):
    conn = sqlite3.connect(':memory:')
    cu = conn.cursor()
    cu.execute("attach database '" + db_file + "' as attached_db")
    cu.execute("select sql from attached_db.sqlite_master "
               "where type='table' and name='" + table_to_dump + "'")
    # sql_create_table = cu.fetchone()[0]
    # cu.execute(sql_create_table);
    cu.execute("insert into " + table_to_dump +
               " select * from attached_db." + table_to_dump)
    conn.commit()
    cu.execute("detach database attached_db")

    # return "\n".join(conn.iterdump())
    backup_path = app.config['BACKUP_FOLDER']
    backup_file = 'table_backup' + time.strftime("-%Y%m%d-%H%M%S") + '.sql'
    file_path = os.path.join(backup_path, backup_file)
    sql = "\n".join(conn.iterdump())
    with open(file_path, 'x') as f:
        f.write('%s\n' % sql)

    # return "\n".join(conn.iterdump())


def validateLicense():
    """
    Checks the license status
    license_status = 0 - Invalid License
    license_status = 1 - License has been validated
    license_status = 10 - License files has been tampered
    license_status = 3  - License table has not been populated  and License count is untampered
     license_status = 4   License count(clds.dat) file has been tampered
    :return:
    """
    license_details = ValidApp.query.first()
    license_status = 1
    file_path = app.config['LICENSE_COUNT']
    file_error = False

    try:  # check if license check file are intact.
        bck_file = open(app.config['LICENSE_BACKUP_FILE'], 'r')
        cnt_file = open(app.config['LICENSE_COUNT'], 'r')
    except IOError:
        file_error = True
    else:
        bck_file.close()
        cnt_file.close()

    if license_details is not None and license_details.activation_code is not None:
        code = license_details.activation_code + "-" + str(hex(uuid.getnode()))
        if not license_details.check_license(code):
            license_status = 0
        else:
            license_status = 1
    else:
        if not file_error:
            if license_details is not None: # License table has been populated
                with open(file_path, 'r') as lrf:
                    elapsed = lrf.readline().split(",")
                    if elapsed[0] == '':
                        license_status = 4
                    else:
                        license_status = 2
            elif license_details is None: # License table has not been populated
                with open(file_path, 'r') as lrf:
                    elapsed = lrf.readline().split(",")
                    if elapsed[0] == '':
                        license_status = 4
                    else:
                        license_status = 3
        else:
            license_status = 10

    return license_status


def data_loader(db_file, tables_to_dump):
    destDB = app.config['SQLITE_PATH']
    conn = sqlite3.connect(destDB)
    cursor = conn.cursor()
    cursor.execute("attach database '" + db_file + "' as sourceDB")

    for table in tables_to_dump:
        if table == 'PaymentType':
            cursor.execute("Delete from PaymentType")

        if table == 'user':
            cursor.execute("Delete from user")

    try:

        for table in tables_to_dump:
            cursor.execute("select sql from sourceDB.sqlite_master "
                           "where type='table' and name='" + table + "'")
            sqldump = "insert into " + table + " select * from sourceDB." + table
            cursor.execute(sqldump)

    except sqlite3.Error as err:
        print(err)
        msg = str(err)
        flash("**********")
        flash(msg.upper())
        cursor.execute('rollback')
        cursor.execute("detach database sourceDB")
        return False
    else:
        conn.commit()
        cursor.execute("detach database sourceDB")
        return True

import subprocess
from subprocess import Popen, PIPE
##--------------- End of ostgres database Managemnet-----------

def backup_postgres_db():
    """
    Backup postgres db to a file.

    host, database_name, port, user, password, dest_file, verbose
    """
    verbose = True
    user = "db_donatrack"
    host = "127.0.0.1"
    port = "5432"
    database_name = "donatrack_web"
    password = '123456'
    #dest_file= "c:\\apps\\FileDump.sql"
    backupdir = app.config['BACKUP_FOLDER']
    backup_file = os.path.join(backupdir, "DonatrackBackupFile" + time.strftime("-%Y%m%d-%H%M%S"))
    #dumper = """ "c:\\program files\\postgresql\\11\\bin\\pg_dump" -U %s -Z 9 -f %s -F c %s  """
    #return backup_file
    print(backup_file)
    USER = "db_donatrack"
    database_name = "donatrack_web"
    dumper = """ "c:\\program files\\postgresql\\11\\bin\\pg_dump" """
    password = '123456'

    if verbose:
        try:
            process = subprocess.Popen(
                ["c:\\program files\\postgresql\\11\\bin\\pg_dump",
                 '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, database_name),
                 '-Fc',
                 '-f', backup_file ,
                 '-v'],
                stdout=subprocess.PIPE
            )
            output = process.communicate()[0]
            if int(process.returncode) != 0:
                print('Command failed. Return code : {}'.format(process.returncode))
                exit(1)
            return output
        except Exception as e:
            print(e)
            exit(1)
    else:

        try:
            process = subprocess.Popen(
                ['pg_dump',
                 '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user, password, host, port, database_name),
                 '-f', dest_file],
                stdout=subprocess.PIPE
            )
            output = process.communicate()[0]
            if process.returncode != 0:
                print('Command failed. Return code : {}'.format(process.returncode))
                exit(1)
            return output
        except Exception as e:
            print(e)
            exit(1)



def restore_postgres_db():
    """
    Restore postgres db from a file.

    db_host, db, port, user, password, backup_file, verbose
    """

    verbose = True
    user = "db_donatrack"
    db_host = "127.0.0.1"
    port = "5432"
    db = "donatrack_web"
    password = '123456'
    backup_file= "c:\\apps\\FileDump.sql"
    # dumper = """ "c:\\program files\\postgresql\\11\\bin\\pg_dump" -U %s -Z 9 -f %s -F c %s  """
    USER = "db_donatrack"
    database_name = "donatrack_web"
    dumper = """ "c:\\program files\\postgresql\\11\\bin\\pg_restore" """
    password = '123456'

    if verbose:
        try:
            print(user,password,db_host,port, db)
            process = subprocess.Popen(
                ["c:\\program files\\postgresql\\11\\bin\\pg_restore",
                 '--no-owner',
                 '-n public'
                 '-c',
                 '-1',
                 '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user,
                                                               password,
                                                               db_host,
                                                               port, db),
                 '-v',
                 backup_file],
                stdout=subprocess.PIPE
# pg_restore -U db_username -n public -c -1 -d db_name dump.db
            )
            output = process.communicate()[0]

            return output
            if int(process.returncode) != 0:
                print('Command failed. Return code : {}'.format(process.returncode))
                #exit(1)
            return output
        except Exception as e:
            print("Issue with the db restore : {}".format(e))
            exit(1)
    else:
        try:
            process = subprocess.Popen(
                ["c:\\program files\\postgresql\\11\\bin\\pg_restore",
                 '--no-owner',
                 '--dbname=postgresql://{}:{}@{}:{}/{}'.format(user,
                                                                      password,
                                                                      db_host,
                                                                      port, db),
                 backup_file],
                stdout=subprocess.PIPE
            )
            output = process.communicate()[0]
            if int(process.returncode) != 0:
                print('Command failed. Return code : {}'.format(process.returncode))
                exit(1)

            #return output
        except Exception as e:
            print("Issue with the db restore : {}".format(e))
            exit(1)


def generate_member_password(member_id):

    import secrets
    import string
    import random
    from random import sample, choice

    conn = db_conn_only()
    cursor = conn.cursor()

    password_input = string.ascii_letters + "!@#$%&" + string.digits
    first_password = ''.join(secrets.choice(password_input) for i in range(8))

    user = Members.query.filter_by(member_id=member_id).first()
    user.set_password(first_password)
    # print('Helooo')
    db.session.commit()
    sqlstmt_1 = 'INSERT INTO public."MemberFirstPass"'
    sqlstmt_1 = sqlstmt_1 + "(member_id, first_pass) VALUES( '" + member_id + "' ,'" + first_password + "');"
    cursor.execute(sqlstmt_1)
    conn.commit()

    ##print(final_password)