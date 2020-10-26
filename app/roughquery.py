import sqlite3
from app import app


def db_connection():
    sqlite_file = app.config['SQLITE_PATH']
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()
    return cursor


class MemberDonationRpt(object):
    """List of payment for a category for a member

    Class Name:
    List of payment for a category for a member

    Description:
    List the payments made by a member for a particular  a category of donation
    and statment of account

    Modules:
    list_payments : list the payments
    stmt_of_acct : sums total paid and  calculates outstanding

    Parameter:
    donation_id : the  id that uniquely identifies the member's donation

    """

    def __init__(self, **kwargs):
        self.donation_id = kwargs.get('donation_id')
        self.member_id = kwargs.get('member_id')

    def list_payments(self):
        stmt = """SELECT typeofdonation.type_description AS [Donation Name], 
                     strftime('%d-%m-%Y',donationtrail.payment_date) AS Date, donationtrail.amount AS Paid,
                           donationtrail.payment_details,
                           donationtrail.donation_type_ID,
                           members.member_Firstname AS Firstname,
                           members.member_lastname AS Surname,
                           members.member_phone_no AS [Mobile No.]
                      FROM donationtrail,
                           typeofdonation,
                           members,
                           donations
                     WHERE donationtrail.donation_id = donations.donation_id AND
                           donationtrail.donation_type_id = typeofdonation.type_code AND
                           members.member_id = donations.member_id AND 
                           donations.donation_id {} '{}';""".format('=', 10)
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt

    def stmt_of_acct(self):
        stmt = """SELECT typeofdonation.type_description AS [Donation Name],
                           sum(donationtrail.amount) AS Paid,
                           donations.amount AS Pledged,
                           sum(donationtrail.amount) - donations.amount AS Outstanding,
                           donation_type_ID,
                           members.member_Firstname AS Firstname,
                           members.member_lastname AS Surname,
                           members.member_phone_no AS [Mobile No.]
                      FROM donationtrail,
                           typeofdonation,
                           members,
                           donations
                     WHERE donationtrail.donation_id = donations.donation_id AND
                           donationtrail.donation_type_id = typeofdonation.type_code AND 
                           members.member_id = donations.member_id AND 
                           donations.donation_id {} ' {} ';"""
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt

    def member_stmt_of_acct(self):
        stmt = """SELECT typeofdonation.type_description AS [Donation Name],
                           sum(donationtrail.amount) AS Paid,
                           donations.amount AS Pledged,
                           sum(donationtrail.amount) - donations.amount AS Outstanding,
                           donation_type_ID,
                           members.member_Firstname AS Firstname,
                           members.member_lastname AS Surname,
                           members.member_phone_no AS [Mobile No.]
                      FROM donationtrail,
                           typeofdonation,
                           members,
                           donations
                     WHERE donationtrail.donation_id = donations.donation_id AND
                           donationtrail.donation_type_id = typeofdonation.type_code AND 
                           members.member_id = donations.member_id AND 
                           Members.member_id  {} '{}';"""
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt


class DonationCategoryRpt(object):

    def __init__(self, **kwargs):
        self.donation_type_id = kwargs.get("donation_type_id")
        self.start_date = kwargs.get("start_date")
        self.end_date = kwargs.get("end_date")
        self.start_amount = kwargs.get("start_amount")
        self.end_amount = kwargs.get("end_amount")

    def category_transaction(self):
        stmt = """SELECT (SELECT TypeOfDonation.type_description,
                                FROM TypeOfDonation
                                WHERE TypeOfDonation.type_code = donations.donation_type_id)
                           AS [Donation Name],
                           strftime('%d-%m-%Y',Donationtrail.payment_date) AS Date,
                           donations.amount AS [Amount Pledged],
                           (SELECT IFNULL(sum(Donationtrail.amount), 0)
                                 FROM Donationtrail
                                 WHERE Donationtrail.donation_id = donations.donation_id) AS [ Amount Redeemed],
                           (SELECT IFNULL(sum(Donationtrail.amount), 0) - Donations.amount
                                 FROM Donationtrail
                                WHERE Donationtrail.donation_id = donations.donation_id) AS [ Balance],
                           Members.member_lastname AS Surname,
                           Members.member_firstname AS FirstName,
                           Members.member_phone_no AS [Mobile No.]
                      FROM members,
                           donations
                     WHERE Donations.member_id = Members.member_id AND 
                           Donations.donation_type_id {} '{}'
                     ORDER BY Date(donations.donation_date) DESC;"""
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt

    def donation_by_date_range(self):
        stmt = """SELECT Members.member_lastname,
                           Members.member_firstname,
                           Donations.donation_id AS Donation ID,
                           strftime('%d-%m-%Y',(Donations.donation_date)) AS Date,
                           (SELECT TypeOfDonation.type_description
                                 FROM TypeOfDonation
                                WHERE TypeOfDonation.type_code = donations.donation_type_id)
                           AS [Donation Name],
                           donations.amount
                      FROM members,
                           donations
                     WHERE (Date(donations.donation_date) {} '{}')
                      AND  Donations.member_id = Members.member_id
                     ORDER BY Date(donations.donation_date) ASC;"""
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt

    def range_by_amount_pledged(self):
        stmt = """SELECT Members.member_lastname AS Surname,
                           Members.member_firstname AS Firstname,
                           (SELECT TypeOfDonation.type_description
                                 FROM TypeOfDonation
                                WHERE TypeOfDonation.type_code = donations.donation_type_id)
                           AS [Donation Name],
                           donations.amount AS [Amount Pledged]
                      FROM members,
                           donations
                     WHERE (donations.amount {}  {} ) 
                     AND Members.member_id = Donations.member_id
                     "order by Members.member_id;"""
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt

   

    def range_by_amount_redeemed(self):
        stmt = """SELECT Members.member_lastname AS Surname,
                           Members.member_firstname AS Firstname,
                           (
                               SELECT TypeOfDonation.type_description
                                 FROM TypeOfDonation
                                WHERE TypeOfDonation.type_code = donations.donation_type_id
                           )
                           AS [Donation Name],
                           (SELECT sum(Donationtrail.amount) 
                                 FROM Donationtrail
                                 WHERE Donationtrail.donation_id = donations.donation_id
                                 group by donation_type_id
                                 Having sum(amount) {} {} )
                                 AS [ Amount Redeemed]
                           FROM Members,
                           Donations,
                           Donationtrail,
                           TypeOfDonation 
                           WHERE Members.member_id = Donations.member_id
                           and Donations.donation_id = Donationtrail.donation_id
                           group by Donationtrail.donation_type_id;"""
        query_stmt = (stmt.replace('"""', '').replace('\n', "")).strip()
        return query_stmt

    def test_from_db(self):
        stat = """
                SELECT typeofdonation.type_description AS [Donation Name],
                       Donationtrail.donation_type_ID AS [Donation Code],
                       strftime('%d-%m-%Y', Donationtrail.payment_date) AS Date,
                       Donationtrail.amount AS Paid,
                       Donationtrail.payment_details,   

                       Members.member_Firstname AS Firstname,
                       Members.member_lastname AS Surname,
                       Members.member_phone_no AS [Mobile No.]
                FROM   Donationtrail,
                       TypeOfDonation,
                       Members,
                       Donations
                WHERE   Donationtrail.donation_id = Donations.donation_id 
                AND     Donationtrail.donation_type_id = TypeOfDonation.type_code 
                AND     Members.member_id = Monations.member_id 
                AND     Donations.donation_id = 'PR-10';
        """



        # report = ReportName.query.filter_by(report_id='MQ001').first()
        #  query_stmt = (report.query_stmt.replace('"""', '').replace('\n', "")).strip()"""
        # query_stmt.format("=","'PR-10'")

