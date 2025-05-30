import pickle
import random

ARTICLES = ['THE', 'AN']
PRONOUNS = ['HE', 'SHE', 'HIS', 'HER', 'THEY', 'THEIR', 'HIM', 'HERS', 'THEM', 'MY']
CONJUNCTIONS = ['FOR', 'AND', 'NOR', 'BUT', 'OR', 'YET', 'SO', 'ALTHOUGH', 'AFTER', 'AS', 'WHILE', 'WHEN', 'WHEREAS', 'WHENEVER', 'WHEREVER', 'WHETHER', 'HOW', 'IF', 'THOUGH', 'BECAUSE', 'BEFORE', 'UNTIL', 'UNLESS', 'SINCE']
PREPOSITIONS = ['IN', 'FROM', 'OF', 'UNTO', 'UNTIL', 'UPON', 'TO']
STOPS = ['OF', 'ON', 'THE', 'AT', 'FROM', 'IN', 'TO', 'ARE', 'WAS', 'WERE', 'THEY', 'AND', 'WITH', 'IS']

# Load pre-computed stressdict (see gen_stress_dict.py)
stressdict = {}
with open('stressdict.pkl', 'rb') as file:
    stressdict = pickle.load(file)
# Store common acronyms that are misunderstood by cmudict
common_acronyms = {
    'AI' : [1, 0],
    'US' : [1, 0]
}

def generate_poem(text_list : list, banned_words : list = [], meter : list = [0, 0, 1], desired_line_length : int = 9, desired_poem_length : int = 120, html = True):
    if len(stressdict) == 0:
        return ''

    poem = ''
    line = []
    syllable_count = 0
    position = 0
    newline = '<br />' if html else '\n'

    # Iterate through each word
    for i in text_list:
        key = word_to_key(i)
        fits = True

        if ((key in stressdict) or (i.isupper() and key in common_acronyms)) and not (key in words_to_keys(banned_words)):
            stresses = common_acronyms[key] if (i.isupper() and key in common_acronyms) else stressdict[key]
            # Add rules here: (word is only considered if all rules equate to True)
            rules = [
                    # Non-consecutive polysyllabics
                    not (len(line) > 0 and len(stresses) > 1 and len(stressdict[word_to_key(line[-1])]) > 1),
                    # Skip duplicates
                    not (len(line) > 0 and word_to_key(i) == word_to_key(line[-1])),
                    # Non-consecutive articles
                    not (len(line) > 0 and word_to_key(i) in ARTICLES),
                    # No articles into conjunctions
                    not (len(line) > 0 and word_to_key(i) in CONJUNCTIONS and word_to_key(line[-1]) in ARTICLES),
                    # No articles into prepositions
                    not (len(line) > 0 and word_to_key(i) in PREPOSITIONS and word_to_key(line[-1]) in ARTICLES),
                    # No prepositions into prepositions
                    not (len(line) > 0 and word_to_key(i) in PREPOSITIONS and word_to_key(line[-1]) in PREPOSITIONS),
                    # No pronouns into pronouns
                    not (len(line) > 0 and word_to_key(i) in PRONOUNS and word_to_key(line[-1]) in PRONOUNS)
            ]
            # Enforce rules
            for r in rules:
                if not r:
                    fits = False
                    break
            
            # Ignore stresses of stressed monosyllabic words (assume stressed words can be read unstressed, but unstressed words cannot be stressed)
            if stresses == [1] and len(meter) > 0:
                stresses = [meter[position % len(meter)]]
            
            # Ignore secondary stresses (if not in meter)
            if not (2 in meter):
                stresses = [min(i, 1) for i in stresses]

            if fits:
                # Enforce meter (skipped if length of meter is 0)
                for j in range(len(stresses)):
                    if len(meter) > 0 and stresses[j] != meter[(position + j) % len(meter)]:
                        fits = False
                        break
                
                # Add word to poem
                if fits:
                    formatted = _remove_all(['.',',',':','“','”'], i)
                    if len(line) == 0:
                        formatted = formatted[0].upper() + formatted[1:]
                    elif word_to_key(formatted) in ARTICLES + CONJUNCTIONS + PRONOUNS + PREPOSITIONS:
                        formatted = formatted.lower()
                        if position % len(meter) == 0 and line[-1] != '.':
                            line[-1] += ','

                    line.append(formatted)
                    count = len(stresses)
                    position += count
                    syllable_count += count
                    if position % len(meter) == 0:
                        if syllable_count >= desired_line_length:
                            if word_to_key(formatted) in STOPS and syllable_count < desired_line_length * 1.5:
                                line[-1] += '...'
                            else:
                                # Check poem length
                                if len(poem) >= desired_poem_length and not word_to_key(formatted) in STOPS:
                                    poem += ' '.join(line) + '.'
                                    return poem
                                
                                poem += ' '.join(line) + newline
                                
                                # Divide stanzas
                                if len(line) < desired_line_length - 1:
                                    poem += newline
                                
                                line.clear()
                                syllable_count = 0

    return poem + '.'

def word_to_key(word : str, upper : bool = True):
    w = word.upper() if upper else word
    return _remove_all(['.',',',':','“','”','’'], w)

def words_to_keys(words : list):
    return [word_to_key(word) for word in words]

def _remove_all(list : list, word : str):
    w = word
    for i in list:
        w = w.replace(i, '')
    return w