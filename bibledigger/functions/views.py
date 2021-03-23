from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, session
from bibledigger import db
from .forms import browseForm, verseSearchForm, parallelVerseSearchForm, \
                   wordListForm, concordanceForm
from bibledigger.models import Book, Language, Translation, Text
import json
import re

functions = Blueprint('functions', __name__)

languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
languageChoices.sort(key=lambda tup: tup[1])

@functions.route('/browse/<int:parallelOrNot>/', methods=['GET', 'POST'])
@functions.route('/browse/<int:parallelOrNot>/<int:language_id>/<int:translation_id>/<verseCode>', methods=['GET', 'POST'])
def browse(parallelOrNot, language_id=None, translation_id=None, verseCode=None):

    form = browseForm()

    ######delete
    # languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]

    if form.validate_on_submit():

        language1 = request.form['language1']
        translation1 = request.form['translation1']
        book = request.form['book']

        if parallelOrNot == 1:
            tran1Text = Text.query.filter_by(translation_id=translation1,\
                book_code=book).join(Book).with_entities(Text.id, \
                Book.title, Text.chapter, Text.verse, Text.text).all()
            textLength = len(tran1Text)
            return render_template('browse.html',
                                    form=form,
                                    texts=tran1Text,
                                    textLength=textLength,
                                    parallelOrNot=parallelOrNot,
                                    languageChoices=languageChoices,
                                    input=[language1, translation1, book])

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
            return render_template('browse.html',
                                    form=form,
                                    texts=bothTranslations,
                                    textLength=textLength,
                                    parallelOrNot=parallelOrNot,
                                    languageChoices=languageChoices,
                                    input=[language1, translation1, book, language2, translation2])

    if translation_id != None:
        book_code = Book.query.with_entities(Book.code).filter_by(title=' '.join(verseCode.split()[:-1])).first()[0]
        tran1Text = Text.query.filter_by(translation_id=translation_id,\
            book_code=book_code).join(Book).with_entities(Text.id, \
            Book.title, Text.chapter, Text.verse, Text.text).all()
        textLength = len(tran1Text)

        return render_template('browse.html',
                                form=form,
                                texts=tran1Text,
                                textLength=textLength,
                                parallelOrNot=parallelOrNot,
                                verseCode=verseCode,
                                languageChoices=languageChoices,
                                input=[language_id, translation_id, book_code])

    return render_template('browse.html',
                            form=form,
                            parallelOrNot=parallelOrNot,
                            languageChoices=languageChoices)


@functions.route('/<target>/<anchor>')
@functions.route('/<target>/<anchor>/<book>')
@functions.route('/<target>/<anchor>/<book>/<chapter>')
def newList(target, anchor, book=None, chapter=None):
    if target == 'translation':
        items = list(db.engine.execute(f"SELECT DISTINCT id, translation \
            FROM translations WHERE language_id = {anchor}"))
    elif target == 'book':
        items = list(db.engine.execute(f"SELECT DISTINCT a.book_code, b.title \
            FROM texts a LEFT JOIN books b ON a.book_code = b.code \
              WHERE translation_id = {anchor}"))
    elif target == 'chapter':
        items = list(db.engine.execute(f"SELECT DISTINCT chapter, chapter \
            FROM texts WHERE translation_id = {anchor} AND \
            book_code = '{book}' ORDER BY id"))
    elif target == 'verse':
        items = list(db.engine.execute(f"SELECT DISTINCT verse, verse \
            FROM texts WHERE translation_id = {anchor} AND \
            book_code = '{book}' AND chapter = '{chapter}' ORDER BY id"))

    itemArray = []

    for item in items:
        itemObj = {}
        itemObj['id'] = item[0]
        itemObj['item'] = item[1]
        itemArray.append(itemObj)

    return jsonify({'items': itemArray})


@functions.route('/verseSearch/<int:parallelOrNot>/', methods=['GET', 'POST'])
@functions.route('/verseSearch/<int:parallelOrNot>/<verseList>', methods=['GET', 'POST'])
def verseSearch(parallelOrNot, verseList=None, input=None):

    if parallelOrNot == 1:
        form = verseSearchForm()
    elif parallelOrNot == 2:
        form = parallelVerseSearchForm()

    # languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]

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
                verse[0] = (book, verse[0])
                verse[3] = (language1, verse[3])
                verse[4] = (translation1, verse[4])
                if parallelOrNot == 2:
                    language2 = db.engine.execute(f"SELECT language FROM languages \
                        WHERE id = {verse[5]}").fetchone().language
                    translation2 = db.engine.execute(f"SELECT translation FROM translations \
                        WHERE id = {verse[6]}").fetchone().translation
                    verse[5] = (language2, verse[5])
                    verse[6] = (translation2, verse[6])

        return verseList

    if form.validate_on_submit():

        anotherVerse = form.anotherVerse.data

        if parallelOrNot == 1:
            verse = [request.form['book'], request.form['chapter'], request.form['verse'],
                request.form['language1'], request.form['translation1']]
        elif parallelOrNot == 2:
            verse = [request.form['book'], request.form['chapter'], request.form['verse'],
                request.form['language1'], request.form['translation1'], request.form['language2'],
                request.form['translation2']]

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
            return redirect(url_for('functions.verseSearch',
                                    verseList=verseList,
                                    languageChoices=languageChoices,
                                    parallelOrNot=parallelOrNot))

        else:

            verseList.append('delete')

            return redirect(url_for('functions.verseSearch',
                                    verseList=verseList,
                                    languageChoices=languageChoices,
                                    parallelOrNot=parallelOrNot))

    if verseList == None:
        return render_template('versesearch.html',
                                form=form,
                                languageChoices=languageChoices,
                                parallelOrNot=parallelOrNot)

    else:
        if verseList.endswith("'delete']"):

            verseList = verseList.replace(", 'delete'", '')
            verseList = processVerseList(verseList, False)

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

                    verseToRender.append(((verse.title + " " + verse.chapter + ":" +
                        str(verse.verse), item[0]), item[1], item[2], (language1, item[3]), (translation1, item[4]), verse.text1))

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

                    verseToRender.append(((verse.title + " " + verse.chapter + ":" +
                        str(verse.verse), item[0]), item[1], item[2], (language1, item[3]),
                        (translation1, item[4]), (language2, item[5]), (translation2, item[6]), verse.text2, verse.text1))

            return render_template('versesearch.html',
                                    form=form,
                                    languageChoices=languageChoices,
                                    anotherVerse=False,
                                    verseToRender=verseToRender,
                                    parallelOrNot=parallelOrNot)

        else:
            verseList = processVerseList(verseList, True)

            return render_template('versesearch.html',
                                    form=form,
                                    languageChoices=languageChoices,
                                    anotherVerse=True,
                                    verseToRender=verseList,
                                    parallelOrNot=parallelOrNot)


def catchIncorrectRegex(searchItem, case):
    try:
        if case == 'False':
            for symbol in searchItem:
                symInd = searchItem.index(symbol)
                if (searchItem[symInd-1] == '\\' and symInd == 1) or \
                    (searchItem[symInd-1] == '\\' and searchItem[symInd-2] != '\\'):
                    continue
                else:
                    searchItem = searchItem[:symInd] + searchItem[symInd].lower() + searchItem[symInd+1:]
        searchRegex = re.compile(searchItem)
        return searchRegex
    except:
        return False


def separatePunctuation(string, language):

    symbols = ['\.', ',', '\?', '\)', '\(', '!', ':', '-', ';', '“', '”', '’', '‘', '\]', '\[', '—', "'", '–', '¿', '…', '»', '¡', '«', '\*', '/', '"', '―', '‹', '›', '\u200c', '„', '=', '‑', '\u200d', '\xad', '‐', '।', '\|', '>', '、', '،', '؟', '。', '<', '\+', '\{', '\}', '؛', '_', '（', '）', '#', '\u200b', '！', '？', '』', '『', '：', '」', '；', '「', '，', '‚', '·', '］', '［', '\u200f', '\$', '%', '॰', '○', '&', '¶', '†', '၊', '〕', '〔', '។', '\u200e', '॥', '×', '။', '《', '》', '៖', '᙭', '၏', '၎', '၍', '၌', '‧', '•', '@', '᙮', '־', '．', '−', '‛', '៕', '៚', '\x9d', '፤', '።', '⌟', '⌞', '\ufeff', '~', '\u2060', '׃', '།', '·', '＃', '・', '－', '፥', '፡', '\x92', '༎', '՝', '։', '՛', '՞', '՜', '׆', '׀', '【', '】', '─', '′', '\x85', '§', '༌', '፦', '¬', '�', '۔', '՚', '་', '‟', '\ue234', '\ue233', '\ue2fc', '\ue2fa', '\ue2fe', '\ue236', '\ue231', '\ue232', '\ue2fb', '\ue2f9', '±', '\x91', '؞', '꤮', '‰', '\uf21d', '£', '\x94', '\x93', '\\\\', '\x90', '\x8f', '\x81', '៙', '៘', '＝', '／', '～', '\uf0b7', '\uf171', '․', '⁄', '\uf219', '☽', '〛', '〚', '©', '⌃', '\x96', '﴿', '﴾', '₦', '\ue2db', '\ue2d9', '\ue2de', '¢', '꤯', '‥', '༽', '༼', '‸', '᥄', '᥅', '∂', '\uf218', '¥', '\x8d', '⌋', '⌊', '๚', '྅', '႟', '\n', '\x9b', '⵰', '⧾', '⸀', '⸁', '⸂', '⸃', '⟧', '⸅', '⟦', ';', '⸄', '¦', '׳', '״', '╚', '╟', '\x8c', '\x98', '۾', '۽', '€', '‒', '༄', '༅', '፣', '\ue314', '\ue315', '\ue310', '\ue309', '＠', '｣', '※', '＋', '△', '＞', '♫', '★', '＆', '｜', '☆', '￥', '🎼', '㎢', '％', '〰', '◎', '→', '＊', '㎞', '＜', '♥', '♪', '･', '\ue439', '\ue030', '\ue317', '〈', '〉', '\x9f', '∼', '\x87']

    def wordEndCheck(string, index, symbols, direction):
        if direction == 'right':
            string = string[index:]
        elif direction == 'left':
            string = string[:index+1][::-1]
        for symbol in string:
            if any([s for s in symbols if symbol in s]):
                continue
            elif symbol.isspace():
                return True
            elif symbol.isalnum():
                return False
        return True

    def addSpaces(shiftIndex, smbl, before, after, spaces):
        if spaces == 2:
            shiftIndex += 2
            string = before + f' {smbl} ' + after
        else:
            shiftIndex += 1
            if spaces == 'left':
                string = before + f' {smbl}' + after
            elif spaces == 'right':
                string = before + f'{smbl} ' + after
        return string, shiftIndex

    noSpaceLanguages = ['Japanese', 'Chinese (Classical)', 'Chinese (Simplified)', 'Chinese (Traditional)', '(Hakkafa)', 'Khmer', 'Thai', 'Myanmar', 'Bunong']

    for symbol in symbols:
        if re.search(symbol, string):
            shiftIndex = 0
            for item in re.finditer(symbol, string):
                itemStart = item.start() + shiftIndex
                itemEnd = item.end() + shiftIndex
                before = string[:itemStart]
                smbl = string[itemStart:itemEnd]    
                after = string[itemEnd:]
                if itemStart != 0:
                    prevSymbol = string[itemStart-1]
                if itemEnd != len(string):
                    nextSymbol = string[itemEnd]
                #Add a space to signs with one space
                if itemStart != 0 and not prevSymbol.isspace() and (itemEnd == len(string) or nextSymbol.isspace()):
                    #Skip apostrophes at the end of the word (bagi', nuyya)
                    if smbl == "'":
                        continue
                    string, shiftIndex = addSpaces(shiftIndex, smbl, before, after, 'left')
                elif itemEnd != len(string) and not nextSymbol.isspace() and (itemStart == 0 or prevSymbol.isspace()):
                    #Skip apostrophes at the beginning of the word (bagi', nuyya)
                    if smbl == "'":
                        continue
                    string, shiftIndex = addSpaces(shiftIndex, smbl, before, after, 'right')
                #Add spaces around symbols in the middle of the word or skip        
                elif itemStart != 0 and itemEnd != len(string):
                    if not prevSymbol.isspace() and not nextSymbol.isspace():
                        #Surround en dash and em dash with spaces if they are not
                        if symbol in ['—', '–', '\u200c', '\u200b', '』', '『', '」', '「']:
                            string, shiftIndex = addSpaces(shiftIndex, smbl, before, after, 2)
                        elif prevSymbol.isdigit() and nextSymbol.isdigit():
                            #Skip comma & dot between digits
                            if ',' in symbol or '.' in symbol:
                                continue
                            #Add spaces around other symbols between digits (hyphens, colons, etc.)
                            else:
                                string, shiftIndex = addSpaces(shiftIndex, smbl, before, after, 2)
                        elif wordEndCheck(string, itemStart, symbols, 'left') or wordEndCheck(string, itemStart, symbols, 'right'):
                            string, shiftIndex = addSpaces(shiftIndex, smbl, before, after, 2) 
                        #If one of the languages without spaces
                        elif len([lang for lang in noSpaceLanguages if lang in language]) > 0:
                            #Add spaces between all signs when no spaces around
                            string, shiftIndex = addSpaces(shiftIndex, smbl, before, after, 2)
    return string
    

@functions.route('/wordlist/', methods=['GET', 'POST'])
@functions.route('''/wordlist/<int:language_id>/<int:translation_id>/<searchItem>/<searchOption>/
                     <case>/<int:freqMin>/<int:freqMax>/<order>''', methods=['GET', 'POST'])
def wordList(language_id=None, translation_id=None, searchItem=None, searchOption=None, case=None,
              freqMin=None, freqMax=None, order=None):

    form = wordListForm()

    # languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]

    if form.validate_on_submit():

        language_id = request.form['language1']
        translation_id = request.form['translation1']
        searchItem=form.search.data.replace('/', '%2F').replace('.', '%2E').replace('#', '%23').replace("’", '%27')
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

        if searchItem == '' and searchOption != 'all':
            return render_template('wordlist.html',
                                    form=form,
                                    languageChoices=languageChoices,
                                    wordsLength=0,
                                    language_id=language_id,
                                    translation_id=translation_id,
                                    searchItem=searchItem,
                                    searchOption=searchOption,
                                    case=case,
                                    freqMin=freqMin,
                                    freqMax=freqMax,
                                    order=order)

        return redirect(url_for('functions.wordList',
                                language_id=language_id,
                                translation_id=translation_id,
                                searchItem=searchItem,
                                searchOption=searchOption,
                                case=case,
                                freqMin=freqMin,
                                freqMax=freqMax,
                                order=order))

    if translation_id != None:

        fullText = Text.query.filter_by(translation_id=translation_id).with_entities(Text.text).all()

        searchItem = searchItem.replace('%2F', '/').replace('%2E', '.').replace('%23', '#').replace('%27', "’")
        
        language = db.engine.execute(f"SELECT language FROM languages WHERE id = {language_id}").fetchone().language

        verseList = []

        for verse in fullText:
            # verse = verse[0].replace('—', ' — ').split()
            verse = separatePunctuation(verse[0], language).split()
            # strippedVerse = []
            # for word in verse:
                ###TO DO: Add spaces for punctuation symbols, rather then strip them
                # strippedVerse.append(word.strip(',.()[];:""„“”?!—/\\-+=_<>¿»«').
                    # strip(",.()[];:''‘’„‛“”?!—/\\-+=_<>"))

            # verseList += strippedVerse

            verseList += verse
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
            sortedWordList.sort(key=lambda tup: tup[1].lower())

        words = []

        ###TO DO: test thoroughly. A lot of bugs!!!
        if searchOption == 'all':
            words = sortedWordList
        else:
            for word in sortedWordList:
                if case == 'False':
                    searchThis = searchItem.lower()
                    testWord = word[1].lower()
                else:
                    searchThis = searchItem
                    testWord = word[1]

                if searchOption == 'start':
                    if testWord.startswith(searchThis):
                        words.append(word)
                elif searchOption == 'end':
                    if testWord.endswith(searchThis):
                        words.append(word)
                elif searchOption == 'cont':
                    if searchThis in testWord:
                        words.append(word)
                elif searchOption == 'regex':
                    ###Catch incorrect regex
                    searchRegex = catchIncorrectRegex(searchThis, case)
                    if searchRegex == False:
                        return render_template('wordlist.html', 
                                                form=form,
                                                languageChoices=languageChoices,
                                                errorMessage='Sorry It seems that your regular expression is incorrect. Try again. ')
                    if re.search(searchRegex, testWord):
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

        return render_template('wordlist.html',
                                form=form,
                                languageChoices=languageChoices,
                                words=wordsPaginated,
                                wordsLength=wordsLength,
                                language_id=language_id,
                                translation_id=translation_id,
                                searchItem=searchItem,
                                searchOption=searchOption,
                                case=case,
                                freqMin=freqMin,
                                freqMax=freqMax,
                                order=order,
                                pages=pages)

    else:
        wordsLength = -1
        return render_template('wordlist.html',
                                form=form,
                                languageChoices=languageChoices,
                                wordsLength=wordsLength)


@functions.route('/concordance/', methods=['GET', 'POST'])
@functions.route('/concordance/<int:language_id>/<int:translation_id>/<searchItem>/<searchOption>/<case>',
                  methods=['GET', 'POST'])
def concordance(language_id=None, translation_id=None, searchItem=None, searchOption=None, case=None):

    form = concordanceForm()

    # languageChoices = [(lang.id, lang.language) for lang in Language.query.all()]
    choices = [(None, 'none'), (0, 'verse'), (32, '3R'), (31, '2R'), (30, '1R'),
                (2, 'KWIC'), (11, '1L'), (12, '2L'), (13, '3L')]

    ###The concordance holder to be filled with search results
    concordanceList = []

    if form.validate_on_submit() and form.submit.data:
        # translation_id = form.translation1.data
        language_id = request.form['language1']
        translation_id = request.form['translation1']
        searchItem = form.search.data.replace('/', '%2F').replace('.', '%2E').replace('#', '%23').replace("’", '%27')
        searchOption = form.searchOptions.data
        case = form.caseSensitive.data

        return redirect(url_for('functions.concordance', 
                        languageChoices=languageChoices,
                        choices=choices, 
                        language_id=language_id, 
                        translation_id=translation_id,
                        searchItem=searchItem, 
                        searchOption=searchOption,
                        case=case))
    else:
        pass

    if translation_id != None:

        text = list(db.engine.execute(f'SELECT b.title, a.chapter, a.verse, a.text \
            FROM texts a LEFT JOIN books b ON a.book_code = b.code WHERE \
            translation_id = {translation_id}'))

        searchItem = searchItem.replace('%2F', '/').replace('%2E', '.').replace('%23', '#').replace('%27', "’")
        
        if searchItem == None: ###Edit
            searchItem = form.search.data
        ###Strip the search item to avoid searching just for whitespaces
        searchItem = searchItem.strip()

        reSpecialSymbols = r'\.^$*+?{}[]|()'

        ###Check if search item is regex to compile it accordingly
        if searchOption == 'regex' or form.searchOptions.data == 'regex':
            ###Skip the search if it consists only of dots -- Takes too long to process and not informative
            skip = True
            for character in searchItem:
                if character != '.':
                    skip = False
                    break
            if skip == True:
                return render_template('concordance.html',
                                        form=form,
                                        languageChoices=languageChoices,
                                        choices=choices,
                                        concLength=0)

            ###Catch incorrect regex
            searchRegex = catchIncorrectRegex(searchItem, case)
            if searchRegex == False:
                return render_template('concordance.html', 
                                        form=form,
                                        languageChoices=languageChoices,
                                        choices=choices,
                                        errorMessage='Sorry It seems that your regular expression is incorrect. Try again. ')

        else:
            searchRegexToCompile = searchItem
            for symbol in reSpecialSymbols:
                searchRegexToCompile = searchRegexToCompile.replace(symbol, '\\' + symbol)
            if case == 'False': # or form.caseSensitive.data == False:
                searchRegex = re.compile(searchRegexToCompile.lower())
            else:
                searchRegex = re.compile(searchRegexToCompile)

        verseCounter = 1

        language = db.engine.execute(f"SELECT language FROM languages WHERE id = {language_id}").fetchone().language
        for verse in text:
            verseText = separatePunctuation(verse[3], language)
            
            if case == 'False': #or form.caseSensitive.data == False:
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
                    while itemStart != 0 and not verseText[itemStart].isspace() and not verseText[itemStart-1].isspace():
                        itemStart -= 1
                if searchOption in ('cont', 'regex', 'start') or \
                    form.searchOptions.data in ('cont', 'regex', 'start'):
                    while itemEnd != len(verseText) and not verseText[itemEnd-1].isspace() and not verseText[itemEnd].isspace():
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
            return render_template('concordance.html',
                                    form=form,
                                    conc=concordanceList,
                                    concLength=concLength,
                                    languageChoices=languageChoices,
                                    choices=choices,
                                    language_id=language_id,
                                    translation_id=translation_id,
                                    searchItem=searchItem,
                                    searchOption=searchOption,
                                    case=case)

    if concordanceList == []:
        return render_template('concordance.html',
                                form=form,
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


###TO DO: Stretching of the sidebar
###TO DO: Change sorting colors
###TO DO: Parallel texts with absent verses
###TO DO: Remove spaces from wordlist
