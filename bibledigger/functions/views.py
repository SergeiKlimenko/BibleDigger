from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from bibledigger import db
from .forms import browseForm, parallelForm
from bibledigger.models import Book, Language, Translation, Text


functions = Blueprint('functions', __name__)


@functions.route('/browse', methods=['GET', 'POST'])
def browse():

    form = browseForm()

    ###TO DO: Make a new db with translation names edited as below:
    #translationList = [(tran.id,
    #    tran.translation.split('--')[1].split('_(')[0].replace('_', ' '))
    #    for tran in Translation.query.filter_by(language_id=8).all()]

    form.translation1.choices = [(tran.id, tran.translation) for tran
       in Translation.query.filter_by(language_id=1).all()]

    #if request.method == 'POST':
    #    translation1 = Translation.query.filter_by(id=form.translation1.data).first()
    #    return f'<h1>Language: {form.language1.data}, Translation: {translation1.translation}</h1>'

    if form.validate_on_submit():
        #print(form.errors)
        ###
        data = request.form
        print(data)
        data = request.data
        print(data)
        ###
        tran1Text = Text.query.filter_by(translation_id=form.translation1.data,\
            book_code=form.book.data).join(Book).with_entities(Text.id, \
            Book.title, Text.chapter, Text.verse, Text.text).all()
        textLength = len(tran1Text)
        return render_template('browse.html', form=form, tran1Text=tran1Text, textLength=textLength)
    else:
        print(form.errors)

    return render_template('browse.html', form=form)


@functions.route('/translation1/<language1>')
def translation(language1):
    translations = Translation.query.filter_by(language_id=language1).all()

    translationArray = []

    for translation in translations:
        translationObj = {}
        translationObj['id'] = translation.id
        translationObj['translation'] = translation.translation
        translationArray.append(translationObj)

    return jsonify({'translations': translationArray})


@functions.route('/parallel', methods=['GET', 'POST'])
def parallel():

    form = parallelForm()

    form.translation1.choices = [(tran.id, tran.translation) for tran
       in Translation.query.filter_by(language_id=form.language1.data).all()]
    form.translation2.choices = [(tran.id, tran.translation) for tran
        in Translation.query.filter_by(language_id=form.language2.data).all()]

    if form.validate_on_submit():
        #print(form.errors)
        data = request.form
        print(data)
        data = request.data
        print(data)

        bothTranslations = list(db.engine.execute(f"SELECT a.id, d.title, a.chapter, \
            a.verse, a.text, b.text FROM ((SELECT * FROM texts \
            WHERE translation_id = {form.translation1.data} and book_code = \
            '{form.book.data}') a LEFT JOIN (SELECT * FROM texts \
            WHERE translation_id = {form.translation2.data} \
            and book_code = '{form.book.data}') b ON a.book_code = b.book_code \
            AND a.chapter = b.chapter AND a.verse = b.verse) c LEFT JOIN books d \
            ON 	c.book_code = d.code"))
        textLength = len(list(bothTranslations))

        return render_template('parallel.html', form=form,
            bothTranslations=bothTranslations, textLength=textLength)
    else:
        print(form.errors) ###DELETE

    return render_template('parallel.html', form=form)
