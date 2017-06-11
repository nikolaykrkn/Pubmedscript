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
#
# (c) Nikolay Kuriakin

import re
from selenium import webdriver
from datetime import date
import codecs
import xlwt
# import Codeautomation
import xml.etree.ElementTree as ET
from nltk import tokenize

from Pubmed_Article_Object import JournalArticle

# queryID = input('Enter metaquery number: ')
queryID = '2.1'
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

xml_file_name = 'AL2O3_21.xml'
tree = ET.parse(xml_file_name)
root = tree.getroot()

results = 0

for article_xml in root.findall('PubmedArticle'):
    if results >= 572:

        art = JournalArticle(article_xml, queryID, results, xml_file_name)

        forXLS = [str(results + 1), art.reference, art.lastName, art.year, art.JournalTitle, art.link,
                  str(monthAccess) + "/" + str(dayAccess) + "/" + str(yearAccess),
                  art.issn, art.IF, art.crossrefCited, art.code, art.HC, art.IFcode,
                  art.TR,
                  #art.HR,
                  art.HUM if queryID != '3.1' else None,
                  art.LVL, art.REV, art.CTX,  art.NO,
                  # art.LR,art.EXP,art.ERM,
                  art.SIZ if queryID == '4.1' else None,
                  art.INC if queryID == '4.1' else None,
                  art.NAT if queryID == '4.1' else None,
                  art.ENG if queryID == '4.1' else None,
                  art.EMIS if queryID in ['3.1', '4.1'] else None,
                  art.NR,
                  art.SecondaryWeight, art.PrimaryWeight]
        forXLS = [x for x in forXLS if x is not None]
        # filling xls spreadsheet
        print(results)
        n = 0
        for data in forXLS:
            query.write(results, n, data)
            n += 1


        resultsToLog.save(
            "output/result_pubmed" + str(monthAccess) + str(dayAccess) + queryID.replace('.','_') + ".xls")

    results+=1
            # if results == 500:
            #     break


