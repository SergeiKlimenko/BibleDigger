#! /usr/bin/env python3
import os
import re
import json
from bibledigger.__init__ import db
from bibledigger.models import Book, Language, Translation, Text

import collections

os.chdir(os.pardir)

languageList = [dir for dir in os.listdir() if os.path.isdir(dir) and dir != 'BibleDigger']
languageList.sort()

#filePath = os.path.dirname(os.path.abspath(__file__)) ###DELETE

###TO DO: Genesis 21 instead of Genesis 1 in Afrikaans--Nuwe_Lewende_Vertaling_(NLV)_nlv!!!!!

###Add bible books to the db
bibleB = {'Genesis': 'GEN', 'Exodus': 'EXO', 'Leviticus': 'LEV', 'Numbers': 'NUM', 'Deuteronomy': 'DEU', 'Joshua': 'JOS', 'Judges': 'JDG', 'Ruth': 'RUT', '1 Samuel': '1SA', '2 Samuel': '2SA', '1 Kings': '1KI', '2 Kings': '2KI', '1 Chronicles': '1CH', '2 Chronicles': '2CH', '1 Esdras': '1ES', '2 Esdras': '2ES', 'Ezra': 'EZR', 'Nehemiah': 'NEH', 'Tobit': 'TOB', 'Judith': 'JDT', 'Esther': 'EST', 'Esther Greek': 'ESG', '1 Maccabees': '1MA', '2 Maccabees': '2MA', '3 Maccabees': '3MA', '4 Maccabees': '4MA', 'Job': 'JOB', 'Psalms': 'PSA', 'Psalm 151': 'PS2', 'Prayer of Manasseh': 'MAN', 'Proverbs': 'PRO', 'Ecclesiastes': 'ECC', 'Song of Solomon': 'SNG', 'Wisdom': 'WIS', 'Sirach': 'SIR', 'Isaiah': 'ISA', 'Jeremiah': 'JER', 'Baruch': 'BAR', 'Letter of Jeremiah': 'LJE', 'Susanna': 'SUS', 'Bel and the Dragon': 'BEL', 'Lamentations': 'LAM', 'Ezekiel': 'EZK', 'Daniel': 'DAN', 'Daniel Greek': 'DAG', 'Hosea': 'HOS', 'Joel': 'JOL', 'Amos': 'AMO', 'Obadiah': 'OBA', 'Jonah': 'JON', 'Micah': 'MIC', 'Nahum': 'NAM', 'Habakkuk': 'HAB', 'Zephaniah': 'ZEP', 'Haggai': 'HAG', 'Zechariah': 'ZEC', 'Malachi': 'MAL', 'Matthew': 'MAT', 'Mark': 'MRK', 'Luke': 'LUK', 'John': 'JHN', 'Acts': 'ACT', 'Luke-Acts': 'LKA', 'Romans': 'ROM', '1 Chorinthians': '1CO', '2 Chorinthians': '2CO', 'Galatians': 'GAL', 'Ephesians': 'EPH', 'Philippians': 'PHP', 'Collosians': 'COL', 'Laodiceans': 'LAO', 'Laoidhean': 'ODA', '1 Thessalonians': '1TH', '2 Thessalonians': '2TH', '1 Timothy': '1TI', '2 Timothy': '2TI', 'Titus': 'TIT', 'Philemon': 'PHM', 'Hebrews': 'HEB', 'James': 'JAS', '1 Peter': '1PE', '2 Peter': '2PE', '1 John': '1JN', '2 John': '2JN', '3 John': '3JN', 'Jude': 'JUD', 'Revelation': 'REV'}

# for t, c in bibleB.items():
#      #if not Book.query.filter_by(code=c).first():
#      book = Book(code=c, title=t)
#      db.session.add(book)
# db.session.commit()
# print('Books added')
###########################

###TO DO: remove "¶ "
###TO DO: check extra long verses
####################
def loopFunc(languageList):
    for language in languageList[1:]:

        #Add language to db
        print(language)
        languageToAdd = Language(language=language)
        db.session.add(languageToAdd)
        db.session.commit()
        print('Language added')
        ###################

        langDir = os.path.join(os.getcwd(), language)
        ###Some translation files have the same translation title
        translationList = [trans for trans in os.listdir(langDir)]
        duplicateTranslationTitles = [item for item, count in collections.Counter([' '.join(translation.split('--')[1].split('_')[:-1]) for translation in translationList]).items() if count > 1]
        duplicateTranslationCounter = 0
        ###
        for translation in translationList:
            print(translation)

            #Add translation to db
            translationToAdd = Translation(translation=translation,
                language_id=Language.query.with_entities(Language.id).filter_by(language=language))
            db.session.add(translationToAdd)
            db.session.commit()
            print('    Translation added')
            ######################

            #if translation != 'Español_(América_Latina)_-_Spanish--Biblia_Reina_Valera_1995_rvr95.txt': ###DELETE
            #    continue
            text = readText(language, translation)
            ###########
            ###add to database###
            ###########
            for chapter in text:
                if len(chapter) == 0:
                    continue
                for verse in chapter:
                    #Some verses are lumped together (e.g. "2-5")
                    if '-' in verse[3]:
                        verses = verse[3].split('-')
                        firstVerse = verses[0]
                        lastVerse = verses[1]
                        verseToAdd = Text(translation_id=Translation.query.with_entities(Translation.id).filter_by(translation=translation),
                                            book_code=verse[1],
                                            chapter=verse[2],
                                            verse=firstVerse,
                                            text=verse[4])
                        db.session.add(verseToAdd)
                        #Some verses have letters in them (e.g. bimk: 6a, 6b)
                        if not firstVerse.isnumeric():
                            firstVerse = firstVerse[:-1]
                        if not lastVerse.isnumeric():
                            lastVerse = lastVerse[:-1]
                        #####################################################
                        for i in range(int(lastVerse)-int(firstVerse)):
                            verseToAdd = Text(translation_id=Translation.query.with_entities(Translation.id).filter_by(translation=translation),
                                                book_code=verse[1],
                                                chapter=verse[2],
                                                verse=str(int(firstVerse)+i+1),
                                                text='')
                            db.session.add(verseToAdd)
                    else:
                        verseToAdd = Text(translation_id=Translation.query.with_entities(Translation.id).filter_by(translation=translation),
                                            book_code=verse[1],
                                            chapter=verse[2],
                                            verse=verse[3],
                                            text=verse[4])
                        db.session.add(verseToAdd)
                        #print(verse)###DELETE
                db.session.commit()
                print(f"        Chapter {text.index(chapter)+1} added")

def readText(language, translation):
    with open(os.path.join(os.getcwd(), language, translation), 'r', encoding='utf-8-sig') as f:
        text = json.loads("[" + f.read().replace("][", "],[") + "]")
    return text


loopFunc(languageList)
