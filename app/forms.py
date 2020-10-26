from datetime import timedelta

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, HiddenField, \
    DecimalField, RadioField, SelectMultipleField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, optional
from wtforms.widgets import ListWidget, CheckboxInput, Select

from app.models import *
#
#
class FormControl(FlaskForm):
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')
    update = SubmitField('update')
    cancel = SubmitField('Cancel')
    close = SubmitField('Close')
    search = SubmitField('Search')
    requiredbx = StringField('inputbx', validators=[DataRequired()])
    inputbx = StringField('inputbx', validators=[optional()])
#
#
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login_type = RadioField('Label', choices=[('member_option', ' Member'), ('admin_option', 'Admin')], default='member_option')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    reset_password = SubmitField('Forgot Password')

#
class OwnerDetailsForm(FlaskForm):
    id = HiddenField()
    name = StringField('Name', validators=[DataRequired('*')])
    address = StringField('Address', validators=[DataRequired('*')])
    address1 = StringField('Address')
    lga = StringField('LGA')
    state = StringField('State')
    email = StringField('Email', validators=[DataRequired('*'), Email()])
    phone_no = StringField('Phone No(1).', validators=[DataRequired('*')])
    phone_no_2 = StringField('Phone No(2).', validators=[optional()])

    # def validate_email(self, email):
    #     user = OwnerDetails.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         return False


class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    lastname = StringField('Lastname', validators=[DataRequired('*')])
    firstname = StringField('Firstname', validators=[DataRequired('*')])
    challenge_1 = PasswordField('My best place in the world', validators=[DataRequired('*')])
    challenge_2 = PasswordField('Favorite Clothe', validators=[DataRequired('*')])
    challenge_3 = PasswordField('Favorite film', validators=[DataRequired('*')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField("Admin")
    su = BooleanField("Super Admin")
    cancel = SubmitField('Cancel')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
#
#
class DonationSettingForm(FlaskForm):
    code = StringField(validators=[DataRequired()])
    description = StringField(validators=[DataRequired()])
    date = DateField('Creation Date', default=datetime.today())
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')
    update = SubmitField('update')
    cancel = SubmitField('Cancel')


class MemberForm(FlaskForm):
    # --- Fields----
    sid = HiddenField()
    member_self_type = HiddenField()
    member_id = StringField('Membership ID', validators=[DataRequired('*')])
    # type_id = StringField('Membership Type', validators=[DataRequired('*')])
    type_id = SelectField('Membership Type:', validators=[DataRequired('*')], id='type_id')
    group_choice = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    # group_id = SelectMultipleField(u'Group Membership', choices=group_choice, id='group_id')
    group_id = SelectField('Group Membership:', id='group_id', validators=[optional()])
    lastname = StringField('Last Name', validators=[DataRequired('*')])
    firstname = StringField('First Name', validators=[DataRequired('*')])
    middlename = StringField('Middle Name')
    address = StringField('Address ')
    address1 = StringField('Address')
    email = StringField('email', validators=[optional(), Email()])
    phone_no = StringField('Phone Number', validators=[DataRequired('*')])

    # --- Buttons----
    def validate_member(self, id):
        member = Members.query.filter_by(member_id=id).first()
        if member is not None:
            return True
        else:
            return False

    def validate_email(self, email):
        if self.email.data:
            member = Members.query.filter_by(member_email=email.data).first()
            if member is not None:
                return True
            else:
                return False


class DonationForm(FlaskForm):
    # --- Fields----

    donation_id = StringField('Donation ID', validators=[DataRequired('*')])
    member_name = StringField('Member Name')
    member_id = StringField('Membership ID', validators=[DataRequired('*')])
    donation_type_id = SelectField('Type of Donation', validators=[DataRequired('*')], id='donation_type_id')
    date = DateField('Donation Date', default=datetime.today())
    # amount = FloatField('Amount Donated', validators=[DataRequired('*')]) format='%d-%m-%Y'
    amount = DecimalField('Amount Donated',
                          places=2, rounding=None, use_locale=False, number_format='0:,.2f',
                          validators=[DataRequired('*')])
    mode_id = SelectField('Mode of Donation:', validators=[DataRequired('*')], id='mode_id')
    mode_id.choices = [(row.mode_code, row.mode_description) for row in ModeOfDonation.query.all()]
    donation_type_id.choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    # payment_type_id = SelectField('Mode of Payment', validators=[DataRequired('*')], id='ptype_id')
    generate_id = SubmitField('Generate Donation ID')
    comment = TextAreaField('Comments', validators=[optional()])
    #  --- Buttons----


class DonationTrailForm(FlaskForm):
    # member_id = StringField('Membership ID', validators=[DataRequired()])
    member_id = HiddenField()
    member_name = StringField('Member Name')
    donation_id = StringField('Donation ID', validators=[DataRequired()])
    # donation_type_id = StringField('Donation Type', validators=[DataRequired()])
    donation_type_id = HiddenField()
    donation_type_name = StringField('Type of Donation')
    payment_type_id = SelectField('Mode of Payment', validators=[DataRequired('*')], id='ptype_id')
    # amount = FloatField('Amonut Paid', validators=[DataRequired()])
    amount = DecimalField('Amount Paid',
                          places=2, rounding=None, use_locale=False, number_format='%0:,.2f',
                          validators=[DataRequired('*')])
    payment_date = DateField('Date of Payment', default=datetime.today(), \
                             validators=[DataRequired()])
    payment_details = StringField('Payment Detail', validators=[DataRequired()])

    def validate_amount(self, amount):
        payment = UpdatePayment(self.donation_id.data, amount.data)
        payment_ok = payment.check_payment()
        if not payment_ok:
            flash('Amount must not exceed :' + ' ' +
                  str('{0:,.2f}'.format(payment.expected_amount())))
            raise ValidationError('Amount out of range.')


class SearchForm(FlaskForm):
    src_string = StringField('Member ID', validators=[DataRequired('*')])
    get_module = HiddenField()
    search_option = RadioField('Label', choices=[('id_option', ' ID'), ('name_option', ' Name')], default='name_option')


class UploadForm(FlaskForm):
    file = FileField('image', validators=[
        FileRequired(), FileAllowed(['csv', 'xls', 'xlsx'])])


class ReportGenaratorForm(FlaskForm):
    report_qry = ReportName.query.order_by(ReportName.report_header).all()
    report_choice = [(row.report_id, row.report_header) for row in report_qry]
    report_name = SelectField(u'Report Name:', validators=[DataRequired()], id='report_name',
                              choices=report_choice, default=report_choice[0][0])

    rptName = ReportName.query.filter_by(report_id=report_choice[0][0]).first()
    rptFieldfilter = rptName.filterfield  # --- ReportFilterField---
    filter_fields_choice = [(row.field_id, row.filter_header) for row in rptFieldfilter]
    filter_field = SelectField(u'Filter Field:', validators=[DataRequired()], id='filter_field',
                               choices=filter_fields_choice, default=filter_fields_choice[0][0])

    rptFieldfilter = ReportFilterField.query.filter_by(field_id=filter_fields_choice[0][0]).first()
    rptfilter = rptFieldfilter.filterlogic  # --- ReportFilter ----
    filter_choice = [(row.filter_id, row.description) for row in rptfilter]
    filter = SelectField(u'Filter:', validators=[DataRequired()], id='filter',
                         choices=filter_choice, default=filter_choice[0][0])
    #
    start_field = StringField()
    end_field = StringField()
    start_date = DateField('Start Date', default=datetime.today() - timedelta(days=30))
    end_date = DateField('End Date', default=datetime.today())

    categoty_choice = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    donation_name = SelectField(u'Donation Name:', validators=[DataRequired()], id='donation_name',
                                choices=categoty_choice)

    categoty_choice = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    group_name = SelectField(u'Group Name:', validators=[DataRequired()], id='group_name',
                             choices=categoty_choice)



    # ------------------------------------------------------------------------------
class MemberReportGenaratorForm(FlaskForm):
        report_qry = ReportName.query.filter_by(access_id='2').order_by(ReportName.report_header).all()
        report_choice = [(row.report_id, row.report_header) for row in report_qry]
        report_name = SelectField(u'Report Name:', validators=[DataRequired()], id='report_name',
                                  choices=report_choice, default=report_choice[0][0])

        rptName = ReportName.query.filter_by(report_id=report_choice[0][0]).first()
        rptFieldfilter = rptName.filterfield  # --- ReportFilterField---
        filter_fields_choice = [(row.field_id, row.filter_header) for row in rptFieldfilter]
        filter_field = SelectField(u'Filter Field:', validators=[DataRequired()], id='filter_field',
                                   choices=filter_fields_choice, default=filter_fields_choice[0][0])

        rptFieldfilter = ReportFilterField.query.filter_by(field_id=filter_fields_choice[0][0]).first()
        rptfilter = rptFieldfilter.filterlogic  # --- ReportFilter ----
        filter_choice = [(row.filter_id, row.description) for row in rptfilter]
        filter = SelectField(u'Filter:', validators=[DataRequired()], id='filter',
                             choices=filter_choice, default=filter_choice[0][0])
        #
        start_field = StringField()
        end_field = StringField()
        start_date = DateField('Start Date', default=datetime.today() - timedelta(days=30))
        end_date = DateField('End Date', default=datetime.today())

        categoty_choice = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
        donation_name = SelectField(u'Donation Name:', validators=[DataRequired()], id='donation_name',
                                    choices=categoty_choice)

        categoty_choice = [(row.type_code, row.type_description) for row in GroupType.query.all()]
        group_name = SelectField(u'Group Name:', validators=[DataRequired()], id='group_name',
                                 choices=categoty_choice)
    # ------------------------------------------------------------------------------------------------------



class PickCounty(FlaskForm):
    form_name = HiddenField('Form Name')
    state = SelectField('State:', validators=[DataRequired()], id='select_state')
    county = SelectField('County:', validators=[DataRequired()], id='select_county')
    submit = SubmitField('Select County!')


class GroupSelect(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = Select()


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class MultiCheckSelectField(SelectMultipleField, SelectField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    option_widget2 = Select()


class ReportBackendForm(FlaskForm):
    # Report Name
    report_id = StringField('Report ID')
    report_name = StringField('Report Name')
    report_header = StringField('Report Header')
    query_stmt = TextAreaField('Query Statement')

    # ReportFilterField
    field_id = StringField('Filter Field ID')
    filter_field = StringField('Filter Field')
    filter_header = StringField('Field Header')

    # ReportFilter
    action_choice = [(row.filter_id, row.description) for row in ReportFilter.query.all()]
    action = MultiCheckboxField('Operator', choices=action_choice)


class GroupMemberForm(FlaskForm):
    member_id = StringField('Membership ID', validators=[DataRequired('*')])
    member_name = StringField('Member Name')
    group_choice = [(row.type_code, row.type_description) for row in GroupType.query.all()]
    group = MultiCheckboxField('Groups', choices=group_choice)
    get_group = SubmitField('Get User Group')


class EditUserForm(FlaskForm):
    username = StringField('UserName', validators=[DataRequired('*')])
    fullname = StringField('Name', validators=[optional()])
    # firstname = StringField('Firstname', validators=[DataRequired('*')])
    email = StringField('email')
    admin_option = RadioField('Label', choices=[('0', 'Non-Admin'), ('1', 'Admin'), ('2', 'Super Admin')], default='0')
    su_option = RadioField('Label', choices=[('0', 'Non-Admin'), ('1', 'Admin')], default='0')

    get_user = SubmitField('Get User Detail')


class ChangePasswordForm(FlaskForm):
    # username = StringField('Username',  validators=[optional()]) #, validators=[DataRequired()]
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    cancel = SubmitField('Cancel')
    submit = SubmitField('Change Password')


class ChallengeForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])  # , validators=[DataRequired()]
    challenge_1 = PasswordField(validators=[optional()])
    challenge_2 = PasswordField(validators=[optional()])
    cancel = SubmitField('Cancel')
    submit = SubmitField('Submit')
    get_quest = SubmitField('Challenge')


class FamilyMemberForm(FlaskForm):
    family_id = StringField('Family ID', validators=[DataRequired('*')])
    family_name = StringField('Family Name')
    family_alert = StringField('')
    family_member_name = StringField('Member Name')
    #
    relation_id = SelectField('Relationship Type:', validators=[DataRequired('*')], id='relation_id')
    relation_choices = [(row.relation_id, row.relation_description) for row in FamilyRelation.query.all()]
    relation_choices.insert(0, ('', 'Select Member Type'))
    relation_id.choices = (relation_choices)
    get_family = SubmitField('Get Family Members')


class LicenseForm(FlaskForm):
    activation_code = StringField('Activation Code', validators=[DataRequired('*')])


class RedFlagForm(FlaskForm):
    redflag_mark = StringField('Redflag Marker', validators=[DataRequired('*')])
    analyze_year = StringField('Year to Analyze', validators=[optional()])
    analyze_option = RadioField('Label', choices=[('all', ' All'), ('one', 'Single'), ('year', 'Year')], default='all')
    donation_code = SelectField('Donation Name:', validators=[optional()], id='donation_code')
    donation_choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    donation_choices.insert(0, ('', 'Select Member Type'))
    donation_code.choices = (donation_choices)
    btnview = SubmitField('View Report')
    btnprint = SubmitField('Print Report')
    btndownload = SubmitField('Download')


class PaymentAnalysisForm(FlaskForm):
    analyze_year = StringField('Year to Analyze', validators=[optional()])
    analyze_option = RadioField('Label', choices=[('all', ' All'), ('one', 'Single'), ('year', 'Year')], default='all')
    analyze_interval = RadioField('Label', choices=[('10', '10'), ('20', '20'), ('25', '25')], default='25')
    donation_code = SelectField('Donation Name:', validators=[optional()], id='donation_code')
    donation_choices = [(row.type_code, row.type_description) for row in TypeOfDonation.query.all()]
    donation_choices.insert(0, ('', 'Select Member Type'))
    donation_code.choices = (donation_choices)
    btnview = SubmitField('View Report')
    btnprint = SubmitField('Print Report')
    btndownload = SubmitField('Download')
