import codecs

with codecs.open('../EIT_lib/EIT7resulting_v_2_0.txt', 'r', encoding='utf-8') as read_file:
    Nano_orgs=codecs.open('EIT_Nano_exclude.txt', 'w', encoding='utf-8')
    nanoSet = set()
    for EITNanoName in read_file:
        if EITNanoName.lower().startswith('nano'):
            nanoSet.add(EITNanoName.strip().split(' ',1)[0])
    for entity in nanoSet:
        Nano_orgs.write(entity+'\n')
    Nano_orgs.close()