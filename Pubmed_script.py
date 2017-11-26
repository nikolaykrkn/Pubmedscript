# This script scans an XML-results file exported from pubmed.com
# The output is a xls file
# The script folder must contain:
#
# pubmed_result.xls from http://www.ncbi.nlm.nih.gov/pubmed/;
# J_Medline.txt from ftp://ftp.ncbi.nih.gov/pubmed/J_Medline.txt;
# In_vivo_toxicity_models.csv;
# scimagojr.xls from http://www.scimagojr.com/journalrank.php;
# Codeautomation.py module file
# phantomJS.exe.exe in ./selenium/webdriver/ folder

import re
from selenium import webdriver
from datetime import date
import codecs
import xlwt
# import Codeautomation
import xml.etree.ElementTree as ET
from nltk import tokenize

from Pubmed_Article_Object import JournalArticle

queryID = input('Enter metaquery number: ')
#queryID = '2.1'
if queryID == '3.1':
    substance_comma = input('Enter substance names separated by comma, no quoting: ')
    Substance = [x.strip().lower() for x in substance_comma.split(',')]
else:
    Substance = None
# MaxResult = 0
# if queryID == '2.1':
#     MaxResult = 600
# elif queryID == '3.1':
#     MaxResult = 300
# elif queryID == '4.1':
#     MaxResult = 100
# else:
#     print('Incorrect metaquery ')
#     input()
#     quit()
#
# overRes = input('How many extra results do you want to check? ')
#
# if overRes != '':
#     MaxResult += int(overRes)

# driver = webdriver.PhantomJS(executable_path='./selenium/webdriver/phantomJS.exe')
# driver.implicitly_wait(2)

yearAccess = date.today().year
dayAccess = date.today().day
monthAccess = date.today().month

resultsToLog = xlwt.Workbook(encoding='UTF-8')
query = resultsToLog.add_sheet('metaquery results')

xml_file_name = input('Enter PubMed xml export file name\n(file must be in the same folder as the executable): ')
#xml_file_name = 'BPA_21.xml'
tree = ET.parse(xml_file_name)
root = tree.getroot()

results = 0

for article_xml in root.findall('PubmedArticle'):
    #if results >= 1088:

        art = JournalArticle(article_xml, queryID, Substance, results, xml_file_name)

        forXLS = [str(results + 1), art.reference, art.lastName, art.year, art.JournalTitle, art.link,
                  str(monthAccess) + "/" + str(dayAccess) + "/" + str(yearAccess),
                  art.issn, art.IF, art.crossrefCited, art.code if queryID != '3.1' else None,
                  art.codeReason if queryID == '2.1' else None, art.HC, art.IFcode, art.TR,
                  #art.HR,
                  art.EIV if queryID == '2.1' else None, art.EIVkey.replace("<EIVkey>", "") if queryID == '2.1' else None,
                  art.EIT if queryID == '2.1' else None, art.EITkey if queryID == '2.1' else None,
                  art.TOX if queryID == '2.1' else None,


                  art.code1 if queryID == '3.1' else None, art.codekey1 if queryID == '3.1' else None,
                  art.code2 if queryID == '3.1' else None, art.codekey2 if queryID == '3.1' else None,
                  art.code3 if queryID == '3.1' else None, art.codekey3 if queryID == '3.1' else None,
                  art.code4 if queryID == '3.1' else None, art.codekey4 if queryID == '3.1' else None,
                  art.code5 if queryID == '3.1' else None, art.codekey5 if queryID == '3.1' else None,

                  art.HUM if queryID not in ('3.1', '4.1') else None,
                  art.HUMkeys if queryID not in ('3.1', '4.1') else None,
                  art.LVL, art.LVLkeys, art.REV, art.CTX, art.CTXkeys, art.NO,
                  # art.LR,art.EXP,art.ERM,
                  art.SIZ if queryID == '4.1' else None, art.SIZkey if queryID == '4.1' else None,
                  art.INC if queryID == '4.1' else None, art.INCkey if queryID == '4.1' else None,
                  art.NAT if queryID == '4.1' else None, art.NATkey if queryID == '4.1' else None,
                  art.ENG if queryID == '4.1' else None, art.ENGkey if queryID == '4.1' else None,
                  #art.EMIS if queryID in ['3.1', '4.1'] else None,
                  art.NR, art.MQkey, art.MQkeyNum,
                  art.SecondaryWeight if queryID != '3.1' else None, art.PrimaryWeight if queryID != '3.1' else None]

        forXLS = [x for x in forXLS if x is not None]
        # filling xls spreadsheet
        print(results)
        n = 0
        for data in forXLS:
            query.write(results, n, data)
            n += 1

        resultsToLog.save(
                "output/result_pubmed" + str(monthAccess) + str(dayAccess) + queryID.replace('.','_') + ".xls")

        results += 1


