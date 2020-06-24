from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from  ..models import Book, Language, Translation, Text


languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
bookChoices = [(book.code, book.title) for book in Book.query.all()]


class browseForm(FlaskForm):

    language1 = SelectField('Select a language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('Select a translation', coerce=int, validators=[DataRequired()])

    book = SelectField('Select a book', choices=bookChoices, validators=[DataRequired()])

    submit = SubmitField('OK')


class parallelForm(FlaskForm):

    language1 = SelectField('Select a language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('Select a translation', coerce=int, validators=[DataRequired()])

    language2 = SelectField('Select a language', choices=languageChoices, coerce=int)
    translation2 = SelectField('Select a translation', coerce=int)

    book = SelectField('Select a book', choices=bookChoices, validators=[DataRequired()])

    submit = SubmitField('OK')
