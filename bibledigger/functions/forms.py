from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField, RadioField, \
                    StringField, IntegerField
from wtforms.validators import DataRequired, optional
from  ..models import Book, Language, Translation, Text


languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
#bookChoices = [(book.code, book.title) for book in Book.query.all()]


class browseForm(FlaskForm):

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


class wordListForm(FlaskForm):

    language1 = SelectField('language', choices=languageChoices, coerce=int, validators=[DataRequired()])
    translation1 = SelectField('translation', coerce=int, validators=[DataRequired()], validate_choice=False)


    search = StringField('What are you looking for?')
    caseSensitive = BooleanField('Case sensitive')

    searchOptions = RadioField('Search options', choices=[('all', 'all'), ('start', 'starting with'),
        ('end', 'ending with'), ('cont', 'containing'), ('regex', 'matching regex')])

    freqMin = IntegerField('freq min', validators=[optional(strip_whitespace=True)])
    freqMax = IntegerField('freq max', validators=[optional(strip_whitespace=True)])

    orderOptions = RadioField('Order by', choices=[('word', 'order by word'), ('freq', 'order by frequency')])

    submit = SubmitField('OK')


class concordanceForm(FlaskForm):

    search = StringField('What are you looking for?')

    searchOptions = RadioField('Search options', choices=[('word', 'whole word'),
         ('start', 'starting with'), ('end', 'ending with'), ('cont', 'containing'),
         ('regex', 'matching regex')])

    caseSensitive = BooleanField('Case sensitive')

    submit = SubmitField('OK')

    choices = [(None, 'none'), (0, 'verse'), (32, '3R'), (31, '2R'), (30, '1R'),
             (2, 'KWIC'), (11, '1L'), (12, '2L'), (13, '3L')]

    option8 = SelectField('Level8', choices=choices, validate_choice=False)

class concordanceSortForm(FlaskForm):

    # choices = [(None, 'none'), (0, 'verse'), (32, '3R'), (31, '2R'), (30, '1R'),
    #              (2, 'KWIC'), (11, '1L'), (12, '2L'), (13, '3L')]
    # # #
    # option1 = SelectField('Level1', choices=choices, validate_choice=False)
    # option2 = SelectField('Level2', choices=choices, validate_choice=False)
    # option3 = SelectField('Level3', choices=choices, validate_choice=False)
    # option4 = SelectField('Level4', choices=choices, validate_choice=False)
    # option5 = SelectField('Level5', choices=choices, validate_choice=False)
    # option6 = SelectField('Level6', choices=choices, validate_choice=False)
    # option7 = SelectField('Level7', choices=choices, validate_choice=False)
    # option8 = SelectField('Level8', choices=choices, validate_choice=False)

    sort = SubmitField('OK')
