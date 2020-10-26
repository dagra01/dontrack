import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


from config import Config

# from app import routes

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

if not app.debug:
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    logging.warning('is when this event was logged.')
    error_folder = os.path.join(os.path.abspath(os.getcwd()), 'errorlog')
    file_handler = RotatingFileHandler(os.path.join(error_folder, 'system_error.log'), maxBytes=1024000, backupCount=1)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

app.config.from_object(Config)
db = SQLAlchemy(app)
##bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
migrate = Migrate(app, db)

from app import routes, models, errors

