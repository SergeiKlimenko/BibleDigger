from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from  ..models import Book, Language, Translation, Text


class browseForm(FlaskForm):

    languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
    language1 = SelectField('Select a language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('Select a translation', coerce=int, validators=[DataRequired()])

    submit = SubmitField('OK')

    anotherTranslation = BooleanField('See a parallel translation?', default=False)

    language2 = SelectField('Select a language', choices=languageChoices, coerce=int)
    translation2 = SelectField('Select a translation', coerce=int)
