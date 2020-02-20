from optparse import OptionParser
import random
import os.path
from os import listdir
from os.path import isfile, join
import pickle
import sys
from HTMLTableParser import  HTMLTableParser
import re
import jieba
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag.stanford import StanfordPOSTagger

usage = "parseAbbreviation.py --output outputpath"

parser = OptionParser(usage=usage)

parser.add_option("--topic", type="string", help="topic", default="tiyu", dest="topic")

parser.add_option("--inputpath", type="string", help="inputpath", default="abbr", dest="inputpath")
parser.add_option("--outputpath", type="string", help="outputpath", default="abbr", dest="outputpath")
parser.add_option("--stanfordpath", type="string", help="stanfordpath", default="/Users/Leo/stanford/", dest="stanfordpath")
parser.add_option("--os", type="string", help="os", default="osx", dest="os")

(options, args) = parser.parse_args()

stanfordpath = options.stanfordpath

if options.os == 'statnlp0':
    stanfordpath = '/home/lihao/'





os.makedirs(options.outputpath, exist_ok=True)

abbreviation = []
abbreviationDict = {}


def writeInstance(instances, path, filename, encoding='utf-8'):
    filename = os.path.join(path, filename)
    with open(filename, 'w', encoding=encoding) as f:
        for inst in instances:
            f.write(inst)
            f.write('\n')
        f.close()

    print('|\t', filename + '    ', '\t|\t', len(instances), '\t|')




for topic in options.topic.split(','):
    filename = topic + '.txt'
    inputfilename = os.path.join(options.inputpath, filename)

    count = 0
    f = open(inputfilename, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        fields = line.split('|||')
        fullname = fields[0]
        fields.append(fields[len(fields) - 1])
        fields[len(fields) - 2] = topic

        if not fullname in abbreviationDict:
            abbreviation.append(line)
            abbreviationDict[fullname] = 0
            count += 1
        else:
            abbreviationDict[fullname] += 1


    f.close()

    print('Count:', count)


random.seed(1997)
size = len(abbreviation)
random.shuffle(abbreviation)

filename = 'abbr.txt'

writeInstance(options.outputpath, filename)

## Train:   7/10    Test  2/10   Dev 1/10

lb = 0
rb = size * 7 // 10
trainInstances = abbreviation[lb:rb]


lb = rb
rb = size * 9 // 10
testInstances = abbreviation[lb:rb]


lb = rb
rb = size
devInstances = abbreviation[lb:rb]

writeInstance(trainInstances, options.outputpath, filename.replace('txt', 'train.txt'))
writeInstance(testInstances, options.outputpath, filename.replace('txt', 'test.txt'))
writeInstance(devInstances, options.outputpath, filename.replace('txt', 'dev.txt'))


