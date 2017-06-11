import codecs
import os

def logline(number='', assigned_code='', link='', title='', abstr='', location='', keyword_scanned='', flags=''):

    logfilename='log_keywords_codeautomation_0.txt'
    log = codecs.open(logfilename, 'a', encoding='utf-8')

    #print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(number, assigned_code, link, title, abstr,
                     # location, keyword_scanned, flags))

    if os.stat(logfilename).st_size == 0:
        log.write(
            'Article number\tAssigned code\tLink\tTitle\tAbstract\tLocation of the keyword\tKeyword\tFlags\n')

    return log.write(
                        str(number) + '\t' +
                        assigned_code + '\t'+
                        link + '\t'+
                        title + '\t'+
                        abstr + '\t'+
                        location + '\t'+
                        keyword_scanned + '\t'+
                        flags + '\n'
                     )
