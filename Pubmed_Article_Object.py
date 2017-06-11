# This script scans an XML-results file exported from pubmed.com
# The output_run1 is a xls file
# The script folder must contain:
#
# pubmed_result.xls from http://www.ncbi.nlm.nih.gov/pubmed/;
# J_Medline.txt from ftp://ftp.ncbi.nih.gov/pubmed/J_Medline.txt;
# In_vivo_toxicity_models.csv;
# scimagojr.xls from http://www.scimagojr.com/journalrank.php;
# Codeautomation.py module file
# phantomJS.exe.exe in ./selenium/webdriver/ folder
#
# (c) Nikolay Kuriakin

import re
import xlrd
from selenium import webdriver
import codecs
from nltk import tokenize
import inflect

from Pubmed_logs import logline

p = inflect.engine()

singularKeys = {
                'MQ2_1': ["toxicity", "safety", "health", "exposure", "human", "people", "worker", "employee",
                          "man", "woman", "girls", "boy", "child", "infant", "adult", "consumer", "patient",
                          "volunteer", "clinical", "clinically", "cohort", "resident", "biomedical", "medical",
                          "public", "occupational", "cytotoxic", "cytotoxicity", "cytotoxin", "cytotoxins",
                          "teratogenicity", "teratogen", "teratogenic", "carcinogen", "carcinogenic",
                          "carcinogenicity", "neurotoxic", "neurotoxicity", "neurotoxin", "nephrotoxicity",
                          "nephrotoxic", "nephrotoxin", "hepatotoxicity", "hepatotoxin", "hepatotoxic",
                          "genotoxicity", "genotoxic", "genotoxin", "cancer", "review", "reviewed",
                          "NOAEL", "LOAEL", "NOEL", "LOEL", "TDI", "NOEC", "threshold limit value",
                           "TLV", "time-weighted average", "time weighted average", "TWA",
                          "provisional tolerable weekly intake", "PTWI", "NOAEC", "occupational exposure limit",
                           "OEL", "PEL", "effect level", "daily intake", "effective dose", "tolerable dose",
                           "lethal dose", "threshold dose", "effect concentration", "inhibitory concentration",
                          "permissible exposure level", "ground-level concentration", "ground level concentration",
                          "GLC",
                         "(LC|EC|LD|ED|IC)[ -]?\\(?(50|₅₀)\\)?"],

                'MQ3_1':["environment", "impact", "manufacturing", "consumption", "recycling", "disposal", "environmental",
                         "ecotoxicology", "ecotoxicological", "ecotoxicity", "ecological", "ecology", "sustainable",
                         "sustainably", "sustainability", "ecosystem", "trophic", "aquatic", "soil", "troposphere",
                         "tropospheric", "atmospheric", "river", "freshwater", "marine", "waste", "waste-water", "wastewater",
                         "biodiversity", "bio-indicator", "bioindicator", "biomonitor", "bio-monitor", "recovery", "recovered",
                         "recycled", "recycling", "recycle", "recyclable", "disposal", "life-cycle", "life cycle", "biodegradable",
                         "biodegradation", "biodegrade", "bio-degradable", "bio-degradation", "bio-degrade", "decompose",
                         "decomposed", "decomposition", "consumption"],

                'MQ4_1':["nanoparticle", "nanomaterial", "nanoscale", "nanosized", "nano", "ultrafine", "combustion",
                         "coal-derived", "coal-fired", "engine", "motor[ ]vehicle", "airborne", "incidental", "aerosols",
                         "naturally[ ]occurring", "dust", "mining", "raw[ ]material", "mineralogy", "ash"],

                'HUM': ["human", "people", "man", "mens", "woman", "girl", "boy", "child" "infant", "adult", "cohort"
                        "consumer", "clinical", "patient", "worker", "volunteer", "health", "employee", "resident",
                        "biomedical", "medical", "occupational", "workforce", "workplace", "public", "clinically"],

                'LVL': ["NOAEL", "no observed adverse effect level", "no observable adverse effect level", "LOAEL",
                        "lowest observed adverse effect level", "lowest observable adverse effect level", "NOEL",
                        "no observed effect level", "no observable effect level", "LOEL", "lowest observed effect level",
                        "lowest observable effect level", "TDI", "tolerable daily intake", "lethal dose", "tolerable dose",
                        "threshold dose",  "effective dose", "threshold limit value", "TLV", "NOEC",
                        "no observed effect concentration", "no observable effect concentration", "inhibitory concentration",
                        "time-weighted average", "time weighted average", "TWA", "provisional tolerable weekly intake",
                        "PTWI", "no observable adverse effect concentration", "no observed adverse effect concentration",
                        "NOAEC", "permissible exposure level", "PEL", "occupational exposure limit", "OEL",
                        "Acceptable Daily Intake", "ADI", "ground-level concentration", "ground level concentration",
                        "GLC", "GLCs", "(LC|EC|LD|ED|IC)[ -]?\\(?(50|₅₀)\\)?"],

                #'REV': ["review", "reviewed"],

                'CTX': ["cytotoxic", "cytotoxicity", "cytotoxin", "teratogen", "teratogenic", "teratogenicity",
                        "teratogenicities", "carcinogen", "carcinogenic", "carcinogenicity", "neurotoxin",
                        "neurotoxic", "neurotoxicity", "nephrotoxicity", "nephrotoxin", "nephrotoxic", "hepatotoxicity",
                        "hepatotoxin", "hepatotoxic", "genotoxic", "genotoxicity", "genotoxin", "cancer"],

                # 'ERM' :["ingest", "ingestion", "oral", "orally", "consumption", "consumed", "consume", "intake",
                #        "metabolism", "metabolic", "metabolise", "epidermis", "epidermal", "epithelial", "epithelium", "Dermal",
                #        "Dermis", "skin", "inhale", "inhaled", "inhalation", "dust", "vapour", "vapourised", "aerosoli[sz]ed",
                #        "aerosol", "atmospheric", "pulmonary", "bioaccumulation", "bioaccumulative", "uptake", "excretion",
                #        "bio[-]?available", "bioavailability", "synergist", "synergistic", "agonist", "agonistic",
                #        "antagonists", "antagonistic", "blood", "brain", "cortex", "liver", "plasma", "respiratory", "serum"],


                'ETX': ["ecotoxicology", "ecotoxicological", "ecotoxicology", "ecotoxicity", "toxicity", "toxic",
                       "trophic", "aquatic", "soil", "troposphere", "tropospheric", "atmospheric", "river", "freshwater", "marine",
                       "bio-indicator", "indicator", "community", "communities"],
                # 'IND': ["manufacturing", "manufacture", "manufactured", "industry", "industrial", "waste", "waste-water",
                #        "waste water", "wastewater", "recovery", "recovered", "produce", "produced", "production", "life-cycle",
                #        "life cycle", "commercial"],
                'SUS': ["sustainable", "sustainably", "sustainability", "recycled", "recycling", "recycle", "recyclable",
                       "disposal", "biodegradable", "biodegradation", "biodegrade", "bio-degradable", "bio-degradation",
                       "bio-degrade", "decompose", "decomposed", "decomposition", "ecological",  "recovery", "recovered",
                        "recovering", "bioremediation", "remediation", "reuse", "revegetation", "revegetated", "life-cycle",
                        "lifecycle", "life cycle",
                        "\(use|application|utilization\) of \(waste[s]?|wastewater[s]?|waste-water[s]?|waste[ ]water[s]?|sludge[s]?|discharge[s]?|discharged|discard[s]?|discarded\)",
                        "\(waste[s]?|wastewater[s]?|waste-water[s]?|waste[ ]water[s]?|sludge[s]?|discharge[s]?|discharged|discard[s]?|discarded\)[ ]\(use|application|utilization\)"]
}

EIVexceptions = ['tio', 'bicon', 'sio', 'old man', 'seal']
EITexceptions = ['nir', 'posterior', 'carrier', 'ria', 'cnt', 'pft']

regex_str = dict()
for key in singularKeys.keys():
    value = r"\b("
    for elem in singularKeys[key]:
            value += p.plural(elem).lower() + "|" if elem != "(LC|EC|LD|ED|IC)[ -]?\\(?(50|₅₀)\\)?" else ''
            value += elem.lower() + "|"
    value = value.rstrip('|') + r")\b"
    regex_str[key] = value

class MedlineDbJournal(object):
    def __init__(self, db_entry):

        def regex_JournalDb(section, datajourn):
            section_match = re.search(section + r': (.*?)\n', datajourn)
            if section_match:
                return section_match.group(1)
            else:
                return

        self.JournalTitle = regex_JournalDb('JournalTitle', db_entry)
        self.MedAbbr = regex_JournalDb('MedAbbr', db_entry)
        self.ISSN_Print = regex_JournalDb('ISSN \(Print\)', db_entry)
        self.ISSN_Online = regex_JournalDb('ISSN \(Online\)', db_entry)
        self.IsoAbbr= regex_JournalDb('IsoAbbr', db_entry)

    def __str__(self):
        return self.JournalTitle


class JournalArticle(object):

    def __init__(self, xml_elem, queryID, number, xml_file_name):

        if queryID == '2.1':
            if 'EIVset' not in locals() and 'EITset' not in locals():
                setWrds = set()
                with codecs.open(xml_file_name, 'r', encoding='utf-8') as Results:
                    for line in Results:
                        for character in line:
                            if not character.isalnum():
                                line = line.replace(character, ' ')
                        for word in line.strip().lower().split(' '):
                            setWrds.add(word)

                EIVset = {'germination', 'root', 'roots', 'in vivo', 'in-vivo'}

                with codecs.open('EIVkeys1.txt', 'r', encoding='utf-8') as EIVfull:
                    for organism in EIVfull:
                        if organism.strip().lower() not in EIVexceptions:
                            orgWords = organism.lower().strip().split(' ')
                            for Word in orgWords:
                                if Word in setWrds:
                                    EIVset.add(organism.lower().strip())
                                    break
                    try:
                        EIVset.remove('orange')
                    except KeyError:
                        pass
                    try:
                        EIVset.remove('')
                    except KeyError:
                        pass
                EITset = {"in vitro", "in-vitro", "cells", "cell", "cellular", "culture", "cultivated",
                          "library screen", "macrophages"
                          }
                with codecs.open('EIT7resulting_v_2_0.txt', 'r', encoding='utf-8') as output:
                    for line_output in output:
                        if line_output.strip().lower() not in EITexceptions:
                            if line_output != '\n':
                                EITset.add(line_output.strip().lower())

        def get_xml_prop(xml_path):
            xml_object = xml_elem.find(xml_path)
            try:
                return xml_object.text
            except AttributeError:
                return ''

        self.weight=0

        pmid = get_xml_prop('./MedlineCitation/PMID')
        pages = get_xml_prop('./MedlineCitation/Article/Pagination/MedlinePgn')
        self.articleTitle = get_xml_prop('./MedlineCitation/Article/ArticleTitle')
        self.lastName = get_xml_prop('./MedlineCitation/Article/AuthorList/Author/LastName')
        self.year = get_xml_prop('./MedlineCitation/Article/Journal/JournalIssue/PubDate/Year')
        self.JournalTitle = get_xml_prop('./MedlineCitation/Article/Journal/Title')
        self.reference = "{0}, {1}. ({2}). {3} ({4}). {5}".format(
            self.lastName,
            get_xml_prop('./MedlineCitation/Article/AuthorList/Author/Initials'),
            self.year,
            self.articleTitle,
            get_xml_prop('./MedlineCitation/Article/Journal/JournalIssue/Volume'),
            pages.split('-', 1)[0] + "." if pages else ''
        )

        self.link = "http://www.ncbi.nlm.nih.gov/pubmed/" + pmid
        lang = get_xml_prop('./MedlineCitation/Article/Language')
        try:
            self.articleAbstract = ' '.join(
                [i.text for i in xml_elem.findall('./MedlineCitation/Article/Abstract/AbstractText')]
            )
        except TypeError:
            self.articleAbstract = ''

        self.REV = ''
        try:
            for type in xml_elem.findall('./MedlineCitation/Article/PublicationTypeList/PublicationType'):
                if type.text.lower().strip() == "review":
                    self.REV = 'REV'
                    break
        except TypeError:
            pass

        journalTitleAbbr = get_xml_prop('./MedlineCitation/MedlineJournalInfo/MedlineTA')

        MedlineDatabase = list()
        with open('J_Medline.txt', 'r') as JOURNAL_FILE:
            JOURNAL_STR = ''.join(JOURNAL_FILE.readlines())
            listJournal = JOURNAL_STR.split('-' * 56)
            for Journal_Data in listJournal:
                if Journal_Data.strip():
                    MedlineDatabase.append(MedlineDbJournal(Journal_Data))

        for journal in MedlineDatabase:
            self.issn = self.issn_print = self.issn_online = ''
            if journal.MedAbbr == journalTitleAbbr:
                self.issn_print = journal.ISSN_Print
                self.issn_online = journal.ISSN_Online
                self.issn = (self.issn_print + " " if self.issn_print else '') + \
                            (self.issn_online + " " if self.issn_online else '')
                break

        # looking for impact factor in scimagojr.xls file
        journalDatabase = xlrd.open_workbook("scimagojr.xls")
        databaseSheet = journalDatabase.sheet_by_index(0)

        self.IF = 'not found'
        self.IFcode = ''
        if self.issn:
            for row_index in range(databaseSheet.nrows):
                databaseIssn=databaseSheet.cell(row_index, 3)
                if self.issn_print.replace('-', '') in databaseIssn.value:
                    self.IF = databaseSheet.cell(row_index, 4).value
                elif self.issn_online.replace('-', '') in databaseIssn.value:
                    self.IF = databaseSheet.cell(row_index, 4).value
            if self.IF != 'not found':
                if self.IF >= 5:
                    self.IFcode='IF'
                    #self.weight += 1

        # doi

        driver=webdriver.PhantomJS(executable_path='../selenium/webdriver/phantomJS.exe')
        driver.implicitly_wait(2)

        self.doi = get_xml_prop('./PubmedData/ArticleIdList/ArticleId[@IdType="doi"]')


        def click_cross_button():
            driver.find_element_by_xpath(ButtonXpath).click()

        if self.doi == '':
            driver.get('http://www.crossref.org/guestquery/?auth2='
                       + self.lastName + '&atitle2=' + self.articleTitle.lstrip('[').rstrip('].'))
            ButtonXpath = '//*[@id="mainContent2"]/div/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/form/table/tbody/tr[4]/td/input[1]'
            click_cross_button()
            try:
                doiLink=driver.find_element_by_xpath(
                    '//*[@id="mainContent2"]/div/table/tbody/tr/td/table[3]/tbody/tr[2]/td[2]/table/tbody/tr[6]/td/a')
                self.doi = doiLink.get_attribute('href').strip('http://dx.doi.org/')
            except:
                pass

        xml_result = ''
        if self.doi != '':
            driver.get('http://www.crossref.org/guestquery?doi=' + self.doi)
            ButtonXpath = '//*[@id="mainContent2"]/div/table/tbody/tr/td/table[4]/tbody/tr/td[2]/form/table/tbody/tr[3]/td/input'
            click_cross_button()
            xml_result=driver.find_element_by_xpath('//*[@id="mainContent2"]/div/table/tbody/\
                tr/td/table[4]/tbody/tr[2]/td[2]/table/tbody/tr[2]/td[2]/textarea').text
        try:
            self.crossrefCited= \
                xml_result.split('<crm-item name="citedby-count" type="number">', 1)[1].split('</crm-item>')[0]
        except IndexError:
            self.crossrefCited = ''

        if self.crossrefCited != '' and int(self.crossrefCited) >= 35:
            self.HC = 'HC'
            #self.weight += 1

        else:
            self.HC = ''
        if lang.lower() != 'eng':
            self.TR = 'TR'
        else:
            self.TR = ''

        if self.articleAbstract == '':
            self.NO = 'NO'
        else:
            self.NO = ''

        AbstractTitle = (self.articleTitle + ". " + self.articleAbstract).lower().replace('..', '.').replace('plasma torch', '')

        if queryID == '2.1':

            MQstring = re.compile(regex_str['MQ2_1'])
        elif queryID == '3.1':
            MQstring = re.compile(regex_str['MQ3_1'])
            ETXcodekey = re.compile(regex_str['ETX'])
            # INDcodekey = re.compile(regex_str['IND'])
            SUScodekey = re.compile(regex_str['SUS'])
        elif queryID == '4.1':
            MQstring = re.compile(regex_str['MQ4_1'])

        noMQ = True
        #self.HR = ''
        #if len(set(re.findall(MQstring, AbstractTitle.replace('atomic absorption spectrometry', '')
        #                                             .replace('atomic absorption spectroscopy', '')
        #                                             .replace('absorption atomic spectroscopy', '')
        #                                             .replace('absorption atomic spectrometry', '')))) >= 3:
            #self.HR = 'HR'
            #self.weight += 2
            #logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
            #        keyword_scanned=' '.join(set(re.findall(MQstring, AbstractTitle))), flags='HR')
            #noMQ = False

        #el

        if len(set(re.findall(MQstring, AbstractTitle#.replace('atomic absorption spectrometry', '')
                                                       # .replace('atomic absorption spectroscopy', '')
                                                       # .replace('absorption atomic spectroscopy', '')
                                                       # .replace('absorption atomic spectrometry', '')
                              ))) > 0:
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=' '.join([(x[0] if isinstance(x, tuple) else x) for x in re.findall(MQstring, AbstractTitle)]), flags='no NR')
            noMQ = False

        self.NR = self.HUM = self.LVL = self.CTX = ''
        #self.ERM = self.EXP = ''
        if queryID in ['3.1', '4.1']:
            self.EMIS = ''

        # Code assignment
        if queryID == '2.1':

            bodypartsList = str()
            with open('bodyparts.txt', 'r') as bodyparts:
                for line in bodyparts:
                    bodypartsList += "|" + line.strip().lower()
            bodypartsList.lstrip('|')

            if re.search(r'in[- ]vivo', self.articleTitle, re.IGNORECASE):
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract, location='Title',
                        keyword_scanned=re.search(r'in[- ]?vivo', self.articleTitle, re.IGNORECASE).group(0),
                        )
                self.codeWeight = 10
                self.code = 'EIV'
                stopINVIVO = True
            else:
                stopINVIVO = False

        HUMstring = re.compile(regex_str['HUM'])
        LVLstring = re.compile(regex_str['LVL'])
        #REVstring = re.compile(regex_str['REV'])
        CTXstring = re.compile(regex_str['CTX'])
        #ERMstring = re.compile(regex_str['ERM'])


        removeList = ["solar cell",
                      "fuel cell",
                      "photovoltaic cell",
                      "opv cell",
                      "fly ash",
                      "fly-ash",
                      "fly coal ash",
                      "bovine serum albumine"
                      "pulsed discharge plasma",
                      "plasma enhanced",
                      "inductively coupled plasma",
                      "emission-scanning",
                      "emission scanning",
                      "field emission microscopy"]

        AbstractTitleMod = str()
        for char in AbstractTitle:
            AbstractTitleMod += char if char.isalnum() or char == '.' else ' '
        for word in removeList:
            AbstractTitleMod = AbstractTitleMod.lower().replace(word, '')

        # function for creating a set of unique keywords found in Abstract and/or Title
        def unique_flag(regcomp):
            result = [x for x in re.findall(regcomp, AbstractTitleMod)]

            result1 = list()
            for elem in result:
                if isinstance(elem, tuple):
                    if elem[0]:
                        result1.append(elem[0])
                else:
                    result1.append(elem)
            return list(
                set(
                [p.singular_noun(x) if p.singular_noun(x) else
                 x for x in result1]
            ))

        if len(unique_flag(HUMstring)) >= 2 and queryID != '3.1':
            self.HUM = 'HUM'
            self.weight += (3 if queryID != '4.1' else 0)
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=' '.join(unique_flag(HUMstring)), flags='HUM')

        if len(unique_flag(LVLstring)) >= 1:
            self.LVL = 'LVL'
            self.weight += (3 if queryID != '4.1' else 0)
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=' '.join(unique_flag(LVLstring)),
                    flags='LVL')

        # if len(unique_flag(REVstring)) >= 1:
        #     self.REV = 'REV'
        #     self.weight += 2
        #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
        #         keyword_scanned=' '.join(unique_flag(REVstring)), flags='REV')

        if len(unique_flag(CTXstring)) >= 2:
            self.CTX='CTX'
            #self.weight += (3 if queryID != '4.1' else 0)
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=' '.join(unique_flag(CTXstring)), flags='CTX')

        # if len(unique_flag(ERMstring)) >= 2:
        #     self.ERM = 'ERM'
        #     self.weight += (2 if queryID != '4.1' else 0)
        #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
        #             keyword_scanned=' '.join(unique_flag(ERMstring)), flags='ERM')

        if queryID in ['3.1', '4.1'] and ('emission' in AbstractTitleMod):
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned='emission', flags='EMIS')
            self.EMIS = 'EMIS'
            self.weight += (0 if queryID != '4.1' else 1)

        if queryID == '2.1':
            for EITkey in EITset:
                if re.search(re.compile(r'\b' + EITkey + r'\b'), AbstractTitleMod):
                    AbstractTitleMod = AbstractTitleMod.replace(EITkey, "<EITkey>" + EITkey + "</EITkey>")

            for EIVkey in EIVset:
                if re.search(r'\b' + re.escape(EIVkey) + r'\b', AbstractTitleMod):
                    AbstractTitleMod = AbstractTitleMod.replace(EIVkey, "<EIVkey>" + EIVkey + "</EIVkey>")

        sentenceList = tokenize.sent_tokenize(AbstractTitleMod)

        keyFlag = dict()
        sentenceNumber = 0

        def check_NR(sent):
            if queryID != '4.1':
                nanoEIVlist = list()
                nanoEIV = open('EIV_Nano_exclude.txt', 'r')
                for nanoEIVterm in nanoEIV.readlines():
                    nanoEIVlist.append(nanoEIVterm.strip())

                EIVnanoRegex = ("(" + '|'.join(nanoEIVlist) + ')')

                if re.search(r'\bnano.*?\b', sent) and not re.search(r'\b' + EIVnanoRegex + r'\b', sent)\
                        and not 'nanovirus' in sent:
                    logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                            keyword_scanned=re.search(r'\bnano.*?\b', sent).group(0), flags='NR', location=locFlag)
                    return True
                else:
                    return False


        for sentence in sentenceList:
            locFlag = ''
            if sentenceNumber == 0:
                locFlag = 'Title'
            elif sentenceNumber <= 3:
                locFlag = '1stThree'
            else:
                locFlag = 'lastSents'

            # Checking flags
            if check_NR(sentence):
                self.NR = "NR"

            # if "exposure" in sentence and \
            #     re.search(r"\b(monitor[(ing)|(ed)]?|occupational|occurrence|model[(led)|(ling)]?|"
            #               r"hazard|worker[s]?|resident[s]?|health risk[s]?|human|industry)\b",
            #               sentence):
            #     self.EXP = "EXP"
            #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
            #             keyword_scanned=re.search(
            #                     r"\b(monitor[(ing)|(ed)]?|occupational|occurrence|model[(led)|(ling)]?|"
            #                     r"hazard|worker[s]?|resident[s]?|health risk[s]?|human|industry)\b",
            #                     sentence).group(0), flags='EXP', location=locFlag)

            if queryID == '2.1':

                if not stopINVIVO and re.search(r"\b" + bodypartsList + r"\b", sentence) and\
                        '<EIVkey>' in sentence:

                    keyFlag.update({'BodypartEIV' + locFlag:
                                re.search(r"\b" + bodypartsList + r"\b", sentence).group(0) + " " +
                                sentence.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0]
                            })

                if not stopINVIVO and re.search('isolate[sd]?', sentence) and \
                                    re.search('(microb(e|(ial)|(es))|bacteria[l]?)', sentence):
                    keyFlag.update({'BactIsolate' + locFlag:
                                        re.search('isolate[sd]?', sentence).group(0) + " " +
                                        re.search('(microb(e|(ial)|(es))|bacteria[l]?)', sentence).group(0)
                                    })

                if not stopINVIVO and '<EITkey>' in sentence and '<EIVkey>' in sentence:
                    keyFlag.update({'EIV+EIT' + locFlag:
                                        sentence.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0] + " " +
                                        sentence.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0]
                                    })

                if not stopINVIVO and '<EITkey>' in sentence:
                    keyFlag.update({'EIT' + locFlag: sentence.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0]})

                    if re.search('isolate[sd]?', sentence):
                        keyFlag.update({'EITisolate' + locFlag:
                                        sentence.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0] + " " +
                                        re.search('isolate[sd]?', sentence).group(0)
                                        })

                if not stopINVIVO and '<EIVkey>' in sentence:
                    keyFlag.update({'EIV' + locFlag: sentence.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0]})

            elif queryID == '3.1':
                def check3_1(code, codestr):
                    if re.findall(code, sentence):
                        keyFlag.update({codestr + locFlag:
                                       str(keyFlag.get(codestr + locFlag) + ' & ' if keyFlag.get(codestr + locFlag)
                                           else '') + ' & '.join(re.findall(code, sentence))})
                check3_1(ETXcodekey, 'ETX')
                #check3_1(INDcodekey, 'IND')
                check3_1(SUScodekey, 'SUS')

            sentenceNumber += 1

        if queryID == '2.1':
            # Assigning code according to the algorithm
            if "BodypartEIVTitle" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["BodypartEIVTitle"],
                        )
                self.codeWeight=10
                self.code='EIV'
            # 1a
            elif "EITisolateTitle" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EITisolateTitle"],
                        )
                self.codeWeight = 9
                self.code = 'EIT'
            # 1b
            elif "BactIsolateTitle" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["BactIsolateTitle"],
                        )
                self.codeWeight = 9
                self.code ='EIT'
            # 1c
            elif 'EIVTitle' in keyFlag.keys() and 'EIV+EITTitle' not in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EIVTitle"],
                        )
                self.codeWeight = 10
                self.code ='EIV'
            # 1d
            elif 'EITTitle' in keyFlag.keys() and 'EIV+EITTitle' not in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EITTitle"],
                        )
                self.codeWeight = 9
                self.code ='EIT'
            # 3
            elif 'EIV+EITTitle' in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EIV+EITTitle"],
                        )
                self.codeWeight = 9
                self.code ='EIT'

            elif "BodypartEIV1stThree" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["BodypartEIV1stThree"],
                        )
                self.codeWeight=10
                self.code='EIV'


            # 2a
            elif "EITisolate1stThree" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EITisolate1stThree"],
                        )
                self.codeWeight=9
                self.code ='EIT'
            # 2a
            elif "BactIsolate1stThree" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["BactIsolate1stThree"],
                        )
                self.codeWeight=9
                self.code ='EIT'
            # 2b
            elif 'EIV1stThree' in keyFlag.keys() and 'EIV+EIT1stThree' not in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EIV1stThree"],
                        )
                self.codeWeight=10
                self.code ='EIV'
            # 2c
            elif 'EIT1stThree' in keyFlag.keys() and 'EIV+EIT1stThree' not in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EIT1stThree"],
                        )
                self.codeWeight = 9
                self.code = 'EIT'
            # 4
            elif 'EIV+EIT1stThree' in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EIV+EIT1stThree"],
                        )
                self.codeWeight = 9
                self.code ='EIT'

            elif "BodypartEIVlastSents" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["BodypartEIVlastSents"],
                        )
                self.codeWeight=10
                self.code='EIV'

            # 5a
            elif "EITisolatelastSents" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EITisolatelastSents"],
                        )
                self.codeWeight=9
                self.code ='EIT'
            # 5a
            elif "BactIsolatelastSents" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["BactIsolatelastSents"],
                        )
                self.codeWeight=9
                self.code ='EIT'
            # 5b
            elif 'EIVlastSents' in keyFlag.keys() and 'EIV+EITlastSents' not in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EIVlastSents"],
                        )
                self.codeWeight=10
                self.code ='EIV'
            # 5c
            elif 'EITlastSents' in keyFlag.keys() and 'EIV+EITlastSents' not in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EITlastSents"],
                        )
                self.codeWeight=9
                self.code ='EIT'
            # 5d
            elif 'EIV+EITlastSents' in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EIV+EITlastSents"],
                        )
                self.codeWeight=9
                self.code ='EIT'
            elif not stopINVIVO:
                self.codeWeight = 7
                self.code = 'TOX'
                logline(number=number, assigned_code='TOX', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                            )

        elif queryID == '3.1':

            if 'ETXTitle' in keyFlag.keys():
                logline(number=number, assigned_code='ETX', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["ETXTitle"],
                        )
                self.codeWeight = 8
                self.code='ETX'
            elif 'SUSTitle' in keyFlag.keys():
                logline(number=number, assigned_code='SUS', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["SUSTitle"],
                        )
                self.codeWeight = 7
                self.code = 'SUS'
            # elif 'INDTitle' in keyFlag.keys():
            #     logline(number=number, assigned_code='IND', link=self.link,
            #             title=self.articleTitle, abstr=self.articleAbstract,
            #             location='Title', keyword_scanned=keyFlag["INDTitle"],
            #             )
            #     self.codeWeight = 7
            #     self.code = 'IND'

            elif keyFlag.get('ETX1stThree') and len(keyFlag.get('ETX1stThree').split(' & ')) >= 2:
                logline(number=number, assigned_code='ETX', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1stThree', keyword_scanned=keyFlag["ETX1stThree"],
                        )
                self.codeWeight = 8
                self.code='ETX'
            elif keyFlag.get('SUS1stThree') and len(keyFlag.get('SUS1stThree').split(' & ')) >= 2:
                logline(number=number, assigned_code='SUS', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1stThree', keyword_scanned=keyFlag["SUS1stThree"],
                        )
                self.codeWeight = 7
                self.code='SUS'
            # elif keyFlag.get('SUS1stThree') and len(keyFlag.get('SUS1stThree').split(' & ')) >= 2:
            #     logline(number=number, assigned_code='IND', link=self.link,
            #             title=self.articleTitle, abstr=self.articleAbstract,
            #             location='1stThree', keyword_scanned=keyFlag["IND1stThree"],
            #             )
            #     self.codeWeight = 7
            #     self.code = 'IND'

            elif len(keyFlag.get('ETX1stThree').split(' & ')) if keyFlag.get('ETX1stThree') else 0 \
                + len(keyFlag.get('ETXlastSents').split(' & ')) if keyFlag.get('ETXlastSents') else 0 >= 2:
                logline(number=number, assigned_code='ETX', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Abstract',
                        keyword_scanned=keyFlag["ETX1stThree"] if keyFlag.get('ETX1stThree') else ''+
                                        keyFlag["ETXlastSents"] if keyFlag.get('ETXlastSents') else '',
                        )
                self.codeWeight = 8
                self.code = 'ETX'
            elif len(keyFlag.get('ETX1stThree').split(' & ')) if keyFlag.get('ETX1stThree') else 0  \
                    + len(keyFlag.get('ETXlastSents').split(' & ')) if keyFlag.get('ETXlastSents') else 0 >= 1:
                logline(number=number, assigned_code='ETX', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Abstract',
                        keyword_scanned=keyFlag["ETX1stThree"] if keyFlag.get('ETX1stThree') else ''
                                        + keyFlag["ETXlastSents"] if keyFlag.get('ETXlastSents') else '',
                        )
                self.codeWeight = 7
                self.code = 'ETX'

            elif len(keyFlag.get('SUS1stThree').split(' & ')) if keyFlag.get('SUS1stThree') else 0  \
                    + len(keyFlag.get('SUSlastSents').split(' & ')) if keyFlag.get('SUSlastSents') else 0  >= 2:
                logline(number=number, assigned_code='SUS', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Abstract',
                        keyword_scanned=keyFlag["SUS1stThree"] if keyFlag.get('SUS1stThree') else ''
                                        + keyFlag["SUSlastSents"] if keyFlag.get('SUSlastSents') else '',
                        )
                self.codeWeight = 7
                self.code = 'SUS'

            elif len(keyFlag.get('SUS1stThree').split(' & ')) if keyFlag.get('SUS1stThree') else 0 +\
                    len(keyFlag.get('SUSlastSents').split(' & ')) if keyFlag.get('SUSlastSents') else 0  == 1:
                logline(number=number, assigned_code='SUS', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Abstract',
                        keyword_scanned=keyFlag["SUS1stThree"] if keyFlag.get('SUS1stThree') else ''
                                        + keyFlag["SUSlastSents"] if keyFlag.get('SUSlastSents') else '' ,
                        )
                self.codeWeight = 6
                self.code = 'SUS'
            # elif len(keyFlag.get('IND1stThree').split(' & ')) if keyFlag.get('IND1stThree') else 0 +\
            #         len(keyFlag.get('INDlastSents').split(' & ')) if keyFlag.get('INDlastSents') else 0 >= 2:
            #     logline(number=number, assigned_code='IND', link=self.link,
            #             title=self.articleTitle, abstr=self.articleAbstract,
            #             location='Abstract',
            #             keyword_scanned=keyFlag["IND1stThree"] if keyFlag.get('IND1stThree') else ''
            #                             + keyFlag["INDlastSents"] if keyFlag.get('INDlastSents') else '' ,
            #             )
            #     self.codeWeight = 7
            #     self.code = 'IND'
            # elif len(keyFlag.get('IND1stThree').split(' & '))  if keyFlag.get('IND1stThree') else 0 +\
            #         len(keyFlag.get('INDlastSents').split(' & '))  if keyFlag.get('IND1stThree') else 0 == 1:
            #     logline(number=number, assigned_code='IND', link=self.link,
            #         title=self.articleTitle, abstr=self.articleAbstract,
            #         location='Abstract',
            #             keyword_scanned=keyFlag["IND1stThree"] if keyFlag.get('IND1stThree') else ''
            #                              + keyFlag["INDlastSents"] if keyFlag.get('IND1stThree') else '',
            #             )
            #     self.codeWeight = 6
            #     self.code ='IND'

            else:
                self.codeWeight = 6
                self.code = 'ENV'
                logline(number=number, assigned_code='ENV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        )

        elif queryID == '4.1':
            taglist = list()
            # if re.search(r"\b(formation|occurrence|forms|occurs|occur)\b", AbstractTitle):
            #     tag.append('F')
            #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
            #             keyword_scanned=re.search(
            #                 r"\b(formation|occurrence|forms|occurs|occur)\b",
            #                 AbstractTitle).group(0), flags='NP-F', location='Title+Abstract')

            # if re.search(r"\b(manufacturing|manufacture|production|produces|produce)\b", AbstractTitle):
            #     tag.append('M')
            #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
            #             keyword_scanned=re.search(
            #                 r"\b(manufacturing|manufacture|production|produces|produce)\b",
            #                 AbstractTitle).group(0), flags='NP-M', location='Title+Abstract')
            #
            # if re.search(r"\b(consumption|consumer|consumed)\b", AbstractTitle):
            #     tag.append('C')
            #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
            #             keyword_scanned=re.search(
            #                 r"\b(consumption|consumer|consumed)\b",
            #                 AbstractTitle).group(0), flags='NP-C', location='Title+Abstract')
            def tagger(regexpr, tag):
                if re.search(regexpr, AbstractTitleMod):
                    taglist.append(tag)
                    logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                            keyword_scanned=re.search(regexpr, AbstractTitleMod).group(0), flags='NP-' + tag,
                            location='Title+Abstract')
            tagger(r"\b(recycling|recycled|recycle|recyclable|bioremediation|"
                         r"bio-remediation|remediation|reuse|re-use)\b", 'R')

            tagger(r"\b(disposal|disposed|biodegradable|bio-degradable|biodegradation|bio-degradation|"
                         r"biodegrade|bio-degrade)\b", 'D')

            self.code = 'NP' + ' ' + ', '.join(taglist)
            self.codeWeight = 6

            def flag41_checker(regexp, flagstr='', wgtadd=0):
                for sentence in sentenceList:
                    if re.search(regexp, sentence) \
                            and ((float(re.search(regexp, sentence).group(1)) < 500) if flagstr == 'SIZ' else True):   # including condition for SIZ flag

                        logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                                keyword_scanned=re.search(regexp, sentence).group(0),
                                flags=flagstr, location='Title+Abstract')
                        self.weight+=wgtadd
                        return flagstr
                return ''

            self.SIZ = flag41_checker(r"\b(\d{1,3}(\.\d)*)[ ]?nm\b", wgtadd=1, flagstr='SIZ')

            self.INC = flag41_checker(
                    r"(\b(incidental(ly)?|unintended|accidental(ly)?|combustion|engine[s]?|vehicle[s]?|ash[es]?) ((.)+ )?"
                    r"(nanoparticle[s]?|particle[s]?|NPs|nano)\b)|(\b(coal[- ]derived) ((.)+ )?"
                    r"(nanoparticle[s]?|NP[s]?|nano|particle[s]?|particulate[ ]matter)\b)",
                    wgtadd=5, flagstr='INC')

            self.NAT = flag41_checker(
                    r"(\b(natural(ly[ ]occurring)?) ((.)+ )?(nanoparticle[s]?|particle[s]?|NPs|nano)\b)|"
                    r"(\bmimic[s]?|biomimetic[s]?|biomimicry\b)",
                    wgtadd=5, flagstr='NAT')

            self.ENG = flag41_checker(
                    r"(\b(preparation|manmade|engineered|produce[sd]?|production|manufacture|manufacturing|manufactured|"
                    r"fabrication|fabricated|prepared|preparing|designed|design|designing|synthesized|"
                    r"synthesis|synthesize) ((.)+ )?(nanoparticle[s]?|particle[s]?|NPs|nano.+)\b)|"
                    r"(\b(nanoparticle[s]?|particle[s]?|NP[s]?|nano) ((.)+ )?(design|fabrication)\b)",
                    wgtadd=0 if (self.INC or self.NAT) else -1000, flagstr='ENG')

        # since exp is checked in every sentence
        # if self.EXP:
        #     self.weight += (2 if queryID != '4.1' else 0)

        # if self.EXP:
        #     self.weight = 0

        # self.LR = ''
        # if self.weight == 0:
        #     self.LR = 'LR'
        #     self.weight -= 1

        if not self.NR:
            self.SecondaryWeight = self.PrimaryWeight = self.codeWeight + self.weight
            if self.SecondaryWeight < 0:
                self.SecondaryWeight = self.PrimaryWeight = 0

        elif self.NR:
            self.SecondaryWeight = self.codeWeight + self.weight
            self.PrimaryWeight = 0

        if noMQ:
            self.NR = 'NR'
            self.SecondaryWeight = self.PrimaryWeight = 0

        if self.TR:
            self.SecondaryWeight = self.PrimaryWeight = 0

    def __str__(self):
        return self.details


if __name__ == '__main__':
    print(regex_str)