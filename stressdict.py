import pickle

d = {}

# CMU dict provided by https://github.com/Alexir/CMUdict/blob/master/cmudict-0.7b
with open('cmudict-0.7b', 'r') as file:
    for i in file:
        row = i.split()
        # Check alphabetical words with more than one letter.
        if row[0].isalpha() and len(row[0]) > 1:
            # Check each last character of each value to get stresses.
            stresses = []
            for j in row[1:]:
                # CMU supports 0 - No Stress, 1 - Primary Stress, 2 - Secondary Stress
                if j[-1] in ['0', '1', '2']:
                    stresses += j[-1]
            # Save word if it has less than 4 stresses.
            if len(stresses) < 4:
                d[row[0]] = [int(s) for s in stresses]

with open('stressdict.pkl', 'wb') as file:
    pickle.dump(d, file)