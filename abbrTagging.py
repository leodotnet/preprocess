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

parser.add_option("--inputpath", type="string", help="inputpath", default="data", dest="inputpath")
parser.add_option("--outputpath", type="string", help="outputpath", default="abbr", dest="outputpath")
parser.add_option("--stanfordpath", type="string", help="stanfordpath", default="/Users/Leo/stanford/", dest="stanfordpath")
parser.add_option("--os", type="string", help="os", default="osx", dest="os")

(options, args) = parser.parse_args()

stanfordpath = options.stanfordpath

if options.os == 'statnlp0':
    stanfordpath = '/home/lihao/'



def pos_tag(words, lang = 'cn', tool = 'stanford'):
    if tool == 'stanford':
        tmp =  pos_tag_stanford(words, lang)
        return list(map(lambda x: tuple(x[1].split('#')), tmp))

    elif tool == 'nltk':
        return pos_tag_nltk(words, lang)
    else:
        return None


def pos_tag_nltk(sentence, lang):
    return None

def pos_tag_stanford(tokens, lang):

    path_to_model = stanfordpath + 'stanford-postagger/models/chinese-distsim.tagger'
    path_to_jar = stanfordpath + '/stanford-postagger/stanford-postagger.jar'
    tagger = StanfordPOSTagger(path_to_model, path_to_jar)
    tagger.java_options = '-mx4096m'  ### Setting higher memory limit for long sentences
    #print('sent:', tokens)
    #seg = list(jieba.cut(sentence, cut_all=False))
    ret = tagger.tag(tokens)
    return ret


def KSTagging(name, abbr):
    markName = [0 for i in range(0, len(name))]

    for i in range(0, len(abbr)):
        chAbbr = abbr[i]

        found = False
        for j in range(0, len(name)):
            chName = name[j]

            if chAbbr == chName and markName[j] == 0:
                markName[j] = 1
                found = True
                break

        if found == False:
            return None

    tag = ['K' if flag == 1 else 'S' for flag in markName]

    return tag

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

    count = 0
    f = open(inputfilename, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        name, abbr, content = line.split('\t')



        KStag = KSTagging(name, abbr)

        if KStag != None:
            segmentation = list(jieba.cut(name, cut_all = False))

            retPOSTags = pos_tag(segmentation)
            #print(retPOSTags)
            tokens, postags = zip(*retPOSTags)

            abbreviation.append((name, abbr, segmentation, postags, KStag))

            line = name + ' ||| ' + abbr + ' ||| ' + ' '.join(segmentation) + ' ||| ' + ' '.join(postags) + ' ||| ' + ' '.join(KStag)
            print(line)
            count += 1



    f.close()

    print('Count:', count)

    f = open(outputfilename, 'w', encoding='utf-8')
    for name, abbr, segmentation, postags, KStag in abbreviation:
        line = name + ' ||| ' + abbr + ' ||| ' + ' '.join(segmentation) + ' ||| ' + ' '.join(postags) + ' ||| ' + ' '.join(KStag)
        f.write(line + '\n')
    f.close()
