from optparse import OptionParser
import random
import os.path
from os import listdir
from os.path import isfile, join
import pickle
import sys
from HTMLTableParser import  HTMLTableParser
import re


usage = "parseAbbreviation.py --output outputpath"

parser = OptionParser(usage=usage)

parser.add_option("--topic", type="string", help="topic", default="tiyu", dest="topic")

parser.add_option("--inputpath", type="string", help="inputpath", default="raw", dest="inputpath")
parser.add_option("--outputpath", type="string", help="outputpath", default="pre", dest="outputpath")

(options, args) = parser.parse_args()



# content = '中华民国（1912——1949），位于亚洲东部、东临太平洋。是辛亥革命以后建立的亚洲第一个民主共和国，简称民国。[1]  为第二次世界大战的主要战胜国及联合国五个主要创始会员国之一。'
# pattern = re.compile(
#             u"简称(.*?)[，。]",
#             re.S
#         )
# findings = re.findall(pattern, content)
# print(findings)
# print()
# for finding in findings:
#     print(finding)
#
# exit()

os.makedirs(options.outputpath, exist_ok=True)
for topic in options.topic.split(','):
    inputfilename = topic + '.html'
    outputfilename = os.path.join(options.outputpath, inputfilename.replace('html', 'txt'))
    #file:///Users/Leo/workspace/abbreviation/raw/tiyu.html
    url = 'file:///Users/Leo/workspace/abbreviation/' + options.inputpath + '/' + inputfilename

    print('url:',options.inputpath + '/' + inputfilename)

    hp = HTMLTableParser()
    table = hp.parse_file(options.inputpath + '/' + inputfilename)[0]

    abbreviation = []
    i = 0
    for index, row in table.iterrows():
        entry = list(row)
        name = entry[1]
        content = entry[2]


        pattern = re.compile(
            u"简称(.*?)[”）)，。\[]",
            re.S
        )
        findings = re.findall(pattern, content)

        if len(findings) > 0:
            item = (name.strip(), findings[0].strip(), content)
            abbreviation.append(item)



        i += 1


    f = open(outputfilename, 'w', encoding='utf-8')
    for name, abbr, content in abbreviation:
        #print(name, abbr, repr(content))
        f.write(name + '\t' + abbr + '\t' + repr(content) + '\n')
    f.close()


