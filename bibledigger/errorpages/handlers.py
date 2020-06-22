from flask import Blueprint, render_template


errorpages = Blueprint('error_pages', __name__)


@errorpages.app_errorhandler(404)
def error_404(error):
    return render_template('errorpages/404.html'), 404


@errorpages.app_errorhandler(500)
def error_500(error):
    return render_template('errorpages/500.html'), 500
