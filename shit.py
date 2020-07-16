import re

text = ['El cens per clans i llinatges de tots i cada un dels homes de vint anys en amunt aptes per a l’exèrcit, va donar els efectius següents: De la tribu de Rubèn, primogènit d’Israel, 46  500.',
    'De la tribu de Simeó, 59  300.', 'De la tribu de Gad, 45  650.', 'De la tribu de Judà, 74  600.',
    'De la tribu d’Issacar, 54  400.', 'El seu cos d’exèrcit compta amb 74  600 homes.',
    '»El total dels tres cossos d’exèrcit del campament de Judà és de 186  400 homes, distribuïts per batallons. Ells obriran la marxa.']


leftSymbols = '(["“<\'‘‛»'
rightSymbols = ',.)];:"”?!>\'’'
middleSymbols = '—/\\+=_'

for verse in text:
    ###Add space between non-alphanumeric symbols and words
    for symbol in leftSymbols:
        verse = verse.replace(symbol, symbol + ' ')
    for symbol in rightSymbols:
        ###Skip adding spaces to numbers with ',' and '.'
        if symbol in ',.':

            for commaDot in (',', '\.'):
                if symbol == commaDot.strip('\\'):
                    listRE = list(re.finditer(commaDot, verse))
                    counter = 0
                    for item in listRE:
                        start = item.start() + counter
                        end = item.end() + counter

                        if start != 0 and end != len(verse) and \
                            verse[start-1].isnumeric() and verse[end].isnumeric():
                            continue
                        else:
                            verse = verse[:start] + ' ' + verse[start:]
                            counter += 1
        else:
            verse = verse.replace(symbol, ' ' + symbol)

    found = re.finditer('\d', verse)

    for item in found:

        ###Set the edges of the concordance item context
        start = item.start()-50
        end = item.end() + 50
        itemStart = item.start()
        itemEnd = item.end()

        ###Adjust the edges of the concordance item context re the start and end of the verse
        if start < 0:
            start = 0
        if end > len(verse)-1:
            end = None
        ###Grab the adjacent letters of the word that was found
        while itemStart != 0 and verse[itemStart-1] != ' ':
            itemStart -= 1
        while itemEnd != len(verse) and verse[itemEnd] != ' ':
            itemEnd += 1

        toAdd = (verse[start:itemStart], verse[itemStart:itemEnd],
            verse[itemEnd:end])

        print(toAdd)
