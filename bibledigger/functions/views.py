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
        print(verseList) ###delete
        print(list(session)[1:]) ###delete
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

                print(verseToRender) ###delete

            sessionKeys = list(session.keys())
            for k in sessionKeys:
                if k != 'csrf_token' and k != '_permanent':
                    session.pop(k)

            return render_template('versesearch.html', form=form,
                anotherVerse=anotherVerse, verseToRender=verseToRender)

    else:
        print(form.errors) ###DELETE

    for k in list(session.keys()):
        if k != 'csrf_token' and k != '_permanent':
            session.pop(k)

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


@functions.route('/concordance', methods=['GET', 'POST'])
def concordance():

    form = concordanceForm()
    sortForm = concordanceSortForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]

    if form.validate_on_submit() and form.submit.data:

        text = list(db.engine.execute(f'SELECT b.title, a.chapter, a.verse, a.text \
            FROM texts a LEFT JOIN books b ON a.book_code = b.code WHERE \
            translation_id = {form.translation1.data}'))

        ###The concordance holder to be filled with search results
        concordanceList = []

        searchItem = form.search.data
        ###Strip the search item to avoid searching just for whitespaces
        searchItem = searchItem.strip()

        import re

        reSpecialSymbols = r'\\.^$*+?{}[]|()'

        ###Check if search item is regex to compile it accordingly
        if form.searchOptions.data == 'regex':
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
                if form.caseSensitive.data == False:
                    for symbol in searchItem:
                        if searchItem.index(symbol) == 0 or \
                          (searchItem[searchItem.index(symbol)-1] == '\\' and searchItem.index(symbol) == 1) or \
                          (searchItem[searchItem.index(symbol)-1] == '\\' and searchItem[index(symbol)-2] != '\\'):
                            continue
                        else:
                            searchItem[searchItem.index(symbol)].lower()
                searchRegex = re.compile(searchItem)
            except:
                errorMessage = 'Sorry It seems that your regular expression is incorrect. Try again. '
                return render_template('concordance.html', form=form,
                                        sortForm=sortForm, errorMessage=errorMessage)

        else:
            for symbol in reSpecialSymbols:
                searchItem = searchItem.replace(symbol, '\\' + symbol)
            print(searchItem) ###delete
            if form.caseSensitive.data == False:
                searchRegex = re.compile(searchItem.lower())
            else:
                searchRegex = re.compile(searchItem)

        ###Add space between non-alphanumeric symbols and words
        leftSymbols = '(["“<\'‘‛'
        rightSymbols = ',.)];:"”?!>\'’'
        middleSymbols = '—/\\+=_'

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
                # if symbol == ',':
                #     listRE = list(re.finditer(',', verseText))
                #     counter = 0
                #     for item in listRE:
                #         start = item.start() + counter
                #         end = item.end() + counter
                #         if start != 0 and end != len(verseText) and \
                #             verseText[start-1].isnumeric() and verseText[end].isnumeric():
                #             continue
                #         else:
                #             verseText = verseText[:start] + ' ' + verseText[start:]
                #             counter += 1
                # elif symbol == '.':
                #     listRE = list(re.finditer('\.', verseText))
                #     counter = 0
                #     for item in listRE:
                #         start = item.start() + counter
                #         end = item.end() + counter
                #         if start != 0 and end != len(verseText) and \
                #             verseText[start-1].isnumeric() and verseText[end].isnumeric():
                #             continue
                #         else:
                #             verseText = verseText[:start] + ' ' + verseText[start:]
                #             counter += 1
                #################################################
                else:
                    verseText = verseText.replace(symbol, ' ' + symbol)
            for symbol in middleSymbols:
                verseText = verseText.replace(symbol, ' ' + symbol + ' ')

            if form.caseSensitive.data == False:
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
                if form.searchOptions.data == 'start' and not (itemStart == 0 or verseText[itemStart-1] == ' '):
                    continue
                elif form.searchOptions.data == 'end' and not (itemEnd == len(verseText) or verseText[itemEnd] == ' '):
                    continue

                ###Adjust the edges of the concordance item context re the start and end of the verse
                if start < 0:
                    start = 0
                if end > len(verseText)-1:
                    end = None
                ###Grab the adjacent letters of the word that was found
                if form.searchOptions.data == 'cont' or \
                    form.searchOptions.data == 'regex' or \
                    form.searchOptions.data == 'end':
                    while itemStart != 0 and verseText[itemStart-1] != ' ':
                        itemStart -= 1
                if form.searchOptions.data == 'cont' or \
                    form.searchOptions.data == 'regex' or \
                    form.searchOptions.data == 'start':
                    while itemEnd != len(verseText) and verseText[itemEnd] != ' ':
                        itemEnd += 1

                toAdd = (verse[0] + ' ' + verse[1] + ':' + str(verse[2]),
                    verseText[start:itemStart], verseText[itemStart:itemEnd],
                    verseText[itemEnd:end])

                concordanceList.append(toAdd)

        ###Remove duplicates from the list
        checkList = [(verse[0], verse[2]) for verse in concordanceList]
        concordanceListNew = []
        checkListNew = []
        for verse in concordanceList:
            if (verse[0], verse[2]) not in checkListNew:
                checkListNew.append((verse[0], verse[2]))
                concordanceListNew.append(verse)
        concordanceList = concordanceListNew

        ###Get the concordance length to display the 'Nothing found' message
        concLength = len(concordanceList)

        session['concordance'] = concordanceList

        print(concLength)###delete

        return render_template('concordance.html', form=form,
                                conc=concordanceList, concLength=concLength,
                                sortForm=sortForm)

    if sortForm.validate_on_submit() and sortForm.sort.data:

        if sortForm.level1.data == True:

            versesToSort = []

            for verse in session['concordance']:
                if int(sortForm.option1.data) == 2:
                    versesToSort.append((verse[2].lower(), verse))
                else:
                    try:
                        if sortForm.option1.data[0] == '3':
                            versesToSort.append((verse[int(sortForm.option1.data[0])].\
                                split()[int(sortForm.option1.data[1])].lower(), verse))
                        elif sortForm.option1.data[0] == '1':
                            versesToSort.append((verse[int(sortForm.option1.data[0])].\
                                split()[int('-' + sortForm.option1.data[1])].lower(), verse))
                    except IndexError:
                        versesToSort.append((' ', verse))

            versesToSort.sort(key=lambda tup: tup[0])

            concordanceList = [item[1] for item in versesToSort]
            concLength = len(concordanceList)

            return render_template('concordance.html', form=form, sortForm=sortForm,
                                    conc=concordanceList, concLength=concLength)

        else:
            pass

    else:
        print(sortForm.errors)



# for k in list(session.keys()):
#     if k != 'csrf_token' and k != '_permanent':
#         session.pop(k)

    return render_template('concordance.html', form=form, sortForm=sortForm)
