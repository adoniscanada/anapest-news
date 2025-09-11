ARTICLES = ['THE', 'AN']
PRONOUNS = ['HE', 'SHE', 'HIS', 'HER', 'THEY', 'THEIR', 'HIM', 'HERS', 'THEM', 'MY', 'IT']
CONJUNCTIONS = ['FOR', 'AND', 'NOR', 'BUT', 'OR', 'YET', 'SO', 'ALTHOUGH', 'AFTER', 'AS', 'WHILE', 'WHEN', 'WHEREAS', 'WHENEVER', 'WHEREVER', 'WHETHER', 'HOW', 'IF', 'THOUGH', 'BECAUSE', 'BEFORE', 'UNTIL', 'UNLESS', 'SINCE']
PREPOSITIONS = ['IN', 'FROM', 'OF', 'UNTO', 'UNTIL', 'UPON', 'TO', 'AT']
STOPS = ['ON', 'ARE', 'WAS', 'WERE', 'WITH', 'IS'] + ARTICLES + PRONOUNS + PREPOSITIONS
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def wordkey(word : str, upper : bool = True):
    _word = word if (not upper) else word.upper()
    w = ''
    for i in _word:
        if i in LETTERS:
            w += i
    return w

def words_are_types(words : list, t : list, exact : bool):
    if len(words) != len(t):
        return False
    for i in range(len(words)):
        k = words[i] if exact else wordkey(words[i])
        if not (k in t[i]):
            return False
    return True