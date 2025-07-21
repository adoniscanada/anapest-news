import pickle
import random

ARTICLES = ['THE', 'AN']
PRONOUNS = ['HE', 'SHE', 'HIS', 'HER', 'THEY', 'THEIR', 'HIM', 'HERS', 'THEM', 'MY', 'IT']
CONJUNCTIONS = ['FOR', 'AND', 'NOR', 'BUT', 'OR', 'YET', 'SO', 'ALTHOUGH', 'AFTER', 'AS', 'WHILE', 'WHEN', 'WHEREAS', 'WHENEVER', 'WHEREVER', 'WHETHER', 'HOW', 'IF', 'THOUGH', 'BECAUSE', 'BEFORE', 'UNTIL', 'UNLESS', 'SINCE']
PREPOSITIONS = ['IN', 'FROM', 'OF', 'UNTO', 'UNTIL', 'UPON', 'TO', 'AT']
STOPS = ['ON', 'ARE', 'WAS', 'WERE', 'WITH', 'IS'] + ARTICLES + PRONOUNS + PREPOSITIONS

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
    cut = []
    syllable_count = 0
    position = 0
    newline = '<br />' if html else '\n'

    # Iterate through each word
    for i in text_list:
        key = word_to_key(i)
        fits = True

        if ((key in stressdict) or (i.isupper() and key in common_acronyms)) and not (key in words_to_keys(banned_words)):
            stresses = common_acronyms[key] if (i.isupper() and key in common_acronyms) else stressdict[key]
            # Add boolean rules here: (word is only considered if all rules equate to True)
            lineKeys = [word_to_key(j) for j in line]
            rules = [
                    # No consecutive polysyllabics
                    not (len(line) > 0 and len(stresses) > 1 and len(stressdict[lineKeys[-1]]) > 1),
                    # No articles into conjunctions
                    not (len(line) > 0 and _are_keys_in_subsets([key, lineKeys[-1]], [CONJUNCTIONS, ARTICLES])),
                    # No articles into prepositions
                    not (len(line) > 0 and _are_keys_in_subsets([key, lineKeys[-1]], [PREPOSITIONS, ARTICLES])),
                    # No consecutive prepositions
                    not (len(line) > 0 and _are_keys_in_subsets([key, lineKeys[-1]], [PREPOSITIONS, PREPOSITIONS])),
                    # No consecutive pronouns
                    not (len(line) > 0 and _are_keys_in_subsets([key, lineKeys[-1]], [PRONOUNS, PRONOUNS])),
                    # No starting a line on a stop
                    not (len(line) == 0 and key in STOPS),
                    # No prepositions into conjunctions
                    not (len(line) > 0 and _are_keys_in_subsets([key, lineKeys[-1]], [CONJUNCTIONS, PREPOSITIONS])),
                    # No duplicates within line
                    not (_are_keys_in_subsets([key], [lineKeys]))
            ]
            # Enforce rules
            for r in rules:
                if not r:
                    fits = False
                    break
            
            # Non-boolean rules
            # Format for poem
            formatted = _remove_all(['.',',',':','“','”'], i)
            fKey = word_to_key(formatted)
            # Ignore stresses of stressed monosyllabic words (assume stressed words can be read unstressed, but unstressed words cannot be stressed)
            if stresses == [1] and len(meter) > 0:
                stresses = [meter[position % len(meter)]]
            # Ignore secondary stresses (if not in meter)
            if not (2 in meter):
                stresses = [min(i, 1) for i in stresses]
            # Generalize articles
            if fKey in ARTICLES:
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
                    elif fKey in nonNoun:
                        formatted = formatted.lower()
                        if position % len(meter) == 0 and not (lineKeys[-1] in nonNoun):
                            line[-1] += ','

                    line.append(formatted)
                    count = len(stresses)
                    position += count
                    syllable_count += count
                    if position % len(meter) == 0:
                        if syllable_count >= desired_line_length:
                            if fKey in STOPS and syllable_count < desired_line_length * 2:
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
                                if len(poem) >= desired_poem_length and not word_to_key(formatted) in STOPS:
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

def _are_keys_in_subsets(keys : list, subsets : list):
    if len(keys) != len(subsets):
        return False
    for i in range(len(keys)):
        if not (keys[i] in subsets[i]):
            return False
    return True