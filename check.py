import re
print(re.search(r"({}_)?{}".format("no|not", 'healthy'), 'healthy').group(1))

a = dict()
a['k'] = 3
print(a.get('k'))

freqs = dict()
freqs['d'][0] += 1 if freqs.get('d') else [0,0]
print (freqs)