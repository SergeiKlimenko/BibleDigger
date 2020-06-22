from bibledigger.__init__ import db
from bibledigger.models import Book, Language, Translation, Text

langs = [(lang.id, lang.language) for lang in Language.query.all()]
print(langs)
