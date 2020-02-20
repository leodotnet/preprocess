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


def parseAbbr(abbr):
    newabbr = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-]+", "", abbr)

    if newabbr.startswith('为'):
        newabbr = newabbr[1:]

    if '或' in newabbr:
        newabbr = ','.join(newabbr.split('或'))


    return newabbr


def isValidAbbr(name, abbr):

    if name == abbr:
        return False

    markName = [0 for i in range(0, len(name))]

    for i in len(abbr):
        chAbbr = abbr[i]

        found = False
        for j in len(name):
            chName = name[j]

            if chAbbr == chName and markName[j] == 0:
                markName[j] = 1
                found = True
                break

        if found == False:
            return False

    return True


os.makedirs(options.outputpath, exist_ok=True)
for topic in options.topic.split(','):
    filename = topic + '.txt'
    inputfilename = os.path.join(options.inputpath, filename)
    outputfilename = os.path.join(options.outputpath, filename)

    abbreviation = []
    abbreviationDict = {}

    f = open(inputfilename, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        name, abbr, content = line.split('\t')
        if abbr.strip() == '':
            continue
        abbr = parseAbbr(abbr)
        if not name in abbreviationDict:
            abbreviationDict[name] = (abbr, content)
            abbreviation.append((name, abbr, content))

    f.close()



    f = open(outputfilename, 'w', encoding='utf-8')
    for name, abbr, content in abbreviation:
        #print(name, abbr, content)
        if isValidAbbr(name, abbr):
            f.write(name + '\t' + abbr + '\t' + content + '\n')
    f.close()


