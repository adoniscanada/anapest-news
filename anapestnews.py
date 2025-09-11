import pickle
import json
from argparse import ArgumentParser
import logging, logging.handlers

from wordtypes import *
from cnnscrape import generate_todays_database

# Load pre-computed stressdict (see stressdict.py)
stressdict = {}
with open('stressdict.pkl', 'rb') as file:
    stressdict = pickle.load(file)
# Store common acronyms that are misunderstood by cmudict
common_acronyms = {
    'AI' : [1, 0],
    'US' : [1, 0]
}

def makePoem(text_list : list, banned_words : list = [], meter : list = [0, 0, 1], desired_line_length : int = 9, desired_poem_length : int = 120, html = True):
    if len(stressdict) == 0:
        return ''

    poem = ''
    line = []
    cut = []
    syllable_count = 0
    position = 0
    newline = '<br />' if html else '\n'
    # Iterate through each word
    for i in text_list:
        # key = word_to_key(i)
        key = wordkey(i)
        fits = True

        if ((key in stressdict) or (i.isupper() and key in common_acronyms)) and not key in [wordkey(i) for i in banned_words]:
            stresses = common_acronyms[key] if (i.isupper() and key in common_acronyms) else stressdict[key]
            # Add boolean rules here: (word is only considered if all rules equate to True)
            lineKeys = [wordkey(j) for j in line]
            rules = [
                    # No consecutive polysyllabics
                    not (len(line) > 0 and len(stresses) > 1 and len(stressdict[lineKeys[-1]]) > 1),
                    # No articles into conjunctions
                    not (len(line) > 0 and words_are_types([key, lineKeys[-1]], [CONJUNCTIONS, ARTICLES], True)),
                    # No articles into prepositions
                    not (len(line) > 0 and words_are_types([key, lineKeys[-1]], [PREPOSITIONS, ARTICLES], True)),
                    # No consecutive prepositions
                    not (len(line) > 0 and words_are_types([key, lineKeys[-1]], [PREPOSITIONS, PREPOSITIONS], True)),
                    # No consecutive pronouns
                    not (len(line) > 0 and words_are_types([key, lineKeys[-1]], [PRONOUNS, PRONOUNS], True)),
                    # No starting a line on a stop
                    not (len(line) == 0 and key in STOPS),
                    # No prepositions into conjunctions
                    not (len(line) > 0 and words_are_types([key, lineKeys[-1]], [CONJUNCTIONS, PREPOSITIONS], True)),
                    # No duplicates within line
                    not (words_are_types([key], [lineKeys], True))
            ]
            # Enforce rules
            for r in rules:
                if not r:
                    fits = False
                    break
            
            # Non-boolean rules
            # Format for poem
            formatted = i
            for j in ['.',',',':','“','”']:
                formatted = formatted.replace(j, '')
            # Ignore stresses of stressed monosyllabic words (assume stressed words can be read unstressed, but unstressed words cannot be stressed)
            if stresses == [1] and len(meter) > 0:
                stresses = [meter[position % len(meter)]]
            # Ignore secondary stresses (if not in meter)
            if not (2 in meter):
                stresses = [min(i, 1) for i in stresses]
            # Generalize articles
            if key in ARTICLES:
                formatted = 'the'

            if fits:
                # Enforce meter (skipped if length of meter is 0)
                for j in range(len(stresses)):
                    if len(meter) > 0 and stresses[j] != meter[(position + j) % len(meter)]:
                        fits = False
                        break
                
                # Add word to poem
                if fits:
                    # Capitalize first word of line and make non-nouns lowercase
                    nonNoun = ARTICLES + CONJUNCTIONS + PRONOUNS + PREPOSITIONS
                    if len(line) == 0:
                        formatted = formatted[0].upper() + formatted[1:]
                    elif key in nonNoun:
                        formatted = formatted.lower()
                        if position % len(meter) == 0 and not (lineKeys[-1] in nonNoun):
                            line[-1] += ','

                    line.append(formatted)
                    count = len(stresses)
                    position += count
                    syllable_count += count
                    if position % len(meter) == 0:
                        if syllable_count >= desired_line_length:
                            if key in STOPS and syllable_count < desired_line_length * 2:
                                # Attempt to replace the ending stop word with a previously cut word
                                while len(cut) > 0:
                                    replacement = cut.pop()
                                    if replacement[1][0] == 1:
                                        replaced = True
                                        line[-1] = replacement[0]
                                        position += len(replacement[1]) - len(stresses)
                                        syllable_count += len(stresses)
                                        break
                            else:
                                # Check poem length
                                if len(poem) >= desired_poem_length and not key in STOPS:
                                    poem += ' '.join(line) + '.'
                                    return poem
                                
                                poem += ' '.join(line) + newline
                                
                                # Divide stanzas
                                if len(line) < desired_line_length:
                                    poem += newline
                                
                                line.clear()
                                syllable_count = 0
            else:
                # Save cut words to replace some stop words
                if not (formatted in STOPS):
                    cut.append([formatted, stresses])

    return poem.strip() + '.'

if __name__ == '__main__':
    # Parse Arguments
    parser = ArgumentParser(description='Poem generator using cnnscrape.py')
    parser.add_argument('-m', '--Meter', help='Set meter', default='0,0,1')
    parser.add_argument('-b', '--Banned', help='Set list of words not to be considered in poem generation', default='')
    parser.add_argument('-ll', '--Line', help='Set line length', default=3)
    parser.add_argument('-pl', '--Poem', help='Set poem length', default=480)
    parser.add_argument('-o', '--Output', help='Set output file', default='poems.json')
    parser.add_argument('-ol', '--Log', help='Set output log file', default='workflow.log')
    args = parser.parse_args()

    # Generate poems using cnnscrape.py
    db = generate_todays_database()
    poems = {}
    for k in db.keys():
        p = makePoem(db[k].split(), [b for b in args.Banned.split(',')], [int(m) for m in args.Meter.split(',')], int(args.Line), int(args.Poem))
        poems[k] = p
    with open(args.Output, 'w') as file:
        json.dump(poems, file)
    
    # Log
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger_file_handler = logging.handlers.RotatingFileHandler(
        args.Log,
        maxBytes=1024 * 1024,
        backupCount=1,
        encoding='utf8',
    )
    formatter = logging.Formatter('%(asctime)s %(message)s')
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)
    logger.info('Generated ' + str(len(poems)) + ' poems with the arguments:' + str(args))