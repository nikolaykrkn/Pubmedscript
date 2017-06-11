from urllib.request import urlopen
from bs4 import BeautifulSoup
import codecs

file = codecs.open('plants_common.txt', 'w', encoding='utf-8')

link = 'https://en.wikipedia.org/w/index.php?title=List_of_plants_by_common_name&printable=yes'
with urlopen(link) as webPage:
    soup = BeautifulSoup(webPage.read().decode('utf-8'), 'html.parser')
    for element in soup.select('li'):
        file.write(element.text.split('–')[0] + '\n' if len(element.text.split('–')[0]) > 1 else '')
file.close()