from flask import render_template, request, Blueprint
from bibledigger import db

core = Blueprint('core', __name__)


@core.route('/')
def index():
    languagesNo = db.engine.execute("SELECT COUNT(*) FROM languages").fetchone()[0]
    translationsNo = db.engine.execute("SELECT COUNT(*) FROM translations").fetchone()[0]

    return render_template('index.html',
                            languagesNo=languagesNo,
                            translationsNo=translationsNo)
