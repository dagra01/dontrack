import os

basedir = os.path.abspath(os.path.dirname(__file__))
# print(basedir)

POSTGRES_URL = "127.0.0.1:5432"
POSTGRES_USER = "db_donatrack"
POSTGRES_PW = "123456"
# POSTGRES_DB="Donatrack"
POSTGRES_DB = "donatrack_web"

ENV = 'prod'

if ENV == 'dev':
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL,
                                                                   db=POSTGRES_DB)
else:
    DB_URL = 'postgres://tpfjxtmbkfvmpc:db466fd20fb5acd1a5f3486cb502640c5d8c273a8c7180dfbb2ef2ef26dd1cd6@ec2-3-222-150-253.compute-1.amazonaws.com:5432/d7rcj7rgtc3ao'

DBDIR = 'sqlite:///' + os.path.join(basedir, 'donatrack.db')
sqlite_path = os.path.join(basedir, 'donatrack.db')
upload_folder = os.path.join(basedir, 'uploads')
#upload_folder = os.path.join('app/', 'uploads')

backup_folder = os.path.join(basedir, 'backup')
old_db_sqlite_path = os.path.join(backup_folder, 'donatrack-old.db')
download_folder = os.path.join(basedir, 'downloads')
wkhtmltopdf_folder = os.path.join(basedir, 'wkhtmltopdf', 'bin')
error_folder = os.path.join(os.path.abspath(os.getcwd()), 'errorlog')
license_count = os.path.join(basedir, 'clds.dat')
license_bck_file = os.path.join(basedir, 'bkclds.dat')
lic_folder = os.path.join(os.path.abspath(os.getcwd()), 'lic')


# error_folder = os.path.join(basedir, 'errorlog')
# print(error_folder1)
# print(error_folder)

# basedir33 = os.path.abspath(os.getcwd())
# error_folder = os.path.join(basedir33, 'errorlog')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'get-me-if-you-can'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLITE_PATH = sqlite_path
    OLD_DB_SQLITE_PATH = old_db_sqlite_path
    LICENSE_FOLDER = lic_folder
    LICENSE_BACKUP_FILE = license_bck_file
    UPLOAD_FOLDER = upload_folder
    DOWNLOAD_FOLDER = download_folder
    BACKUP_FOLDER = backup_folder
    ERROR_FOLDER = error_folder
    LICENSE_COUNT = license_count
    BASE_DIR = basedir
    WKHTMLTOPDF_FOLDER = wkhtmltopdf_folder

    # ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
