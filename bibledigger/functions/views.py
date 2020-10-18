from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, session
from bibledigger import db
from .forms import browseForm, verseSearchForm, parallelVerseSearchForm, \
                   wordListForm, concordanceForm, concordanceSortForm
from bibledigger.models import Book, Language, Translation, Text
import json

functions = Blueprint('functions', __name__)


@functions.route('/browse/<int:parallelOrNot>/', methods=['GET', 'POST'])
@functions.route('/browse/<int:parallelOrNot>/<int:language_id>/<int:translation_id>/<verseCode>', methods=['GET', 'POST'])
def browse(parallelOrNot, language_id=None, translation_id=None, verseCode=None):

    form = browseForm()

    ###TO DO: Make a new db with translation names edited as below:
    #translationList = [(tran.id,
    #    tran.translation.split('--')[1].split('_(')[0].replace('_', ' '))
    #    for tran in Translation.query.filter_by(language_id=8).all()]

    ######delete
    languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]

    if form.validate_on_submit():

        language1 = request.form['language1']
        translation1 = request.form['translation1']
        book = request.form['book']

        if parallelOrNot == 1:
            tran1Text = Text.query.filter_by(translation_id=translation1,\
                book_code=book).join(Book).with_entities(Text.id, \
                Book.title, Text.chapter, Text.verse, Text.text).all()
            textLength = len(tran1Text)
            return render_template('browse.html', form=form, texts=tran1Text,
                textLength=textLength, parallelOrNot=parallelOrNot,
                languageChoices=languageChoices, input=[language1, translation1, book])

        elif parallelOrNot == 2:
            language2 = request.form['language2']
            translation2 = request.form['translation2']
            bothTranslations = list(db.engine.execute(f"SELECT a.id, d.title, a.chapter, \
                a.verse, a.text, b.text FROM ((SELECT * FROM texts \
                WHERE translation_id = {translation1} and book_code = \
                '{book}') a LEFT JOIN (SELECT * FROM texts \
                WHERE translation_id = {translation2}) b ON \
                a.book_code = b.book_code AND a.chapter = b.chapter \
                AND a.verse = b.verse) c LEFT JOIN books d ON c.book_code = d.code"))
            textLength = len(list(bothTranslations))
            return render_template('browse.html', form=form,
                texts=bothTranslations, textLength=textLength, parallelOrNot=parallelOrNot,
                languageChoices=languageChoices, input=[language1, translation1, book, language2, translation2])

    if translation_id != None:
        book_code = Book.query.with_entities(Book.code).filter_by(title=' '.join(verseCode.split()[:-1])).first()[0]
        tran1Text = Text.query.filter_by(translation_id=translation_id,\
            book_code=book_code).join(Book).with_entities(Text.id, \
            Book.title, Text.chapter, Text.verse, Text.text).all()
        textLength = len(tran1Text)

        return render_template('browse.html', form=form, texts=tran1Text,
            textLength=textLength, parallelOrNot=parallelOrNot, verseCode=verseCode,
            languageChoices=languageChoices, input=[language_id, translation_id, book_code])

    return render_template('browse.html', form=form, parallelOrNot=parallelOrNot,
        languageChoices=languageChoices)


@functions.route('/<target>/<anchor>')
def newList(target, anchor):
    if target == 'translation':
        items = list(db.engine.execute(f"SELECT DISTINCT id, translation \
            FROM translations WHERE language_id = {anchor}"))
    elif target == 'book':
        items = list(db.engine.execute(f"SELECT DISTINCT a.book_code, b.title \
            FROM texts a LEFT JOIN books b ON a.book_code = b.code \
              WHERE translation_id = {anchor}"))

    itemArray = []

    for item in items:
        itemObj = {}
        itemObj['id'] = item[0]
        itemObj['item'] = item[1]
        itemArray.append(itemObj)

    return jsonify({'items': itemArray})


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
            if verseList.endswith("'delete']"):
                verseList = []
            else:
                verseList = processVerseList(verseList, False)
            verseList.append(verse)

        if anotherVerse == True:
            return redirect(url_for('functions.verseSearch', verseList=verseList,
                parallelOrNot=parallelOrNot))

        else:

            verseList.append('delete')

            return redirect(url_for('functions.verseSearch', verseList=verseList,
                parallelOrNot=parallelOrNot))
            #return render_template('versesearch.html', form=form,
            #    anotherVerse=anotherVerse, verseToRender=verseToRender, parallelOrNot=parallelOrNot)

    if verseList == None:
        return render_template('versesearch.html', form=form, parallelOrNot=parallelOrNot)

    else:
        if verseList.endswith("'delete']"):

            verseList = verseList.replace(", 'delete'", '')
            verseList = processVerseList(verseList, False)

            verseToRender =[]

            print('\n')
            print("We're here")
            print(verseList) ###delete
            print('\n')

            for item in verseList:

                print(item)###Delete

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
                anotherVerse=False, verseToRender=verseToRender, parallelOrNot=parallelOrNot)

        else:
            verseList = processVerseList(verseList, True)
            return render_template('versesearch.html', form=form,
                anotherVerse=True, verseToRender=verseList, parallelOrNot=parallelOrNot)


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


@functions.route('/wordlist/', methods=['GET', 'POST'])
@functions.route('''/wordlist/<int:translation_id>/<searchItem>/<searchOption>/
                     <case>/<int:freqMin>/<int:freqMax>/<order>/<int:page>''', methods=['GET', 'POST'])
def wordList(translation_id=None, searchItem=None, searchOption=None, case=None,
              freqMin=None, freqMax=None, order=None, page=None):

    form = wordListForm()

    if form.language1.data == None:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=1).all()]
    else:
        form.translation1.choices = [(tran.id, tran.translation) for tran
            in Translation.query.filter_by(language_id=form.language1.data).all()]

    if form.validate_on_submit():

        translation_id=form.translation1.data
        searchItem=form.search.data.replace('/', '%2F').replace('.', '%2E')
        searchOption=form.searchOptions.data
        if searchOption == 'all':
            searchItem = "None"
        case=form.caseSensitive.data
        freqMin=form.freqMin.data
        if freqMin == None:
            freqMin = 0
        freqMax=form.freqMax.data
        if freqMax == None:
            freqMax = 0
        order=form.orderOptions.data
        page=1

        return redirect(url_for('functions.wordList',
                                translation_id=translation_id,
                                searchItem=searchItem,
                                searchOption=searchOption,
                                case=case,
                                freqMin=freqMin,
                                freqMax=freqMax,
                                order=order,
                                page=page))

    if translation_id != None:

        fullText = Text.query.filter_by(translation_id=translation_id).with_entities(Text.text).all()

        searchItem = searchItem.replace('%2F', '/').replace('%2E', '.')
        print(searchItem)
        print(searchOption)

        verseList = []

        for verse in fullText:

            verse = verse[0].replace('—', ' ').split()
            strippedVerse = []
            for word in verse:
                if case == 'True':
                    ###TO DO: Add spaces for punctuation symbols, rather then strip them
                    strippedVerse.append(word.strip(',.()[];:""“”?!—/\\-+=_<>¿»«').
                        strip(",.()[];:''‘’‛“”?!—/\\-+=_<>"))
                elif case == 'False':
                    strippedVerse.append(word.lower().strip(',.()[];:""“”?!—/\\-+=_<>¿»«').
                        strip(",.()[];:''‘’‛“”?!—/\\-+=_<>"))
            verseList += strippedVerse

        from collections import Counter
        wordList = Counter(verseList)

        sortedWordList = []

        for k, v in wordList.items():
            if k == '':
                continue
            if freqMin != 0:
                if v < freqMin:
                    continue
            if freqMax != 0:
                if v > freqMax:
                    continue
            sortedWordList.append((v, k))

        if order == 'freq':
            sortedWordList.sort(key=lambda tup: tup[1])
            sortedWordList.sort(key=lambda tup: tup[0], reverse=True)
        elif order == 'word':
            sortedWordList.sort(key=lambda tup: tup[0], reverse=True)
            sortedWordList.sort(key=lambda tup: tup[1])

        words = []

        if case == False:
            searchItem = searchItem.lower()

        ###TO DO: test thoroughly. A lot of bugs!!!
        if searchOption == 'all':
            words = sortedWordList
        elif searchOption == 'start':
            for word in sortedWordList:
                if word[1].startswith(searchItem):
                    words.append(word)
        elif searchOption == 'end':
            for word in sortedWordList:
                if word[1].endswith(searchItem):
                    words.append(word)
        elif searchOption == 'cont':
            for word in sortedWordList:
                if searchItem in word[1]:
                    words.append(word)
        elif searchOption == 'regex':
            import re
            regex = re.compile(searchItem)
            for word in sortedWordList:
                if re.search(regex, word[1]):
                    words.append(word)

        #Add ranks to the wordlist
        rank = 1
        for i in range(len(words)):
            words[i] = (rank, words[i][0], words[i][1])
            rank += 1

        wordsLength = len(words)

        #Split the words into pages
        pages = wordsLength // 100 + (wordsLength % 100 > 0)

        wordsPaginated = {}

        if pages > 1:
            pageStep1 = 0
            pageStep2 = 100
            for i in range(pages):
                if i + 1 == pages:
                    wordsPaginated[i+1] = words[pageStep1:]
                else:
                    wordsPaginated[i+1] = words[pageStep1:pageStep2]
                    pageStep1 += 100
                    pageStep2 += 100
        else:
            wordsPaginated[1] = words

        return render_template('wordlist.html', form=form, words=wordsPaginated,
                                wordsLength=wordsLength, translation_id=translation_id,
                                searchItem=searchItem, searchOption=searchOption,
                                case=case, freqMin=freqMin, freqMax=freqMax,
                                order=order, page=page, pages=pages)

    else:
        wordsLength = -1
        return render_template('wordlist.html', form=form, wordsLength=wordsLength)


@functions.route('/concordance/', methods=['GET', 'POST'])
@functions.route('/concordance/<int:language_id>/<int:translation_id>/<searchItem>/<searchOption>/<case>',
                  methods=['GET', 'POST'])
def concordance(language_id=None, translation_id=None, searchItem=None, searchOption=None, case=None):

    form = concordanceForm()
    sortForm = concordanceSortForm()

    languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
    choices = [(None, 'none'), (0, 'verse'), (32, '3R'), (31, '2R'), (30, '1R'),
                (2, 'KWIC'), (11, '1L'), (12, '2L'), (13, '3L')]

    ###The concordance holder to be filled with search results
    concordanceList = []

    if form.validate_on_submit() and form.submit.data:

        # translation_id = form.translation1.data
        language_id = request.form['language1']
        translation_id = request.form['translation1']
        searchItem = form.search.data
        searchOption = form.searchOptions.data
        case = form.caseSensitive.data

        return redirect(url_for('functions.concordance', languageChoices=languageChoices,
                        choices=choices, language_id=language_id, translation_id=translation_id,
                        searchItem=searchItem, searchOption=searchOption,
                        case=case))

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
                                        sortForm=sortForm,
                                        languageChoices=languageChoices,
                                        choices=choices,
                                        concLength=0)

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
                                        languageChoices=languageChoices,
                                        choices=choices,
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
                if (searchOption == 'start' or form.searchOptions.data == 'start') \
                    and not (itemStart == 0 or verseText[itemStart-1].isspace()):
                        continue
                elif (searchOption == 'end' or form.searchOptions.data == 'end') \
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

        print("concordance ready") ###delete
        if concLength == 0:
            return render_template('concordance.html',
                                    form=form,
                                    sortForm=sortForm,
                                    conc=concordanceList,
                                    concLength=concLength,
                                    languageChoices=languageChoices,
                                    choices=choices,
                                    language_id=language_id,
                                    translation_id=translation_id,
                                    searchItem=searchItem,
                                    searchOption=searchOption,
                                    case=case)

    if sortForm.validate_on_submit() and sortForm.sort.data:

        verseList = [[[verse[0], verse[1].split(), verse[2], verse[3].split(),
                    verse[4]], None, None, None, None, None, None] for verse in concordanceList]

        # colors = {sortForm.option1.name: 'DeepPink', sortForm.option2.name: 'Lime',
        #           sortForm.option3.name: 'Turquoise', sortForm.option4.name: 'Indigo',
        #           sortForm.option5.name: 'Blue', sortForm.option6.name: 'Gold'}

        colors = {'option1': 'DeepPink', 'option2': 'Lime', 'option3': 'Turquoise',
                    'option4': 'Indigo', 'option5': 'Blue', 'option6': 'Gold'}

        for option in list(form):
            print(option.data)
        print('\n')
        print(request.form)
        print('\n')
        for option in list(sortForm):
            print(option.data)

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

        # return render_template('concordance.html', form=form, sortForm=sortForm,
        #                             conc=concordanceList, concLength=concLength,
        #                             translation_id=translation_id)

    if concordanceList == []:
        return render_template('concordance.html',
                                form=form,
                                sortForm=sortForm,
                                choices=choices,
                                languageChoices=languageChoices)
    else:

        #Split the words into pages
        pages = concLength // 100 + (concLength % 100 > 0)

        concPaginated = {}

        if pages > 1:
            pageStep1 = 0
            pageStep2 = 100
            for i in range(pages):
                if i + 1 == pages:
                    concPaginated[i+1] = concordanceList[pageStep1:]
                else:
                    concPaginated[i+1] = concordanceList[pageStep1:pageStep2]
                    pageStep1 += 100
                    pageStep2 += 100
        else:
            concPaginated[1] = concordanceList

        return render_template('concordance.html',
                                form=form,
                                sortForm=sortForm,
                                conc=concPaginated,
                                concLength=concLength,
                                pages=pages,
                                languageChoices=languageChoices,
                                choices=choices,
                                language_id=language_id,
                                translation_id=translation_id,
                                searchItem=searchItem,
                                searchOption=searchOption,
                                case=case)


###TO DO: Some verse numbers have letters (3a, 3b)
###TO DO: Shitty vese numbering (21, 2, 3,.. 20, 22 in Afrikaans NLV)
###TO DO: Move scripts to separate files
###TO DO: Fix translation names in the database
###TO DO: Concordance: separate colons ("22 :14")
###TO DO: Pagination or lazy loading
###TO DO: JavaScript for dropdown lists
###TO DO: Separate punctuation from words for all languages
