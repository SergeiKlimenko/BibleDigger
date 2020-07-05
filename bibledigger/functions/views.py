from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, session
from bibledigger import db
from .forms import browseForm, parallelForm, verseSearchForm, parallelVerseSearchForm, wordListForm
from bibledigger.models import Book, Language, Translation, Text


functions = Blueprint('functions', __name__)


@functions.route('/browse', methods=['GET', 'POST'])
def browse():

    form = browseForm()

    ###TO DO: Make a new db with translation names edited as below:
    #translationList = [(tran.id,
    #    tran.translation.split('--')[1].split('_(')[0].replace('_', ' '))
    #    for tran in Translation.query.filter_by(language_id=8).all()]
    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=1).distinct(Text.book_code).
            join(Book).with_entities(Text.book_code, Book.title).all()]
    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=form.translation1.data).
            distinct(Text.book_code).join(Book).with_entities(Text.book_code,
            Book.title).all()]

    if form.validate_on_submit():
        #print(form.errors)
        ###
        data = request.form
        print(data)
        data = request.data
        print(data)
        ###
        translation1 = Translation.query.filter_by(id=form.translation1.data).first().id
        tran1Text = Text.query.filter_by(translation_id=translation1,\
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


@functions.route('/book/<translation1>')
def book(translation1):
    books = list(db.engine.execute(f"SELECT DISTINCT a.book_code, b.title \
        FROM texts a LEFT JOIN books b ON a.book_code = b.code \
        WHERE translation_id = {translation1}"))
    bookArray = []

    for book in books:
        bookObj = {}
        bookObj['id'] = book[0]
        bookObj['book'] = book[1]
        bookArray.append(bookObj)

    return jsonify({'books': bookArray})


@functions.route('/parallel', methods=['GET', 'POST'])
def parallel():

    form = parallelForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        form.translation2.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=1).distinct(Text.book_code).
            join(Book).with_entities(Text.book_code, Book.title).all()]
    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]
        form.translation2.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language2.data).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=form.translation1.data).
            distinct(Text.book_code).join(Book).with_entities(Text.book_code,
            Book.title).all()]

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
            WHERE translation_id = {form.translation2.data}) b ON \
            a.book_code = b.book_code AND a.chapter = b.chapter \
            AND a.verse = b.verse) c LEFT JOIN books d ON c.book_code = d.code"))
        textLength = len(list(bothTranslations))

        return render_template('parallel.html', form=form,
            bothTranslations=bothTranslations, textLength=textLength)
    else:
            print(form.errors) ###DELETE

    return render_template('parallel.html', form=form)


@functions.route('/verseSearch', methods=['GET', 'POST'])
def verseSearch():

    form = verseSearchForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=1).distinct(Text.book_code).
            join(Book).with_entities(Text.book_code, Book.title).all()]
        form.chapter.choices = [(verse.chapter, verse.chapter) for verse
            in list(db.engine.execute("SELECT DISTINCT chapter FROM texts \
            WHERE translation_id = 1 AND book_code = 'GEN' ORDER BY id"))]
        form.verse.choices = [(verse.verse, verse.verse) for verse
            in list(db.engine.execute(f"SELECT DISTINCT verse FROM texts \
            WHERE translation_id = 1 AND book_code = 'GEN' AND chapter = 1 \
            ORDER BY id"))]

    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=form.translation1.data).
            distinct(Text.book_code).join(Book).with_entities(Text.book_code,
            Book.title).all()]
        form.chapter.choices = [(verse.chapter, verse.chapter) for verse
            in list(db.engine.execute(f"SELECT DISTINCT chapter FROM texts \
            WHERE translation_id = {form.translation1.data} AND \
            book_code = '{form.book.data}' ORDER BY id"))]
        form.verse.choices = [(verse.verse, verse.verse) for verse
            in list(db.engine.execute(f"SELECT DISTINCT verse FROM texts \
            WHERE translation_id = {form.translation1.data} AND book_code = \
            '{form.book.data}' AND chapter = {form.chapter.data} \
            ORDER BY id"))]

    if form.validate_on_submit():
        anotherVerse = form.anotherVerse.data

        book = db.engine.execute(f"SELECT title FROM books WHERE code = \
        '{form.book.data}'").fetchone().title
        language1 = db.engine.execute(f"SELECT language FROM languages \
            WHERE id = {form.language1.data}").fetchone().language
        translation1 = db.engine.execute(f"SELECT translation FROM translations \
            WHERE id = {form.translation1.data}").fetchone().translation

        session[(form.book.data, form.chapter.data, form.verse.data, language1,
            translation1)] = (book, form.chapter.data, form.verse.data, language1,
            translation1)

        verseList = list(session.values())[1:]
        print(verseList)
        print(list(session)[1:])
        if anotherVerse == True:
            return render_template('versesearch.html', form=form,
                anotherVerse=anotherVerse, verseToRender=verseList)
        else:
            verseToRender = []

            for item in list(session)[1:]:
                verse = db.engine.execute(f"SELECT a.id AS id, b.title AS title, \
                    a.chapter AS chapter, a.verse AS verse, a.text AS text1 \
                    FROM texts a LEFT JOIN books b ON a.book_code = b.code \
                    WHERE a.translation_id = {form.translation1.data} and \
                    a.book_code = '{item[0]}' and a.chapter = '{item[1]}' and \
                    a.verse = '{item[2]}'").fetchone()

                verseToRender.append((verse.title + " " + verse.chapter + ":" +
                    str(verse.verse), verse.text1, item[3], item[4]))

                print(verseToRender)

            sessionKeys = list(session.keys())
            for k in sessionKeys:
                if k != 'csrf_token' and k != '_permanent':
                    session.pop(k)

            return render_template('versesearch.html', form=form,
                anotherVerse=anotherVerse, verseToRender=verseToRender)

    else:
        print(form.errors) ###DELETE

    return render_template('versesearch.html', form=form)


@functions.route('/parallelverseSearch', methods=['GET', 'POST'])
def parallelVerseSearch():

    form = parallelVerseSearchForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        form.translation2.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=1).distinct(Text.book_code).
            join(Book).with_entities(Text.book_code, Book.title).all()]
        form.chapter.choices = [(verse.chapter, verse.chapter) for verse
            in list(db.engine.execute("SELECT DISTINCT chapter FROM texts \
            WHERE translation_id = 1 AND book_code = 'GEN' ORDER BY id"))]
        form.verse.choices = [(verse.verse, verse.verse) for verse
            in list(db.engine.execute(f"SELECT DISTINCT verse FROM texts \
            WHERE translation_id = 1 AND book_code = 'GEN' AND chapter = 1 \
            ORDER BY id"))]

    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]
        form.translation2.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language2.data).all()]
        form.book.choices = [(book.book_code, book.title) for book
            in Text.query.filter_by(translation_id=form.translation1.data).
            distinct(Text.book_code).join(Book).with_entities(Text.book_code,
            Book.title).all()]
        form.chapter.choices = [(verse.chapter, verse.chapter) for verse
            in list(db.engine.execute(f"SELECT DISTINCT chapter FROM texts \
            WHERE translation_id = {form.translation1.data} AND \
            book_code = '{form.book.data}' ORDER BY id"))]
        form.verse.choices = [(verse.verse, verse.verse) for verse
            in list(db.engine.execute(f"SELECT DISTINCT verse FROM texts \
            WHERE translation_id = {form.translation1.data} AND book_code = \
            '{form.book.data}' AND chapter = {form.chapter.data} \
            ORDER BY id"))]

    if form.validate_on_submit():
        anotherVerse = form.anotherVerse.data

        book = db.engine.execute(f"SELECT title FROM books WHERE code = \
        '{form.book.data}'").fetchone().title
        language1 = db.engine.execute(f"SELECT language FROM languages \
            WHERE id = {form.language1.data}").fetchone().language
        translation1 = db.engine.execute(f"SELECT translation FROM translations \
            WHERE id = {form.translation1.data}").fetchone().translation
        language2 = db.engine.execute(f"SELECT language FROM languages \
            WHERE id = {form.language2.data}").fetchone().language
        translation2 = db.engine.execute(f"SELECT translation FROM translations \
            WHERE id = {form.translation2.data}").fetchone().translation

        session[(form.book.data, form.chapter.data, form.verse.data, language1,
            translation1, language2, translation2)] = (book, form.chapter.data,
            form.verse.data, language1, translation1, language2, translation2)

        verseList = list(session.values())[1:]
        print(verseList)
        print(list(session)[1:])
        if anotherVerse == True:
            return render_template('parallelversesearch.html', form=form,
                anotherVerse=anotherVerse, verseToRender=verseList)
        else:
            verseToRender = []

            for item in list(session)[1:]:
                verse = db.engine.execute(f"SELECT a.id AS id, d.title AS title, \
                    a.chapter AS chapter, a.verse AS verse, a.text AS text1, \
                    b.text AS text2 FROM ((SELECT * FROM texts \
                    WHERE translation_id = {form.translation1.data} and book_code = \
                    '{item[0]}' and chapter = '{item[1]}' and \
                    verse = '{item[2]}') a LEFT JOIN (SELECT * FROM texts \
                    WHERE translation_id = {form.translation2.data}) b ON \
                    a.book_code = b.book_code AND a.chapter = b.chapter \
                    AND a.verse = b.verse) c LEFT JOIN books d ON c.book_code = d.code").fetchone()

                verseToRender.append((verse.title + " " + verse.chapter + ":" +
                    str(verse.verse), verse.text1, verse.text2,
                    item[3], item[4],
                    item[5], item[6]))

                print(verseToRender)

            sessionKeys = list(session.keys())
            for k in sessionKeys:
                if k != 'csrf_token' and k != '_permanent':
                    session.pop(k)

            return render_template('parallelversesearch.html', form=form,
                anotherVerse=anotherVerse, verseToRender=verseToRender)

    else:
        print(form.errors)

    return render_template('parallelversesearch.html', form=form)


@functions.route('/chapter/<book>/<translation_id>')
def chapter(translation_id, book):
    chapters = list(db.engine.execute(f"SELECT DISTINCT chapter \
        FROM texts WHERE translation_id = {translation_id} AND \
        book_code = '{book}' ORDER BY id"))
    chapterArray = []

    for chapter in chapters:
        chapterObj = {}
        chapterObj['id'] = chapter[0]
        chapterObj['chapter'] = chapter[0]
        chapterArray.append(chapterObj)

    return jsonify({'chapters': chapterArray})


@functions.route('/verse/<chapter>/<book>/<translation_id>')
def verse(translation_id, book, chapter):
    verses = list(db.engine.execute(f"SELECT DISTINCT verse \
        FROM texts WHERE translation_id = {translation_id} AND \
        book_code = '{book}' AND chapter = '{chapter}' ORDER BY id"))
    verseArray = []

    for verse in verses:
        verseObj = {}
        verseObj['id'] = verse[0]
        verseObj['verse'] = verse[0]
        verseArray.append(verseObj)

    return jsonify({'verses': verseArray})


@functions.route('/wordlist', methods=['GET', 'POST'])
def wordList():

    form = wordListForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]

    if form.validate_on_submit():

        fullText = Text.query.filter_by(translation_id=form.translation1.data).with_entities(Text.text).all()

        verseList = []

        for verse in fullText:

            verse = verse[0].replace('—', ' ').split()
            strippedVerse = []
            for word in verse:
                if form.caseSensitive.data == True:
                    strippedVerse.append(word.strip(',.()[];:""“”?!—/\\-+=_<>').
                        strip(",.()[];:''‘’‛“”?!—/\\-+=_<>"))
                elif form.caseSensitive.data == False:
                    strippedVerse.append(word.lower().strip(',.()[];:""“”?!—/\\-+=_<>').
                        strip(",.()[];:''‘’‛“”?!—/\\-+=_<>"))
            verseList += strippedVerse
            #verseList.append(verse)

        from collections import Counter
        wordList = Counter(verseList)

        sortedWordList = []

        for k, v in wordList.items():
            if k == '':
                continue
            if form.freqMin.data != None:
                if v < form.freqMin.data:
                    continue
            if form.freqMax.data != None:
                if v > form.freqMax.data:
                    continue
            sortedWordList.append((v, k))

        if form.orderOptions.data == 'freq':
            sortedWordList.sort(key=lambda tup: tup[1])
            sortedWordList.sort(key=lambda tup: tup[0], reverse=True)
        elif form.orderOptions.data == 'word':
            sortedWordList.sort(key=lambda tup: tup[0], reverse=True)
            sortedWordList.sort(key=lambda tup: tup[1])

        words = []

        if form.searchOptions.data == 'all':
            words = sortedWordList
        elif form.searchOptions.data == 'start':
            for word in sortedWordList:
                if word[1].startswith(form.search.data):
                    words.append(word)
        elif form.searchOptions.data == 'end':
            for word in sortedWordList:
                if word[1].endswith(form.search.data):
                    words.append(word)
        elif form.searchOptions.data == 'cont':
            for word in sortedWordList:
                if form.search.data in word[1]:
                    words.append(word)
        elif form.searchOptions.data == 'regex':
            import re
            regex = re.compile(form.search.data)
            for word in sortedWordList:
                if re.search(regex, word[1]):
                    words.append(word)

        wordsLength = len(words)

        return render_template('wordlist.html', form=form, words=words, wordsLength=wordsLength)

    else:
        print(form.errors)

    wordsLength = -1

    return render_template('wordlist.html', form=form, wordsLength=wordsLength)
