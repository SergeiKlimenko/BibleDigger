from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, session
from bibledigger import db
from .forms import browseForm, parallelForm, verseSearchForm, parallelVerseSearchForm, \
                   wordListForm, concordanceForm, concordanceSortForm
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


@functions.route('/verseSearch/<int:parallelOrNot>/', methods=['GET', 'POST'])
@functions.route('/verseSearch/<int:parallelOrNot>/<verseList>', methods=['GET', 'POST'])
def verseSearch(parallelOrNot, verseList=None):

    if parallelOrNot == 1:
        form = verseSearchForm()
    elif parallelOrNot == 2:
        form = parallelVerseSearchForm()

    #Convert string representation of verse list from route into list
    def processVerseList(verseList, fullProcess):
        verseList = [verse.split(', ') for verse in verseList.strip('[]').replace("'", '').strip('[]').split('], [')]
        if fullProcess == True:
            for verse in verseList:
                book = db.engine.execute(f"SELECT title FROM books WHERE code = \
                    '{verse[0]}'").fetchone().title
                language1 = db.engine.execute(f"SELECT language FROM languages \
                    WHERE id = {verse[3]}").fetchone().language
                translation1 = db.engine.execute(f"SELECT translation FROM translations \
                    WHERE id = {verse[4]}").fetchone().translation
                verse[0] = book
                verse[3] = language1
                verse[4] = translation1
                if parallelOrNot == 2:
                    language2 = db.engine.execute(f"SELECT language FROM languages \
                        WHERE id = {verse[5]}").fetchone().language
                    translation2 = db.engine.execute(f"SELECT translation FROM translations \
                        WHERE id = {verse[6]}").fetchone().translation
                    verse[5] = language2
                    verse[6] = translation2

        return verseList

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
        if parallelOrNot == 2:
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
        if parallelOrNot == 2:
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

        if parallelOrNot == 1:
            verse = [form.book.data, form.chapter.data, form.verse.data,
                form.language1.data, form.translation1.data]
        elif parallelOrNot == 2:
            verse = [form.book.data, form.chapter.data, form.verse.data,
                form.language1.data, form.translation1.data, form.language2.data,
                form.translation2.data]

        if verseList == None:
            verseList = []
            verseList.append(verse)
        else:
            verseList = processVerseList(verseList, False)
            verseList.append(verse)

        if anotherVerse == True:
            return redirect(url_for('functions.verseSearch', verseList=verseList,
                parallelOrNot=parallelOrNot))

        else:

            verseToRender =[]

            for item in verseList:

                language1 = db.engine.execute(f"SELECT language FROM languages \
                    WHERE id = {item[3]}").fetchone().language
                translation1 = db.engine.execute(f"SELECT translation FROM translations \
                    WHERE id = {item[4]}").fetchone().translation

                if parallelOrNot == 1:

                    verse = db.engine.execute(f"SELECT a.id AS id, b.title AS title, \
                        a.chapter AS chapter, a.verse AS verse, a.text AS text1 \
                        FROM texts a LEFT JOIN books b ON a.book_code = b.code \
                        WHERE a.translation_id = {item[4]} and \
                        a.book_code = '{item[0]}' and a.chapter = '{item[1]}' and \
                        a.verse = '{item[2]}'").fetchone()

                    verseToRender.append((verse.title + " " + verse.chapter + ":" +
                        str(verse.verse), verse.text1, language1, translation1))

                elif parallelOrNot == 2:

                    verse = db.engine.execute(f"SELECT a.id AS id, d.title AS title, \
                        a.chapter AS chapter, a.verse AS verse, a.text AS text1, \
                        b.text AS text2 FROM ((SELECT * FROM texts \
                        WHERE translation_id = {item[4]} and book_code = \
                        '{item[0]}' and chapter = '{item[1]}' and \
                        verse = '{item[2]}') a LEFT JOIN (SELECT * FROM texts \
                        WHERE translation_id = {item[6]}) b ON \
                        a.book_code = b.book_code AND a.chapter = b.chapter \
                        AND a.verse = b.verse) c LEFT JOIN books d ON c.book_code = d.code").fetchone()
                    language2 = db.engine.execute(f"SELECT language FROM languages \
                            WHERE id = {item[5]}").fetchone().language
                    translation2 = db.engine.execute(f"SELECT translation FROM \
                        translations WHERE id = {item[6]}").fetchone().translation

                    verseToRender.append((verse.title + " " + verse.chapter + ":" +
                        str(verse.verse), verse.text1, verse.text2, language1,
                        translation1, language2, translation2))

            return render_template('versesearch.html', form=form,
                anotherVerse=anotherVerse, verseToRender=verseToRender, parallelOrNot=parallelOrNot)

    else:
        print(form.errors) ###DELETE

    if verseList == None:
        return render_template('versesearch.html', form=form, parallelOrNot=parallelOrNot)
    else:
        verseList = processVerseList(verseList, True)
        return render_template('versesearch.html', form=form,
            anotherVerse=True, verseToRender=verseList, parallelOrNot=parallelOrNot)


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
                    strippedVerse.append(word.strip(',.()[];:""“”?!—/\\-+=_<>¿»«').
                        strip(",.()[];:''‘’‛“”?!—/\\-+=_<>"))
                elif form.caseSensitive.data == False:
                    strippedVerse.append(word.lower().strip(',.()[];:""“”?!—/\\-+=_<>¿»«').
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

        if form.caseSensitive.data == True:
            searchItem = form.search.data
        else:
            searchItem = form.search.data.lower()

        if form.searchOptions.data == 'all':
            words = sortedWordList
        elif form.searchOptions.data == 'start':
            for word in sortedWordList:
                if word[1].startswith(searchItem):
                    words.append(word)
        elif form.searchOptions.data == 'end':
            for word in sortedWordList:
                if word[1].endswith(searchItem):
                    words.append(word)
        elif form.searchOptions.data == 'cont':
            for word in sortedWordList:
                if searchItem in word[1]:
                    words.append(word)
        elif form.searchOptions.data == 'regex':
            import re
            regex = re.compile(searchItem)
            for word in sortedWordList:
                if re.search(regex, word[1]):
                    words.append(word)

        wordsLength = len(words)

        return render_template('wordlist.html', form=form, words=words,
                                wordsLength=wordsLength, translation_id=form.translation1.data,
                                case=form.caseSensitive.data)

    else:
        print(form.errors)

    wordsLength = -1

    return render_template('wordlist.html', form=form, wordsLength=wordsLength)


@functions.route('/concordance/', methods=['GET', 'POST'])
@functions.route('/concordance/<int:translation_id>/<searchItem>/<searchOption>/<case>',
                  methods=['GET', 'POST'])
def concordance(translation_id=None, searchItem=None, searchOption=None, case=None):

    form = concordanceForm()
    sortForm = concordanceSortForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]

    ###The concordance holder to be filled with search results
    concordanceList = []

    if form.validate_on_submit() and form.submit.data:

        translation_id = form.translation1.data
        searchItem = form.search.data
        searchOption = form.searchOptions.data
        case = form.caseSensitive.data

        return redirect(url_for('functions.concordance',
                         translation_id=translation_id, searchItem=searchItem,
                         searchOption=searchOption, case=case))

    if translation_id != None:

        text = list(db.engine.execute(f'SELECT b.title, a.chapter, a.verse, a.text \
            FROM texts a LEFT JOIN books b ON a.book_code = b.code WHERE \
            translation_id = {translation_id}'))

        if searchItem == None: ###Edit
            searchItem = form.search.data
        ###Strip the search item to avoid searching just for whitespaces
        searchItem = searchItem.strip()

        import re

        reSpecialSymbols = r'\\.^$*+?{}[]|()'

        ###Check if search item is regex to compile it accordingly
        if searchOption == 'regex' or form.searchOptions.data == 'regex':
            ###Skip the search if it consists only of dots -- Takes too long to process and not informative
            skip = True
            for character in searchItem:
                if character != '.':
                    skip = False
                    break
            if skip == True:
                return render_template('concordance.html', form=form,
                                        sortForm=sortForm, concLength=0)

            ###Catch incorrect regex
            try:
                if case == False or form.caseSensitive.data == False:
                    for symbol in searchItem:
                        symInd = searchItem.index(symbol)
                        if (searchItem[symInd-1] == '\\' and symInd == 1) or \
                            (searchItem[symInd-1] == '\\' and searchItem[symInd-2] != '\\'):
                            continue
                        else:
                            searchItem = searchItem[:symInd] + searchItem[symInd].lower() + searchItem[symInd+1:]
                searchRegex = re.compile(searchItem)
            except:
                errorMessage = 'Sorry It seems that your regular expression is incorrect. Try again. '
                return render_template('concordance.html', form=form,
                                        sortForm=sortForm, errorMessage=errorMessage)

        else:
            for symbol in reSpecialSymbols:
                searchItem = searchItem.replace(symbol, '\\' + symbol)

            if case == False or form.caseSensitive.data == False:
                searchRegex = re.compile(searchItem.lower())
            else:
                searchRegex = re.compile(searchItem)

        ###Add space between non-alphanumeric symbols and words
        leftSymbols = '(["“<\'‘‛¿»«'
        rightSymbols = ',.)];:"”?!>\'’'
        middleSymbols = '—/\\+=_'

        verseCounter = 1

        for verse in text:
            verseText = verse[3]
            ###Add space between non-alphanumeric symbols and words
            for symbol in leftSymbols:
                verseText = verseText.replace(symbol, symbol + ' ')
            for symbol in rightSymbols:
                ###Skip adding spaces to numbers with ',' and '.'
                if symbol in ',.':
                    for commaDot in (',', '\.'):
                        if symbol == commaDot.strip('\\'):
                            listRE = list(re.finditer(commaDot, verseText))
                            counter = 0
                            for item in listRE:
                                start = item.start() + counter
                                end = item.end() + counter
                                if start != 0 and end != len(verseText) and \
                                    verseText[start-1].isnumeric() and verseText[end].isnumeric():
                                    continue
                                else:
                                    verseText = verseText[:start] + ' ' + verseText[start:]
                                    counter += 1
                #################################################
                else:
                    verseText = verseText.replace(symbol, ' ' + symbol)
            for symbol in middleSymbols:
                verseText = verseText.replace(symbol, ' ' + symbol + ' ')

            if case == False or form.caseSensitive.data == False:
                found = list(re.finditer(searchRegex, verseText.lower()))
            else:
                found = list(re.finditer(searchRegex, verseText))

            ###Skip processing verses without any search results
            if len(found) == 0:
                continue

            for item in found:

                ###Skip empty searches consisting only of whitespace or regex only with dots
                if item.group() == '':
                    continue

                ###Set the edges of the concordance item context
                start = item.start()-50
                end = item.end() + 50
                itemStart = item.start()
                itemEnd = item.end()

                ###Skip if item does not start or end with the search item
                if searchOption == 'start' or form.searchOptions.data == 'start' \
                    and not (itemStart == 0 or verseText[itemStart-1].isspace()):
                    continue
                elif searchOption == 'end' or form.searchOptions.data == 'end' \
                    and not (itemEnd == len(verseText) or verseText[itemEnd].isspace()):
                    continue
                elif (searchOption == 'word' or form.searchOptions.data == 'word') \
                    and (not (itemStart == 0 or verseText[itemStart-1].isspace()) \
                    or not (itemEnd == len(verseText) or verseText[itemEnd].isspace())):
                    continue

                ###Adjust the edges of the concordance item context re the start and end of the verse
                if start < 0:
                    start = 0
                if end > len(verseText)-1:
                    end = None
                ###Grab the adjacent letters of the word that was found
                if searchOption in ('cont', 'regex', 'end') or \
                    form.searchOptions.data in ('cont', 'regex', 'end'):
                    while itemStart != 0 and not verseText[itemStart-1].isspace():
                        itemStart -= 1
                if searchOption in ('cont', 'regex', 'start') or \
                    form.searchOptions.data in ('cont', 'regex', 'start'):
                    while itemEnd != len(verseText) and not verseText[itemEnd].isspace():
                        itemEnd += 1

                toAdd = [verse[0] + ' ' + verse[1] + ':' + str(verse[2]),
                    verseText[start:itemStart], verseText[itemStart:itemEnd],
                    verseText[itemEnd:end], verseCounter, itemStart]

                if len(concordanceList) > 0 and concordanceList[-1][0] != toAdd[0]:
                    verseCounter += 1

                concordanceList.append(toAdd)

        ###Remove duplicates from the list
        concordanceListNew = {}
        for verse in concordanceList:
            concordanceListNew[(verse[0], verse[2]), verse[5]] = verse

        concordanceList = list(concordanceListNew.values())

        ###Get the concordance length to display the 'Nothing found' message
        concLength = len(concordanceList)

        if concLength == 0:
            return render_template('concordance.html', form=form, sortForm=sortForm,
                                    conc=concordanceList, concLength=concLength)

    if sortForm.validate_on_submit() and sortForm.sort.data:

        verseList = [[[verse[0], verse[1].split(), verse[2], verse[3].split(),
                    verse[4]], None, None, None, None, None, None] for verse in concordanceList]

        colors = {sortForm.option1.name: 'DeepPink', sortForm.option2.name: 'Lime',
                  sortForm.option3.name: 'Turquoise', sortForm.option4.name: 'Indigo',
                  sortForm.option5.name: 'Blue', sortForm.option6.name: 'Gold'}

        options = list(sortForm)[:-2]

        for option in options:
            if option.data != 'None':
                for verse in verseList:
                    if int(option.data) == 0:
                        verse[options.index(option)+1] = verse[0][4]
                        verse[0][0] = f'<span class="{colors[option.name]}">{verse[0][0]}</span>'
                    elif int(option.data) == 2:
                        verse[options.index(option)+1] = verse[0][2].lower()
                        verse[0][2] = f'<span class="{colors[option.name]}">{verse[0][2]}</span>'
                    else:
                        try:
                            if option.data[0] == '3':
                                kwicIndex = int(option.data[1])
                                verse[options.index(option)+1] = verse[0][3][kwicIndex].lower()
                                verse[0][3] = verse[0][3][:kwicIndex] + \
                                    [f'<span class="{colors[option.name]}">\
                                    {verse[0][3][kwicIndex]}</span>'] \
                                    + verse[0][3][kwicIndex+1:]
                            elif option.data[0] == '1':
                                kwicIndex = int("-"+option.data[1])
                                verse[options.index(option)+1] = verse[0][1][kwicIndex].lower()
                                if kwicIndex != -1:
                                    verse[0][1] = verse[0][1][:kwicIndex] + \
                                        [f'<span class="{colors[option.name]}">\
                                        {verse[0][1][kwicIndex]}</span>'] + \
                                        verse[0][1][kwicIndex+1:]
                                elif kwicIndex == -1:
                                    verse[0][1] = verse[0][1][:kwicIndex] + \
                                        [f'<span class="{colors[option.name]}">\
                                        {verse[0][1][kwicIndex]}</span>']
                        except IndexError:
                            verse[options.index(option)+1] = ' '

        for index in range(len(verseList[0][1:])):
            if verseList[0][index+1] != None:
                verseList.sort(key=lambda tup: tup[index+1])

        concordanceList = [[entry[0][0], ' '.join(entry[0][1]), entry[0][2],
                            ' '.join(entry[0][3]), entry[0][4]] for entry in verseList]

        concLength = len(concordanceList)

        return render_template('concordance.html', form=form, sortForm=sortForm,
                                    conc=concordanceList, concLength=concLength)

    if concordanceList == []:
        return render_template('concordance.html', form=form, sortForm=sortForm)
    else:
        return render_template('concordance.html', form=form,
                                conc=concordanceList, concLength=concLength,
                                sortForm=sortForm)


###TO DO: Some verse numbers have letters (3a, 3b)
###TO DO: Delete parallelversesearch.html
###TO DO: Delete parallel.html
###TO DO: Move scripts to separate files
