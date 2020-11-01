from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField, RadioField, \
                    StringField, IntegerField
from wtforms.validators import DataRequired, optional
from  ..models import Book, Language, Translation, Text


languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
#bookChoices = [(book.code, book.title) for book in Book.query.all()]


class FieldsRequiredForm(FlaskForm):
    """Require all fields to have content. This works around the bug that WTForms radio
    fields don't honor the `DataRequired` or `InputRequired` validators.
    """

    class Meta:
        def render_field(self, field, render_kw):
            if type(field) != BooleanField and type(field) != IntegerField and field.id != 'wordListSearch':
                render_kw.setdefault('required', True)
            return super().render_field(field, render_kw)


class browseForm(FlaskForm):

    language1 = SelectField('language', choices=languageChoices, coerce=int, validators=[DataRequired()])
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


class wordListForm(FieldsRequiredForm):

    search = StringField('What are you looking for?', id="wordListSearch")
    caseSensitive = BooleanField('Case sensitive')

    searchOptions = RadioField('Search options', choices=[('all', 'all'), ('start', 'starting with'),
        ('end', 'ending with'), ('cont', 'containing'), ('regex', 'matching regex')])

    freqMin = IntegerField('freq min', validators=[optional(strip_whitespace=True)])
    freqMax = IntegerField('freq max', validators=[optional(strip_whitespace=True)])

    orderOptions = RadioField('Order by', choices=[('word', 'order by word'), ('freq', 'order by frequency')])

    submit = SubmitField('OK')


class concordanceForm(FieldsRequiredForm):

    search = StringField('What are you looking for?', validators=[DataRequired()])

    searchOptions = RadioField('Search options', choices=[('word', 'whole word'),
         ('start', 'starting with'), ('end', 'ending with'), ('cont', 'containing'),
         ('regex', 'matching regex')])

    caseSensitive = BooleanField('Case sensitive')

    submit = SubmitField('OK')
