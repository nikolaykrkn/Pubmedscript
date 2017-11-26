# -*- coding: utf-8 -*-


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

def pl(word):
    return word + "|" + p.plural(word)


notnp = [pl('nucleoside[ ]?phosphorylase'), pl('nucleotide[ ]?pair'), pl('Nucleotide[ ]?Protein'), pl('neuropeptide'), pl('neuropathy'),
         pl('Neuro[ ]?Pathology'), pl('NeuroPathology'), 'neuropsychiatric', 'Nickel[ ]?Plated', pl('nitrogen[ ]?phosphorus'),
         pl('nitroprusside'), pl('nonylphenol'), pl('nonapeptide'), pl('nonhistone[ ]?protein'), pl('nosocomial[ ]?pneumonia'),
         pl('N[ ]?protein'), pl('nasal[ ]?polyp'), pl('nasal[ ]?pack'), pl('nasopharyngeal'), 'No[ ]?Phosphate', 'No[ ]?Phosphorus',
         pl('natriuretic[ ]?peptide'), 'Normal[ ]?Probability', 'Neptunium', pl('nonylphenol')]

notnpregex = r'(' + r'|'.join(notnp) + r') \(np[s]?\)\b'

singularKeys = {
                'MQ2_1': [pl('toxicity'), 'toxic', pl('safety'), 'health', pl('exposure'), pl('human'),
                          'people', pl('worker'), pl('employee'), pl('man'), pl('woman'), pl('girl'),
                          pl('boy'), pl('child'), pl('infant'), pl('adult'), pl('consumer'), pl('patient'),
                          pl('volunteer'), 'clinical', 'clinically', pl('cohort'), pl('resident'),
                          'biomedical', 'medical', 'public', 'occupational', 'cytotoxic', pl('cytotoxicity'),
                          pl('cytotoxin'), pl('teratogenicity'), pl('teratogen'), 'teratogenic',
                          pl('carcinogen'), 'carcinogenic', pl('carcinogenicity'), 'neurotoxic', pl('neurotoxicity'),
                          pl('neurotoxin'), pl('nephrotoxicity'), 'nephrotoxic', pl('nephrotoxin'),
                          pl('hepatotoxicity'), pl('hepatotoxin'), 'hepatotoxic', pl('genotoxicity'),
                          'genotoxic', pl('genotoxin'), pl('cancer'), pl('review'), 'reviewed', 'NOAEL',
                          'NOAELs', 'LOAEL', 'LOAELs', 'NOEL', 'NOELs', 'LOEL', 'LOELs', 'TDI', 'TDIs',
                          'NOEC', 'NOECs', pl('threshold limit value'), 'TLV', 'TLVs', pl('time[-]?weighted average'),
                          'TWA', 'TWAs', pl('provisional tolerable weekly intake'), 'PTWI', 'PTWIs', 'NOAEC', 'NOAECs',
                          pl('occupational exposure limit'), 'OEL', 'OELs', 'PEL', 'PELs', pl('effect level'),
                          pl('daily intake'), pl('effective dose'), pl('tolerable dose'), pl('lethal dose'),
                          pl('threshold dose'), pl('effect concentration'), pl('inhibitory concentration'),
                          pl('permissible exposure level'), pl('ground[-]?level concentration'), 'GLC', 'GLCs',
                          'bioaccumulation', 'bio-accumulation', 'bio-accumulative', 'bioaccumulative',
                          'accumulation', 'intake', 'consumption',"(?:lc|ec|ld|ed|ic)[ -]?\\(?(?:50|₅₀)\\)?"],

                'MQ3_1-A': ["ecotoxicology", "ecotoxicological", pl("ecotoxicity"), pl("toxicity"), "pollution",
                            pl("pollutant"), pl("exposure"), pl("sustainability"), "sustainable", "sustainably"],

                'MQ3_1-B': ["accumulation", "aquatic", "atmosphere", "atmospheric", "bio-accumulation",
                            "bio-degradable", "bio-degradation", "bio-degrade", "bio-indicator", "bio[ -]?monitor",
                            "bio[ -]?monitoring", "bioaccumulation", "biodegradable", "biodegradation", "biodegrade",
                            "biodiversity", "bioindicator", "consumption", "contamination", "decontamination",
                            pl("discharge"), pl("discharged"), "disposal", "ecological", "ecology", "ecosystem",
                            pl("emission"), "environmental", "freshwater", "fresh-water", "indicator species",
                            "life[ -]cycle", "marine", "model system", "recovered", "recovery", "recyclable",
                            "recycle", "recycled", "recycling", pl("resource"), pl("river"), pl("ocean"),
                            pl("sea"), pl("lake"), pl("soil"), "trophic", "troposphere", "tropospheric", pl("waste"),
                            pl("waste water"), pl("waste-water"), pl("wastewater")],

                'MQ4_1-A': [pl('nanoparticle'), pl('nanomaterial'), 'nanoscale', 'nano[ ]?size',
                            'nano[ ]?sized', 'ultrafine', pl('dust'), 'aerosol', pl('np'), 'nano\w+?',
                            'nanometric', pl('nanotube'), 'fly ash', 'particle[ ]size', 'particle diameter',
                            'size distribution'],

                'MQ4_1-B':['incidental', 'naturally occurring', 'anthropogenic', 'natural', pl('emission'), 'emitted',
                           pl('source'), 'disposal', 'anthropogenic', pl('by-product'), pl('by-products'),
                           pl('byproduct')],

                'HUM': [pl('human'), 'people', pl('man'), 'mens', 'men’s', 'man’s',  pl('woman'), "woman's",
                        'women’s', pl('girl'), pl('boy'), pl('child'), pl('infant'), pl('adult'), pl('cohort'),
                        pl('consumer'), 'clinical', pl('patient'), "patient's", pl('worker'), pl('volunteer'),
                        'health', pl('employee'), pl('resident'), 'occupational', 'workforce', pl('workplace'),
                        'clinically'],

                'LVL': [pl('noael'), pl('no observed adverse effect level'), pl('no observable adverse effect level'),
                        pl('loael'), pl('lowest observed adverse effect level'),
                        pl('lowest observable adverse effect level'), pl('noel'), pl('no observed effect level'),
                        pl('no observable effect level'), pl('loel'), pl('lowest observed effect level'),
                        pl('lowest observable effect level'), pl('tdi'), pl('tolerable daily intake'),
                        pl('lethal dose'), pl('tolerable dose'), pl('threshold dose'), pl('effective dose'),
                        pl('threshold limit value'), pl('tlv'), pl('noec'), pl('no observed effect concentration'),
                        pl('no observable effect concentration'), pl('inhibitory concentration'),
                        pl('time[ -]?weighted average'), pl('twa'), pl('provisional tolerable weekly intake'),
                        pl('ptwi'), pl('no observable adverse effect concentration'),
                        pl('no observed adverse effect concentration'), pl('noaec'),
                        pl('permissible exposure level'), pl('pel'), pl('occupational exposure limit'),
                        pl('oel'), pl('acceptable daily intake'), pl('adi'), pl('ground[ -]?level concentration'),
                        pl('glc'), "(lc|ec|ld|ed|ic)[ -]?\\(?(50|₅₀)\\)?"
                        ],

                'CTX': ['cytotoxic', pl('cytotoxicity'), pl('cytotoxin'), pl('teratogen'), 'teratogenic',
                        pl('teratogenicity'), pl('carcinogen'), 'carcinogenic', pl('carcinogenicity'), pl('neurotoxin'),
                        'neurotoxic', pl('neurotoxicity'), pl('nephrotoxicity'), pl('nephrotoxin'), 'nephrotoxic',
                        pl('hepatotoxicity'), pl('hepatotoxin'), pl('hepatotoxic'), 'genotoxic', pl('genotoxicity'),
                        pl('genotoxin'), pl('cancer'), pl('neuro[-]?developmental toxicity')],

                'TOX-A': [pl('exposure'),'health', pl('safety'), 'toxic', pl('toxicity')],
                'TOX-B': ['accumulation', pl('daily intake'),  "(lc|ec|ld|ed|ic)[ -]?\\(?(50|₅₀)\\)?[s]?",
                          pl('effect concentration'), pl("effect level"), pl("effective dose"),
                          pl('ground level concentration'), pl('ground-level concentration'),
                          pl("inhibitory concentration"), pl("lethal dose"), pl("occupational exposure limit"),
                          pl("permissible exposure level"), pl("provisional tolerable weekly intake"),
                          pl("threshold dose"), pl("threshold limit value"), pl("time weighted average"),
                          pl("time-weighted average"), pl("tolerable dose"), pl("adult"), "bio-accumulation",
                          "bio-accumulative", "bioaccumulation", "bioaccumulative", "biomedical", pl("boy"),
                          pl("cancer"), pl("carcinogen"), "carcinogenic", pl("carcinogenicity"), pl("child"),
                          "clinical", "clinically", pl("cohort"), pl("consumer"), "consumption", "cytotoxic",
                          pl("cytotoxicity"), pl("cytotoxin"), pl("employee"), "genotoxic",  pl("genotoxicity"),
                          pl("genotoxin"), pl("girl"), pl("GLC"), 'hepatotoxic', pl("hepatotoxicity"), pl("hepatotoxin"),
                          pl("human"), pl("human"), pl("infant"), "intake", pl("LOAEL"), pl("LOEL"), pl("man"),
                          "medical", "nephrotoxic", pl("nephrotoxicity"), pl("nephrotoxin"), "neurotoxic",
                          pl("neurotoxicity"), pl("neurotoxin"), pl("NOAEC"), pl("NOAEL"), pl("NOEC"), pl("NOEL"),
                          "occupational", pl("OEL"), pl("patient"), pl("PEL"), "people",  pl("PTWI"), "public",
                          pl("resident"), pl("review"), "reviewed", pl("TDI"), pl("teratogen"), "teratogenic",
                          pl("teratogenicity"), pl("TLV"), pl("TWA"), pl("volunteer"), pl("woman"), pl("worker")],

                'EIT-B': ['bio-assay', 'bio-indicator', 'bioassay', 'bioindicator', pl('cell'), 'cellular',
                          'cultivated', 'cultured', 'in vitro', 'in-vitro', 'model system'],
                'EIV-B': [pl('animal'), "in vivo", "in-vivo" "live", "living", pl("organism")],

                'ETX-A': ["ecotoxicology", "ecotoxicological", pl("ecotoxicity"), "toxicities", "toxicity",
                          pl("exposure")],

                'ETX-B': [
                          pl('noael'), pl('loael'), pl('noel'), pl('loel'), pl('tdi'), pl('noec'),
                          pl('threshold limit value'), pl('tlv'), "(lc|ec|ld|ed|ic)[ -]?\\(?(50|₅₀)\\)?s?",
                          pl('noaec'), pl('effective dose'), pl('tolerable dose'), pl('lethal dose'),
                          pl('threshold dose'), pl('effect concentration'),  pl('inhibitory concentration'),
                          pl('permissible exposure level'), pl('ground[ -]?level concentration'), pl('glc')],



                'SUS-A': ["bio[ -]?degradable", "bio[- ]?degradation", "bio[ -]?degrade", "biodegradable", "conservation",
                          "conserving", "bioremediation", "contaminant", "contaminated", "contamination", "decontamination",
                          "depletion", pl("life[- ]?cycle"), "recovered", "recovery", "recyclable", "recycle", "recycled",
                          "recyclability", "recycling", "remediation", "restoration", "sustainability", "sustainable",
                          "sustainably", pl("waste"), pl("waste[- ]?water"), pl("discharge"), "discharged", pl("emission"),
                          "dregs", "garbage", "sewage"],

                'SUS-B': [pl("resource"), pl("soil"), pl("water"), "air", pl("river"), pl("ocean"), pl("sea"), "fresh[- ]?water",
                          "aquatic", "atmosphere", "atmospheric", "marine", "coastal", pl("lake"), "mud", "sludge",
                          "clay", "sediment", pl("crop"), "biota", pl("animal"), "vegetation", pl("woodland"), pl("forest")
                          ],

                'INC-A': ['incidental', 'unintentional', 'unintended', pl('emission'),
                          pl('byproduct'), pl('by-product'), 'emitted', pl('source'), 'disposal', 'anthropogenic'],
                'INC-B': [pl('nanoparticle'), pl('np'), 'nano', pl('nano-particle'), pl('dust'), pl('particle'),
                          'nanoscale', 'nano.+?[ -]', 'fly ash'],

                'NAT-A': ['natural', 'naturally occurring'],
                'NAT-B': [pl('nanoparticle'), pl('np'), 'nano', pl('nano-particle'), pl('dust'), pl('particle'),
                          'nanoscale', 'nano.+?'],

                'SIZ-A': ['nano scale', pl('particle size'), pl('particle diameter'), 'size distribution',
                        'd10', 'd50', 'd90', 'nanometric'],

                'ENG-A': ['engineered', 'engineer', 'manufactured', 'manufacture', 'fabrication', 'fabricated',
                          'design', 'designed', 'synthetic', 'synthesize', 'synthesis', 'prepare', 'prepared',
                          'preparation', 'synthesized', 'commercial', "artificial", "functionalized", "commercially"],
                'ENG-B': [pl('np'), 'nano', pl('nano-particle'), pl('dust'), pl('particle'),
                          'nanoscale', 'nano.+?[ -]']
}

EIVexceptions = ['tio', 'bicon', 'sio', 'old man', 'seal', 'ash', 'iso', 'plane', 'planes', 'aa', 'hand']
EITexceptions = ['nir', 'posterior', 'carrier', 'ria', 'cnt', 'pft',
                 'tem', 'chloride', 'nmr', 'phosphate', 'tar', 'ash', 'root', 'roots','plane', 'planes']

Exclusions = ['graphene liquid cells glc', 'dual emission']

regex_str = dict()
for key in singularKeys.keys():
    value = r"\b("
    for elem in singularKeys[key]:
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

    def __init__(self, xml_elem, queryID, substance, number, xml_file_name):

        self.code=str()

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

                EIVset = {'germination', 'in vivo', 'in-vivo',  "exaiptasia pallida", "isochrysis galbana"}

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
                          "library screen", "macrophages", "bioluminescence inhibition"
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
            try:
                xml_result=driver.find_element_by_xpath('//*[@id="mainContent2"]/div/table/tbody/\
                    tr/td/table[4]/tbody/tr[2]/td[2]/table/tbody/tr[2]/td[2]/textarea').text
            except:
                xml_result = None
        try:
            self.crossrefCited= \
                xml_result.split('<crm-item name="citedby-count" type="number">', 1)[1].split('</crm-item>')[0]
        except (IndexError, AttributeError):
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

        AbstractTitle = (self.articleTitle + ". " + self.articleAbstract).lower().replace('..', '.')

        for excl in Exclusions:
            AbstractTitle = AbstractTitle.replace(excl, '')

        if queryID == '4.1' and re.sub(notnpregex.lower(), '', AbstractTitle, re.I):
            AbstractTitle = AbstractTitle.replace(r'np', '')


        if queryID == '2.1':
            MQstring = re.compile(regex_str['MQ2_1'], re.I)

        elif queryID == '3.1':
            MQstring_A = re.compile(regex_str['MQ3_1-A'], re.I)
            MQstring_B = re.compile(regex_str['MQ3_1-B'], re.I)
            ETX_A = re.compile(regex_str['ETX-A'], re.I)
            ETX_B = re.compile(regex_str['ETX-B'], re.I)
            SUS_A = re.compile(regex_str['SUS-A'], re.I)
            SUS_B = re.compile(regex_str['SUS-B'], re.I)

        elif queryID == '4.1':
            MQstring_A = re.compile(regex_str['MQ4_1-A'], re.I)
            MQstring_B = re.compile(regex_str['MQ4_1-B'], re.I)
            INC_A = re.compile(regex_str['INC-A'], re.I)
            INC_B = re.compile(regex_str['INC-B'], re.I)
            NAT_A = re.compile(regex_str['NAT-A'], re.I)
            NAT_B = re.compile(regex_str['NAT-B'], re.I)
            NAT_dir=re.compile(
                r"\b" + regex_str['NAT-A'].strip("\\b") + ' ' + regex_str['NAT-B'].strip("\\b") + r"\b",
                re.I)

            ENG_A = re.compile(regex_str['ENG-A'], re.I)
            ENG_B = re.compile(regex_str['ENG-B'], re.I)
            SIZ_A = re.compile(regex_str['SIZ-A'], re.I)
            SIZ_B = re.compile(r"(\d{1,3}(\.\d+)*)([ ](\d{1,3}(\.\d+)*))?[ ]?([nμ]m)", re.I)


        noMQ = True

        # if len(set(re.findall(MQstring, AbstractTitle#.replace('atomic absorption spectrometry', '')
        #                                                # .replace('atomic absorption spectroscopy', '')
        #                                                # .replace('absorption atomic spectroscopy', '')
        #                                                # .replace('absorption atomic spectrometry', '')
        #                       ))) > 0:
        #     logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
        #             keyword_scanned=' '.join([(x[0] if isinstance(x, tuple) else x) for x in re.findall(MQstring, AbstractTitle)]), flags='no NR')
        #     noMQ = False

        self.NR = self.HUM = self.LVL = self.CTX = ''
        self.NRkeys = self.HUMkeys = self.LVLkeys = self.CTXkeys = ''

        # Code assignment




        self.MQkey = self.INCkey = self.NATkey = self.SIZkey = self.ENGkey = self.NRkey = str()
        self.EIVkey = self.EITkey = str()
        self.EIV=self.EIT= self.TOX = str()
        self.MQ = self.INC = self.NAT = self.SIZ = self.ENG = self.NR = str()
        self.codekey1 = self.codekey2 = self.codekey3 = self.codekey4 = self.codekey5 = str()
        self.code1 = self.code2 = self.code3 = self.code4 = self.code5 = "ENV"
        self.codeReason=str()


        if queryID == '2.1':
            EIVkeysSet = set()
            EITkeysSet = set()

            bodypartsArray = list()
            with open('bodyparts.txt', 'r') as bodyparts:
                for line in bodyparts:
                    bodypartsArray.append("(" + line.strip().lower() + ")")
            bodypartsList = '|'.join(bodypartsArray)

            if re.search(r'in[- ]vivo', self.articleTitle, re.IGNORECASE):
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract, location='Title',
                        keyword_scanned=re.search(r'in[- ]?vivo', self.articleTitle, re.IGNORECASE).group(0),
                        )
                self.codeWeight = 10
                self.EIV = 'EIV'
                EIVkeysSet.add(re.search(r'in[- ]?vivo', self.articleTitle, re.IGNORECASE).group(0) + " [in Title]")
                stopINVIVO = True
                self.codeReason = "In Vivo in Title"
            else:
                stopINVIVO = False

        HUMstring = re.compile(regex_str['HUM'])
        LVLstring = re.compile(regex_str['LVL'])
        CTXstring = re.compile(regex_str['CTX'])


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
                      "field emission microscopy",
                      "discharge capacity",
                      "atmospheric pressure",
                      "plasma torch"]

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
                                [p.singular_noun(x) if p.singular_noun(x) else x for x in result1]
                            )
                        )

        if len(unique_flag(HUMstring)) >= 1 and queryID not in ('3.1', '4.1'):
            self.HUM = 'HUM'
            self.HUMkeys = ' '.join(unique_flag(HUMstring))
            self.weight += 3
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=self.HUMkeys, flags='HUM')


        if len(unique_flag(LVLstring)) >= 1:
            self.LVL = 'LVL'
            self.LVLkeys = ' '.join(unique_flag(LVLstring))
            self.weight += (3 if queryID != '4.1' else 0)
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=self.LVLkeys,
                    flags='LVL')

        if len(unique_flag(CTXstring)) >= 1:
            self.CTX = 'CTX'
            self.CTXkeys = ' '.join(unique_flag(CTXstring))
            logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                    keyword_scanned=self.CTXkeys, flags='CTX')



        if queryID == '2.1':
            for EITkey in EITset:
                if re.search(re.compile(r'\b' + EITkey + r'\b'), AbstractTitleMod):
                    AbstractTitleMod = AbstractTitleMod.replace(EITkey, "<EITkey>" + EITkey + "</EITkey>")
            for EIVkey in EIVset:
                if re.search(r'\b' + re.escape(EIVkey) + r'\b', AbstractTitleMod):
                    AbstractTitleMod = AbstractTitleMod.replace(EIVkey, "<EIVkey>" + EIVkey + "</EIVkey>")

        sentenceList = tokenize.sent_tokenize(AbstractTitleMod)

        keyFlag = dict()



        def check_NR(sent):
            if queryID != '4.1':
                nanoEIVlist = list()
                nanoEIV = open('EIV_Nano_exclude.txt', 'r')
                for nanoEIVterm in nanoEIV.readlines():
                    nanoEIVlist.append(nanoEIVterm.strip())

                EIVnanoRegex = ("(" + '|'.join(nanoEIVlist) + ')')

                if re.search(r'\bnano.*?\b', sent) and not re.search(r'\b' + EIVnanoRegex + r'\b', sent)\
                        and not 'nanovirus' in sent:
                    self.NRkeys = re.search(r'\bnano.*?\b', sent).group(0)
                    #logline(number=number, link=self.link, title=self.articleTitle, abstr=self.articleAbstract,
                     #       keyword_scanned=self.NRkeys, flags='NR', location=locFlag)
                    return True
                else:
                    return False


        if queryID == '3.1':

            if len(re.findall(r'\b' + "|".join(substance) + r'\b', AbstractTitleMod)) >= 2 \
                    and re.findall(ETX_A, AbstractTitleMod):
                self.codekey1 += '[' + ', '.join(re.findall(r'\b' + "|".join(substance) + r'\b', AbstractTitleMod)) + \
                             " + " + ", ".join(re.findall(ETX_A, AbstractTitleMod)) + " (A)]; "
                self.code1 = "ETX"

            if len(re.findall(r'\b' + "|".join(substance) + r'\b', AbstractTitleMod)) >= 2 \
                    and re.findall(SUS_A, AbstractTitleMod):
                self.codekey1 += '[' + ', '.join(re.findall(r'\b' + "|".join(substance) + r'\b', AbstractTitleMod)) + \
                             " + " + ', '.join(re.findall(SUS_A, AbstractTitleMod)) + " (A)]; "
                if self.code1 == "ETX":
                    self.code1 = "SUS/ETX"
                else:
                    self.code1 = "SUS"

            if re.findall(ETX_A, AbstractTitleMod):
                self.codekey4 += "[" + ", ".join(re.findall(ETX_A, AbstractTitleMod)) + " (A)]; "
                self.code4 = "ETX"
            if re.findall(SUS_A, AbstractTitleMod):
                self.codekey4 += "[" + ", ".join(re.findall(SUS_A, AbstractTitleMod)) + " (A)]; "
                if self.code4 == "ETX":
                    self.code4 = "SUS/ETX"
                else:
                    self.code4 = "SUS"

            sub_title=str()

        self.MQkeyNum = 0



        sentenceNumber = 0
        for sentence in sentenceList:


            def flag_key_word(subst, regex1, regex2, sent=sentence):
                return "[" + subst + ' ' + ', '.join(re.findall(regex1, sent)) + '(A) + ' \
                       + ', '.join([(x[0] if isinstance(x, tuple) else x) for x in re.findall(regex2, sent)]) + '(B)' + "]; "



            if queryID != '2.1' and re.findall(MQstring_A, sentence) and re.findall(MQstring_B, sentence):

                self.MQ = "MQ"
                self.MQkey += flag_key_word('', MQstring_A, MQstring_B)
                self.MQkeyNum += len(re.findall(MQstring_A, sentence)) + len(re.findall(MQstring_B, sentence))
                noMQ = False

            elif queryID == '2.1' and re.findall(MQstring, sentence):
                self.MQ = "MQ"
                match = re.findall(MQstring, sentence)
                self.MQkey += ', '.join(match)  + '; '
                self.MQkeyNum += len(re.findall(MQstring, sentence))
                noMQ = False

            # Checking flags
            if check_NR(sentence):
                self.NR = "NR"



            if sentenceNumber == 0:
                sentence21 = sentence
                locFlag='Title'
            elif sentenceNumber <= 3:

                if sentenceNumber == 1:
                    locFlag = '1stThree'
                    sentence21 = sentence
                else:
                    sentence21 += sentence
            else:
                if sentenceNumber == 4:
                    locFlag='lastSents'
                    sentence21 = sentence
                else:
                    sentence21 += sentence

            if queryID == '2.1':

                if sentenceNumber in (0, 3, len(sentenceList) - 1):
                    if not stopINVIVO and re.search(r"\b(" + bodypartsList + r")\b", sentence21) and\
                            '<EIVkey>' in sentence21:

                        keyFlag.update({'BodypartEIV' + locFlag:
                                    re.search(r"\b" + bodypartsList + r"\b", sentence21).group(0) + " " +
                                    sentence21.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0]
                                })
                        EIVkeysSet.add(re.search(r"\b" + bodypartsList + r"\b", sentence21).group(0) + ' (BP) [in ' + locFlag + ']')
                        EIVkeysSet.add(sentence21.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0] + " [in " + locFlag + ']')

                    if not stopINVIVO and re.search('isolate[sd]?', sentence21) and \
                                        re.search('(microb(e|(ial)|(es))|bacteria[l]?)', sentence21):
                        keyFlag.update({'BactIsolate' + locFlag:
                                            re.search('isolate[sd]?', sentence21).group(0) + " " +
                                            re.search('(microb(e|(ial)|(es))|bacteria[l]?)', sentence21).group(0)
                                        })
                        EITkeysSet.add(re.search('isolate[sd]?', sentence21).group(0) + " " +\
                                            re.search('(microb(e|(ial)|(es))|bacteria[l]?)', sentence21).group(0) +  " [in " + locFlag + ']')

                    if not stopINVIVO and '<EITkey>' in sentence21 and '<EIVkey>' in sentence21:
                        keyFlag.update({'EIV+EIT' + locFlag:
                                            sentence21.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0] + " " +
                                            sentence21.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0]
                                        })
                        EITkeysSet.add(sentence21.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0] + " [in " + locFlag + ']')
                        EIVkeysSet.add(sentence21.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0] + " [in " + locFlag + ']')

                    if not stopINVIVO and '<EITkey>' in sentence21:
                        keyFlag.update({'EIT' + locFlag: sentence21.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0]})

                        EITkeysSet.add(sentence21.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0] + " [in " + locFlag + ']')

                        if re.search('isolate[sd]?', sentence):
                            keyFlag.update({'EITisolate' + locFlag:
                                            sentence21.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0] + " " +
                                            re.search('isolate[sd]?', sentence21).group(0)
                                            })
                            EITkeysSet.add(sentence21.split('<EITkey>', 1)[1].split('</EITkey>', 1)[0] + " " +\
                                            re.search('isolate[sd]?', sentence21).group(0) + " [in" + locFlag + ']')


                    if not stopINVIVO and '<EIVkey>' in sentence21:
                        keyFlag.update({'EIV' + locFlag: sentence21.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0]})

                        EIVkeysSet.add(sentence21.split('<EIVkey>', 1)[1].split('</EIVkey>', 1)[0] + " [in " + locFlag + ']')

            elif queryID == '3.1':
                subst_in_sentence = re.findall(r'\b' + "|".join(substance) + r'\b', sentence)
                if locFlag == "Title" and len(subst_in_sentence) > 0:
                    sub_title = ', '.join(set(subst_in_sentence))

                    if re.findall(ETX_A, sentence):
                        self.codekey5 += '{[' + sub_title + " - in Title" + " + " + ", ".join(re.findall(ETX_A,
                                                                                        sentence)) + " (A) - in Title]}; "
                        self.code5 = "ETX"

                    if re.findall(SUS_A, sentence):
                        self.codekey5 += '{[' + sub_title + " - in Title" + " + " + ", ".join(re.findall(SUS_A,
                                                                                      sentence)) + " (A) - in Title]}; "
                        if self.code5 == "ETX":
                            self.code5="SUS/ETX"
                        else:
                            self.code5="SUS"


                if len(subst_in_sentence) > 0 and re.findall(ETX_A, sentence):
                    self.codekey2 += '[' + ', '.join(set(subst_in_sentence)) + " + " +\
                                 ', '.join(re.findall(ETX_A, sentence)) + " (A)]; "
                    self.code2="ETX"

                if len(subst_in_sentence) and re.findall(SUS_A, sentence):
                    self.codekey2 += '[' + '; '.join(set(subst_in_sentence)) + " + " +\
                                 ', '.join(re.findall(SUS_A, sentence)) + " (A)]; "
                    if self.code2 == "ETX":
                        self.code2 = "SUS/ETX"
                    else:
                        self.code2 = "SUS"


                if re.findall(ETX_A, sentence) and re.findall(ETX_B, sentence) and len(subst_in_sentence) > 0:
                    self.codekey3 += flag_key_word(', '.join(set(subst_in_sentence)) + " +", ETX_A, ETX_B)
                    self.code3 = "ETX"
                elif re.findall(SUS_A, sentence) and re.findall(SUS_B, sentence) and len(subst_in_sentence) > 0:
                    self.codekey3 += flag_key_word(', '.join(set(subst_in_sentence))+ " +", SUS_A, SUS_B)
                    if self.code3 == "ETX":
                        self.code3 = "SUS/ETX"
                    else:
                        self.code3 = "SUS"

                if locFlag != "Title" and sub_title != str() and self.code5 == "ENV":
                    if re.findall(ETX_A, sentence) and re.findall(ETX_B, sentence):

                        self.codekey5 += '[' + sub_title + " + " + ", ".join([(x[0] if
                        isinstance(x, tuple) else x) for x in re.findall(ETX_A, sentence)]) + ", (A), " + ', '.join([(x[0] if
                        isinstance(x, tuple) else x) for x in re.findall(ETX_B, sentence)]) + " (B) - in sentence " +\
                                         str(sentenceNumber) + ']; '
                        if self.code5 not in ("ETX", "SUS/ETX"):
                            if self.code5 == "SUS":
                                self.code5 = "SUS/ETX"
                            else:
                                self.code5="ETX"

                if locFlag != "Title" and sub_title != str() and self.code5 in ("ENV", "ETX"):
                    if re.findall(SUS_A, sentence) and re.findall(SUS_B, sentence):

                        self.codekey5+='[' + sub_title + " + "  + ", ".join([(x[0] if
                        isinstance(x, tuple) else x) for x in re.findall(SUS_A, sentence)]) + " (A), " + ', '.join([(x[0] if
                        isinstance(x, tuple) else x) for x in re.findall(SUS_B, sentence)]) + " (B) - in sentence " + \
                                       str(sentenceNumber) + ']; '
                        if self.code5 not in ("SUS", "SUS/ETX"):
                            if self.code5 == "ETX":
                                self.code5="SUS/ETX"
                            else:
                                self.code5="SUS"

            elif queryID == '4.1':

                if re.search(r'emission|emitted', sentence)\
                        and re.search(r'light|optical|heat|energy|exciton|spectroscopy', sentence):
                    sentence = re.sub(r'emission|emitted', '', sentence)

                if re.findall(INC_A, sentence) and re.findall(INC_B, sentence):
                    self.INCkey += flag_key_word(INC_A, INC_B)
                    self.INC = "INC"

                if re.findall(NAT_dir, sentence):
                    self.NAT = "NAT"
                    self.NATkey += flag_key_word(NAT_A, NAT_B)

                if re.findall(ENG_A, sentence) and re.findall(ENG_B, sentence):
                    self.ENG = "ENG"
                    self.ENGkey += flag_key_word(ENG_A, ENG_B)

                if re.findall(SIZ_A, sentence):
                    self.SIZkey += "[" + ', '.join(re.findall(SIZ_A, sentence)) + "] "
                    self.SIZ="SIZ"

                if re.findall(SIZ_B, sentence):
                    siz_result = re.search(SIZ_B, sentence)

                    if float(siz_result.group(1)) < 500 and siz_result.group(6) == 'nm' or\
                        float(siz_result.group(1)) < 0.5 and siz_result.group(6) == 'μm':
                        self.SIZkey += "[" + ', '.join(x[0] for x in re.findall(SIZ_B, sentence)) + '(B)' + "] "
                        self.SIZ = "SIZ"

            sentenceNumber += 1

        if queryID == '2.1':
            self.EIVkey = '; '.join(EIVkeysSet)
            self.EITkey = '; '.join(EITkeysSet)
            # Assigning code according to the algorithm
            if "BodypartEIVTitle" in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["BodypartEIVTitle"],
                        )
                self.codeWeight=10
                self.EIV='EIV'
                self.codeReason = "EIV in title and body part in title"
            # 1a
            elif "EITisolateTitle" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EITisolateTitle"],
                        )
                self.codeWeight = 9
                self.EIT = 'EIT'
                self.codeReason="EIT isolate in Title"
            # 1b
            elif "BactIsolateTitle" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["BactIsolateTitle"],
                        )
                self.codeWeight = 9
                self.EIT ='EIT'
                self.codeReason="bacterial isolate in Title"
            # 1c
            elif 'EIVTitle' in keyFlag.keys() and 'EIV+EITTitle' not in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EIVTitle"],
                        )
                self.codeWeight = 10
                self.EIV ='EIV'
                self.codeReason="EIV in Title"
            # 1d
            elif 'EITTitle' in keyFlag.keys() and 'EIV+EITTitle' not in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EITTitle"],
                        )
                self.codeWeight = 9
                self.EIT ='EIT'
                self.codeReason="EIT in Title"
            # 3
            elif 'EIV+EITTitle' in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Title', keyword_scanned=keyFlag["EIV+EITTitle"],
                        )
                self.codeWeight = 9
                self.EIT ='EIT'
                self.codeReason="EIV and EIT in Title"

            elif "BodypartEIV1stThree" in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["BodypartEIV1stThree"],
                        )
                self.codeWeight=10
                self.EIV='EIV'
                self.codeReason="EIV and body part in 1st 3 sentences"


            # 2a
            elif "EITisolate1stThree" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EITisolate1stThree"],
                        )
                self.codeWeight=9
                self.EIT = 'EIT'
                self.codeReason="EIT isolate in 1st 3 sentences"
            # 2a
            elif "BactIsolate1stThree" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["BactIsolate1stThree"],
                        )
                self.codeWeight=9
                self.EIT = 'EIT'
                self.codeReason="Bacterial isolate in 1st 3 sentences"
            # 2b
            elif 'EIV1stThree' in keyFlag.keys() and 'EIV+EIT1stThree' not in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EIV1stThree"],
                        )
                self.codeWeight=10
                self.EIV = 'EIV'
                self.codeReason="EIV in 1st 3 sentences"
            # 2c
            elif 'EIT1stThree' in keyFlag.keys() and 'EIV+EIT1stThree' not in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EIT1stThree"],
                        )
                self.codeWeight = 9
                self.EIT = 'EIT'
                self.codeReason="EIT in 1st 3 sentences"
            # 4
            elif 'EIV+EIT1stThree' in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='1st three sentences', keyword_scanned=keyFlag["EIV+EIT1stThree"],
                        )
                self.codeWeight = 9
                self.EIT = 'EIT'
                self.codeReason="EIV + EIT in 1st 3 sentences"

            elif "BodypartEIVlastSents" in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["BodypartEIVlastSents"],
                        )

                self.codeWeight = 10
                self.EIV = 'EIV'
                self.codeReason="EIV and body part in last sentences"

            # 5a
            elif "EITisolatelastSents" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EITisolatelastSents"],
                        )
                self.codeWeight=9
                self.EIT ='EIT'
                self.codeReason="EIT isolate in last sentences"
            # 5a
            elif "BactIsolatelastSents" in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["BactIsolatelastSents"],
                        )
                self.codeWeight=9
                self.EIT ='EIT'
                self.codeReason="Bacterial isolate in last sentences"
            # 5b
            elif 'EIVlastSents' in keyFlag.keys() and 'EIV+EITlastSents' not in keyFlag.keys():
                logline(number=number, assigned_code='EIV', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EIVlastSents"],
                        )
                self.codeWeight=10
                self.EIV ='EIV'
                self.codeReason="EIV in last sentences"
            # 5c
            elif 'EITlastSents' in keyFlag.keys() and 'EIV+EITlastSents' not in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EITlastSents"],
                        )
                self.codeWeight=9
                self.EIT ='EIT'
                self.codeReason="EIT in last sentences"

            # 5d
            elif 'EIV+EITlastSents' in keyFlag.keys():
                logline(number=number, assigned_code='EIT', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                        location='Last Sentences', keyword_scanned=keyFlag["EIV+EITlastSents"],
                        )
                self.codeWeight=9
                self.EIT ='EIT'
                self.codeReason="EIV + EIT in last sentences"

            elif not stopINVIVO:
                self.codeWeight = 7
                self.TOX = 'TOX'
                logline(number=number, assigned_code='TOX', link=self.link,
                        title=self.articleTitle, abstr=self.articleAbstract,
                            )
                self.codeReason="No keywords found"

        elif queryID == '4.1':
            taglist = list()

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
            self.codeWeight = 7

        if self.LVL and queryID != '2.1': self.weight += 1
        if self.CTX: self.weight += 0
        if self.REV: self.weight += 1 if queryID == '4.1' else 2

        if queryID == '3.1':

            '''if "ETX" in [self.code1, self.code2 or self.code3 or self.code4 or self.code5]:
                self.code = 'ETX'
                self.codeWeight = 10

            elif "SUS" in [self.code1, self.code2 or self.code3 or self.code4 or self.code5]:
                self.code='SUS'
                self.codeWeight = 9

            else:
                self.code='ENV'
                self.codeWeight = 7'''

            if not self.code1: self.code1 = "ENV"
            if not self.code2: self.code2 = "ENV"
            if not self.code3: self.code3 = "ENV"
            if not self.code4: self.code4 = "ENV"
            if not self.code5: self.code5 = "ENV"
            self.codeWeight = 0


        elif queryID == '4.1':

            if self.INC: self.weight += 2
            if self.NAT: self.weight += 2
            if self.SIZ: self.weight += 3


        if not self.NR:
            self.SecondaryWeight = self.PrimaryWeight = self.codeWeight + self.weight
        #     if self.SecondaryWeight < 0:
        #         self.SecondaryWeight = self.PrimaryWeight = 0

        if self.NR:
            self.SecondaryWeight = self.codeWeight + self.weight
            self.PrimaryWeight = 0




        if noMQ:
            self.NR = 'NR'
            self.SecondaryWeight = self.PrimaryWeight = 0

        if self.TR or self.ENG:
            self.SecondaryWeight = self.PrimaryWeight = 0

    def __str__(self):
        return self.details


if __name__ == '__main__':
    print(regex_str)