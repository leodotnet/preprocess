from optparse import OptionParser
import random
import os.path
from os import listdir
from os.path import isfile, join
import pickle
import sys
import re
import numpy as np

usage = "lda2emb.py --output outputpath"

parser = OptionParser(usage=usage)

parser.add_option("--inputpath", type="string", help="inputpath", default="wsj", dest="inputpath")
parser.add_option("--outputpath", type="string", help="outputpath", default="wsj", dest="outputpath")

(options, args) = parser.parse_args()

os.makedirs(options.outputpath, exist_ok=True)

LDA={}


#read model-final.others
f = open('model-final.others', 'r', encoding='utf-8')
for line in f:
    line = line.strip()
    if line == '':
        continue

    fields = line.split('=')
    if line.startswith('ntopics'):
        LDA['ntopics'] = int(fields[1])
    elif line.startswith('nwords'):
        LDA['nwords'] = int(fields[1])

f.close()

embList = [np.zeros(LDA['ntopics']) for i in range(0, LDA['nwords'])]

#read model-final.phi
topicIdx = 0
f = open('model-final.phi', 'r', encoding='utf-8')
for line in f:
    line = line.strip()
    if line == '':
        continue

    v = np.fromstring(line, dtype=np.float, sep=' ')
    for i in range(0, LDA['nwords']):
        embList[i][topicIdx] = v[i]

    topicIdx += 1
f.close()


word2Idx = {}
idx2word = {}
#read wordmap.txt
f = open('wordmap.txt', 'r', encoding='utf-8')
first = True
for line in f:
    if first == False:
        line = line.strip()
        fields = line.split(' ')
        word = fields[0]
        wordIdx = int(fields[1])
        word2Idx[word] = wordIdx
        idx2word[wordIdx] = word
    else:
        first = False
f.close()

word2emb = {}
for i in range(0, len(embList)):
    word2emb[idx2word[i]] = embList[i]


#save embList
f = open('ldaemb.txt', 'w', encoding='utf-8')
f.write(str(LDA['nwords']) + ' ' + str(LDA['ntopics']) + '\n')
for i in range(0, LDA['nwords']):
    line = idx2word[i] + ' ' + ' '.join([str(item) for item in embList[i].tolist()])
    f.write(line + '\n')
f.close()




