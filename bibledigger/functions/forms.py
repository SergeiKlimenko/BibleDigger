from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField, RadioField, \
                    StringField, IntegerField
from wtforms.validators import DataRequired, optional
from  ..models import Book, Language, Translation, Text


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

    submit = SubmitField('OK')


class verseSearchForm(FlaskForm):

    anotherVerse = BooleanField('Add another verse?')

    submit = SubmitField('OK')


class parallelVerseSearchForm(FlaskForm):

    anotherVerse = BooleanField('Add another verse?')

    submit = SubmitField('OK')


class wordListForm(FieldsRequiredForm):

    search = StringField('Search for:', id="wordListSearch")
    caseSensitive = BooleanField('Case sensitive')

    searchOptions = RadioField('Search options', choices=[('all', 'all'), ('start', 'starting with'),
        ('end', 'ending with'), ('cont', 'containing'), ('regex', 'matching regex')])

    freqMin = IntegerField('freq min', validators=[optional(strip_whitespace=True)])
    freqMax = IntegerField('freq max', validators=[optional(strip_whitespace=True)])

    orderOptions = RadioField('Order by', choices=[('word', 'order by word'), ('freq', 'order by frequency')])

    submit = SubmitField('OK')


class concordanceForm(FieldsRequiredForm):

    search = StringField('Search for:', validators=[DataRequired()])

    searchOptions = RadioField('Search options', choices=[('word', 'whole word'),
         ('start', 'starting with'), ('end', 'ending with'), ('cont', 'containing'),
         ('regex', 'matching regex')])

    caseSensitive = BooleanField('Case sensitive')

    submit = SubmitField('OK')
