from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

db = SQLAlchemy()


def init_app():
    """Initialie the core application"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config')

    #Initialie plugins
    db.init_app(app)

    with app.app_context():
        ###BLUEPRINT CONFIG###
        from bibledigger.core.views import core
        from bibledigger.errorpages.handlers import errorpages
        from bibledigger.functions.views import functions

        app.register_blueprint(core)
        app.register_blueprint(errorpages)
        app.register_blueprint(functions)
        ######################

        Migrate(app, db)
        bootstrap = Bootstrap(app)
        ####################

        return app




