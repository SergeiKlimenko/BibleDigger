import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

app = Flask(__name__)


###CONFIG###
app.config['SECRET_KEY'] = 'hugesecret'
############


###DATABASE SETUP###
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLACHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)
####################

bootstrap = Bootstrap(app)

###BLUEPRINT CONFIG###
from bibledigger.core.views import core
from bibledigger.errorpages.handlers import errorpages
from bibledigger.functions.views import functions

app.register_blueprint(core)
app.register_blueprint(errorpages)
app.register_blueprint(functions)
######################
