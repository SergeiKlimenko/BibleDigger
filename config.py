from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))


###FLASK CONFIG VARIABLES###
load_dotenv(path.join(basedir, '.env'))
SECRET_KEY = environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")


 ###DATABASE SETUP###
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'data.sqlite')
SQLACHEMY_TRACK_MODIFICATIONS = False