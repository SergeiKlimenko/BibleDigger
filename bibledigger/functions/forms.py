from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from  ..models import Book, Language, Translation, Text


languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
#bookChoices = [(book.code, book.title) for book in Book.query.all()]


class browseForm(FlaskForm):

    language1 = SelectField('Select a language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('Select a translation', coerce=int, validators=[DataRequired()], validate_choice=False)

    book = SelectField('Select a book', validators=[DataRequired()])

    submit = SubmitField('OK')


class parallelForm(FlaskForm):

    language1 = SelectField('Select a language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('Select a translation', coerce=int, validators=[DataRequired()], validate_choice=False)

    language2 = SelectField('Select a language', choices=languageChoices, coerce=int)
    translation2 = SelectField('Select a translation', coerce=int, validate_choice=False)

    book = SelectField('Select a book', validators=[DataRequired()])

    submit = SubmitField('OK')


class verseSearchForm(FlaskForm):

    language1 = SelectField('language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('translation', coerce=int, validators=[DataRequired()], validate_choice=False)

    book = SelectField('book', validators=[DataRequired()])
    chapter = SelectField('chapter', coerce=int, validate_choice=False)
    verse = SelectField('verse', coerce=int, validate_choice=False)

    anotherVerse = BooleanField('Add another verse?')

    submit = SubmitField('OK')


class parallelVerseSearchForm(FlaskForm):

    language1 = SelectField('language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('translation', coerce=int, validators=[DataRequired()], validate_choice=False)

    language2 = SelectField('language', choices=languageChoices, coerce=int)
    translation2 = SelectField('translation', coerce=int, validate_choice=False)

    book = SelectField('book', validators=[DataRequired()])
    chapter = SelectField('chapter', coerce=int, validate_choice=False)
    verse = SelectField('verse', coerce=int, validate_choice=False)

    anotherVerse = BooleanField('Add another verse?')

    submit = SubmitField('OK')
