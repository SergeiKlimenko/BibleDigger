import sys
sys.path.insert(0, 'D://NewBibles/BibleApp')

from bibledigger import db


class Book(db.Model):

    __tablename__ = 'books'

    code = db.Column(db.String(3), primary_key=True)
    title = db.Column(db.String(64), unique=True, nullable=False)
    verses  = db.relationship('Text', backref='book')

    def __repr__(self):
        return f"{self.code}: {self.title}"

    def __init__(self, code, title):
        self.code = code
        self.title = title


class Language(db.Model):

    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.Unicode, nullable=False, unique=True)
    translations = db.relationship('Translation', backref='language')

    def __repr__(self):
        return f"{self.id}: {self.language}"

    def __init__(self, language):
        self.language = language


class Translation(db.Model):

    __tablename__ = 'translations'

    id = db.Column(db.Integer, primary_key=True)
    translation = db.Column(db.Unicode, nullable=False, unique=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'), nullable=False)
    verses = db.relationship('Text', backref='translation')
    __table_args__ = (db.Index('language_id_index', "language_id"),)

    def __repr__(self):
        return f"{self.id}: {self.language_id}: {self.translation}"

    def __init__(self, translation, language_id):
        self.translation = translation
        self.language_id = language_id


class Text(db.Model):

    __tablename__ = 'texts'

    id = db.Column(db.Integer, primary_key=True)
    translation_id = db.Column(db.Integer, db.ForeignKey('translations.id'), nullable=False)
    book_code = db.Column(db.String(3), db.ForeignKey('books.code'), nullable=False)
    chapter = db.Column(db.String(10), nullable=False)
    verse = db.Column(db.Integer, nullable=False)
    text = db.Column(db.UnicodeText, nullable=False)
    __table_args__ = (db.Index('translation_id_index', "translation_id"),
        db.Index('book_code_index', "book_code"), db.Index('verse_index', "book_code", "chapter", "verse"),)

    def __repr__(self):
        return f"{self.book}.{self.chapter}:{self.verse}: {self.text}"

    def __init__(self, translation_id, book_code, chapter, verse, text):
        self.translation_id = translation_id
        self.book_code = book_code
        self.chapter = chapter
        self.verse = verse
        self.text = text
